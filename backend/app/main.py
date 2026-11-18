import json
from pathlib import Path
import os
from datetime import datetime, timedelta, timezone
import random
import secrets
import base64

from fastapi import Request
from fastapi.responses import Response

from fastapi.params import Header
from dotenv import load_dotenv

from contextlib import asynccontextmanager

import asyncio
import threading
from time import perf_counter

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.core import db
from app.core.config import (AMBULANCE_SEED, HOSPITALS_SEED, LAT_MAX, LAT_MIN,
                             LON_MAX, LON_MIN, ROOT)
from app.core.enums import AccidentStatus, AmbulanceStatus
from app.core.schemas import Accident, AccidentReport, Ambulance
from app.core.seeds import load_ambulances
from app.services.dispatch import STRATEGIES, dispatch_pending
from app.services import progress
from app.services.notify import notify_nearest
from app.services.routing import road_type_at
from app.services.traffic import best_route
from app.services.weather import get_weather as _get_weather
import time as _time
_WX = {}


def get_weather(lat, lon):
    """Weather barely changes in minutes: cache per ~1 km cell for 10 minutes."""
    key = (round(lat, 2), round(lon, 2))
    hit = _WX.get(key)
    if hit and _time.time() - hit[0] < 600:
        return hit[1]
    val = _get_weather(lat, lon)
    if val is not None:
        _WX[key] = (_time.time(), val)
    return val

load_dotenv()

AGENT_KEY = os.getenv("AGENT_API_KEY")

FRAMES_DIR = ROOT / "results" / "frames"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    db.seed_ambulances(load_ambulances(AMBULANCE_SEED))
    db.seed_hospitals(json.loads(HOSPITALS_SEED.read_text()))
    threading.Thread(target=_warm_up, daemon=True).start()
    task = asyncio.create_task(_batch_loop()) if BATCH_S > 0 else None
    prog = asyncio.create_task(_progress_loop()) if AUTO_PROGRESS else None
    yield
    for t in (task, prog):
        if t:
            t.cancel()


app = FastAPI(title="AI Emergency Response Network", lifespan=lifespan)
DASHBOARD_PIN = os.getenv("DASHBOARD_PIN")


@app.middleware("http")
async def require_login(request: Request, call_next):
    if not DASHBOARD_PIN or request.url.path == "/health":
        return await call_next(request)
    key = request.headers.get("x-api-key", "")
    if (request.method == "POST" and request.url.path == "/accidents" and AGENT_KEY
            and secrets.compare_digest(key.encode(), AGENT_KEY.encode())):
        return await call_next(request)               # camera agents
    auth = request.headers.get("authorization", "")
    if auth.startswith("Basic "):
        try:
            _, _, pw = base64.b64decode(auth[6:]).decode().partition(":")
            if secrets.compare_digest(pw.encode(), DASHBOARD_PIN.encode()):
                return await call_next(request)       # people using the dashboard
        except Exception:
            pass
    return Response("Login required", status_code=401,
                    headers={"WWW-Authenticate": 'Basic realm="Emergency Network"'})
app.mount("/frames", StaticFiles(directory=FRAMES_DIR), name="frames")
CLIPS_DIR = ROOT / "results" / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/clips", StaticFiles(directory=CLIPS_DIR), name="clips")

NEXT_STATUS = {
    AccidentStatus.AMBULANCE_ASSIGNED: AccidentStatus.EN_ROUTE,
    AccidentStatus.EN_ROUTE: AccidentStatus.ARRIVED,
    AccidentStatus.ARRIVED: AccidentStatus.RESOLVED,
}


class StatusChange(BaseModel):
    new_status: AccidentStatus


class NotificationStatus(BaseModel):
    status: str


DEDUPE_MINUTES = 10


def _recent_camera_incident(camera_id):
    """Unresolved incident from this camera in the last DEDUPE_MINUTES, or None."""
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=DEDUPE_MINUTES)
              ).strftime("%Y-%m-%dT%H:%M:%S")
    with db.connect() as conn:
        row = conn.execute(
            "SELECT accident_id FROM accidents WHERE camera_id = ? AND status != 'RESOLVED' "
            "AND substr(reported_at, 1, 19) >= ? ORDER BY reported_at DESC LIMIT 1",
            (camera_id, cutoff)).fetchone()
    return db.get_accident(row["accident_id"]) if row else None


