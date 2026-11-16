import json
import os
import secrets
import base64

from fastapi import Request
from fastapi.responses import Response

from fastapi.params import Header
from dotenv import load_dotenv

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
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
from app.services.notify import notify_nearest
from app.services.routing import road_type_at
from app.services.traffic import best_route
from app.services.weather import get_weather

load_dotenv()

AGENT_KEY = os.getenv("AGENT_API_KEY")

FRAMES_DIR = ROOT / "results" / "frames"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    db.seed_ambulances(load_ambulances(AMBULANCE_SEED))
    db.seed_hospitals(json.loads(HOSPITALS_SEED.read_text()))
    yield


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

NEXT_STATUS = {
    AccidentStatus.AMBULANCE_ASSIGNED: AccidentStatus.EN_ROUTE,
    AccidentStatus.EN_ROUTE: AccidentStatus.ARRIVED,
    AccidentStatus.ARRIVED: AccidentStatus.RESOLVED,
}


class StatusChange(BaseModel):
    new_status: AccidentStatus


class NotificationStatus(BaseModel):
    status: str


@app.get("/health")
def health():
    return {"status": "ok"}


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
def report_accident(report: AccidentReport, x_api_key: str | None = Header(default=None)):
    if report.source == "camera" and AGENT_KEY and not secrets.compare_digest(
            x_api_key or "", AGENT_KEY):
        raise HTTPException(401, "invalid or missing API key")
    loc = report.location
    if not (LAT_MIN <= loc.lat <= LAT_MAX and LON_MIN <= loc.lon <= LON_MAX):
        raise HTTPException(422, "Location is outside the Indore map area")
    weather = get_weather(loc.lat, loc.lon)
    road = road_type_at(loc.lat, loc.lon)
    accident = db.add_accident(report, weather=weather, road_type=road)
    try:
        notify_nearest(accident)        # a notification failure must never block the incident
    except Exception as e:
        print("notification failed:", e)
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
    return dispatch_pending(strategy)


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