@app.post("/demo/reset")
def demo_reset():
    """Demo control: clear all incidents and notifications, free every ambulance."""
    with db.connect() as conn:
        conn.execute("DELETE FROM notifications")
        conn.execute("DELETE FROM accidents")
        conn.execute("UPDATE ambulances SET status = ?", (AmbulanceStatus.AVAILABLE.value,))
        conn.commit()
    return {"status": "reset"}


_dispatch_lock = threading.Lock()     # one notify/dispatch at a time, so no double assignment
BATCH_S = float(os.getenv("DISPATCH_BATCH_S", "0"))   # 0 = dispatch right after each incident


def _warm_up():
    """Load the road graph and the per-ambulance travel-time caches before the first click."""
    try:
        from app.services.assignment import times_from
        from app.services.routing import snap_to_node
        t = perf_counter()
        road_type_at(22.72, 75.86)
        for a in db.list_ambulances():
            times_from(snap_to_node(a.location.lat, a.location.lon))
        print(f"warm-up done in {perf_counter() - t:.1f}s")
    except Exception as e:
        print("warm-up failed:", e)


def _notify_and_dispatch(accident):
    with _dispatch_lock:
        t = perf_counter()
        try:
            notify_nearest(accident)
        except Exception as e:
            print("notification failed:", e)
        t_notify = perf_counter() - t
        t = perf_counter()
        if BATCH_S <= 0:
            try:
                _run_dispatch("hungarian")
            except Exception as e:
                print("dispatch failed:", e)
        print(f"timing {accident.accident_id}: notify {t_notify:.2f}s, "
              f"dispatch {perf_counter() - t:.2f}s")


async def _batch_loop():
    def run():
        with _dispatch_lock:
            try:
                _run_dispatch("hungarian")
            except Exception as e:
                print("dispatch failed:", e)
    while True:
        await asyncio.sleep(BATCH_S)
        await asyncio.to_thread(run)


AUTO_PROGRESS = os.getenv("AUTO_PROGRESS", "1") != "0"   # 0 = only the manual advance buttons


def _run_dispatch(strategy="hungarian"):
    out = dispatch_pending(strategy)
    progress.record(out)              # keep each ETA so the journey can be timed from it
    return out


def _progress_once():
    with _dispatch_lock:
        for event in progress.tick():
            print("journey:", event)


async def _progress_loop():
    while True:
        await asyncio.sleep(5)
        try:
            await asyncio.to_thread(_progress_once)
        except Exception as e:
            print("progress failed:", e)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def home_page():
    return FileResponse(ROOT / "dashboard" / "home.html")


@app.get("/map", include_in_schema=False)
def map_page():
    return FileResponse(ROOT / "dashboard" / "index.html")


@app.get("/portal", include_in_schema=False)
def portal_page():
    return FileResponse(ROOT / "dashboard" / "portal.html")


@app.get("/ambulances", response_model=list[Ambulance])
def get_ambulances():
    return db.list_ambulances()


@app.get("/hospitals")
def get_hospitals():
    return db.list_hospitals()


@app.get("/accidents", response_model=list[Accident])
def get_accidents():
    return db.list_accidents()


@app.post("/accidents", response_model=Accident, status_code=201)
def report_accident(report: AccidentReport, background: BackgroundTasks,
                    x_api_key: str | None = Header(default=None)):
    if report.source == "camera" and AGENT_KEY and not secrets.compare_digest(
            x_api_key or "", AGENT_KEY):
        raise HTTPException(401, "invalid or missing API key")
    loc = report.location
    if not (LAT_MIN <= loc.lat <= LAT_MAX and LON_MIN <= loc.lon <= LON_MAX):
        raise HTTPException(422, "Location is outside the Indore map area")
    if report.source == "camera" and report.camera_id:
        existing = _recent_camera_incident(report.camera_id)
        if existing:                       # same camera, same ongoing incident: do not duplicate
            return existing
    if not report.frame_path and report.source != "camera":
        pool = sorted(FRAMES_DIR.glob("demo_pool_*.jpg"))      # simulated incident: borrow a recorded frame
        if pool:
            report = report.model_copy(update={
                "frame_path": str(random.choice(pool)),
                "description": ((report.description or "")
                                + " [demo: replayed frame from a recorded accident clip]").strip()})
    weather = get_weather(loc.lat, loc.lon)
    road = road_type_at(loc.lat, loc.lon)
    accident = db.add_accident(report, weather=weather, road_type=road)
    background.add_task(_notify_and_dispatch, accident)   # runs after the response is sent
    return accident


@app.get("/accidents/{accident_id}", response_model=Accident)
def get_accident(accident_id: str):
    accident = db.get_accident(accident_id)
    if accident is None:
        raise HTTPException(404, "Accident not found")
    return accident


@app.patch("/accidents/{accident_id}/status", response_model=Accident)
def change_accident_status(accident_id: str, change: StatusChange):
    try:
        return db.change_status(accident_id, change.new_status)
    except LookupError:
        raise HTTPException(404, "Accident not found")
    except db.IllegalTransition as e:
        raise HTTPException(409, str(e))


@app.post("/accidents/{accident_id}/advance", response_model=Accident)
def advance(accident_id: str):
    """Demo control: move an accident one step along its journey."""
    acc = db.get_accident(accident_id)
    if acc is None:
        raise HTTPException(404, "Accident not found")
    nxt = NEXT_STATUS.get(acc.status)
    if nxt is None:
        raise HTTPException(409, f"Cannot advance from {acc.status.value}")
    updated = db.change_status(accident_id, nxt)
    if acc.assigned_ambulance_id:
        if nxt == AccidentStatus.ARRIVED:
            db.set_ambulance_status(acc.assigned_ambulance_id, AmbulanceStatus.AT_SCENE)
        elif nxt == AccidentStatus.RESOLVED:
            db.set_ambulance_status(acc.assigned_ambulance_id, AmbulanceStatus.AVAILABLE)
    return updated


@app.get("/accidents/{accident_id}/media")
def accident_media(accident_id: str):
    """Frame and recording for one incident. Paths are relative to the API root."""
    acc = db.get_accident(accident_id)
    if acc is None:
        raise HTTPException(404, "Accident not found")
    frame = Path(acc.frame_path) if acc.frame_path else None
    clip = CLIPS_DIR / f"{frame.stem}.mp4" if frame else None
    return {
        "frame": f"frames/{frame.name}" if frame and (FRAMES_DIR / frame.name).exists() else None,
        "clip": f"clips/{clip.name}" if clip and clip.exists() else None,
    }


@app.get("/cameras")
def get_cameras():
    """Camera sites for the map. Stream URLs are never returned (they contain passwords)."""
    out = []
    for name, demo in (("cameras.local.json", False), ("demo_sites.json", True)):
        f = ROOT / name
        if f.exists():
            for c in json.loads(f.read_text()):
                out.append({"id": c["id"], "name": c.get("name", c["id"]),
                            "lat": c["lat"], "lon": c["lon"], "demo": demo})
    return out


@app.get("/assignments")
def get_assignments():
    """accident_id -> the hospital it was sent to (latest notification), with its location."""
    hospitals = {h["hospital_id"]: h for h in db.list_hospitals()}
    out = {}
    for n in db.list_notifications():
        h = hospitals.get(n["hospital_id"])
        if h is None:
            continue
        cur = out.get(n["accident_id"])
        if cur is None or n["created_at"] > cur["notified_at"]:
            out[n["accident_id"]] = {
                "hospital_id": h["hospital_id"], "hospital": h["name"],
                "lat": h["lat"], "lon": h["lon"],
                "scene_to_hospital_min": (n.get("payload") or {}).get("scene_to_hospital_min"),
                "notification_status": n["status"], "notified_at": n["created_at"],
            }
    return out


@app.get("/route")
def get_route(from_lat: float, from_lon: float, to_lat: float, to_lon: float):
    result = best_route(from_lat, from_lon, to_lat, to_lon)
    if result is None:
        raise HTTPException(404, "ROUTE UNAVAILABLE")
    return result


@app.post("/dispatch")
def dispatch(strategy: str = "hungarian"):
    if strategy not in STRATEGIES:
        raise HTTPException(400, f"strategy must be one of {list(STRATEGIES)}")
    with _dispatch_lock:
        return _run_dispatch(strategy)


@app.get("/notifications")
def get_notifications(hospital_id: str | None = None):
    return db.list_notifications(hospital_id)


@app.post("/notifications/{nid}/status")
def update_notification(nid: str, body: NotificationStatus):
    if body.status not in {"ACKNOWLEDGED", "ACCEPTED", "DECLINED"}:
        raise HTTPException(400, "status must be ACKNOWLEDGED, ACCEPTED or DECLINED")
    try:
        db.set_notification_status(nid, body.status)
    except LookupError:
        raise HTTPException(404, "Notification not found")
    return {"notification_id": nid, "status": body.status}