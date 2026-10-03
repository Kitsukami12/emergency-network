from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core import db
from app.core.config import AMBULANCE_SEED, LAT_MAX, LAT_MIN, LON_MAX, LON_MIN
from app.core.enums import AccidentStatus
from app.core.schemas import Accident, AccidentReport, Ambulance
from app.core.seeds import load_ambulances
from app.services.astar import route_between
from fastapi.responses import FileResponse
from app.core.config import ROOT
from app.core.enums import AccidentStatus, AmbulanceStatus
from app.services.dispatch import STRATEGIES, dispatch_pending
from app.services.weather import get_weather
from app.services.routing import road_type_at


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    db.seed_ambulances(load_ambulances(AMBULANCE_SEED))
    yield


app = FastAPI(title="AI Emergency Response Network", lifespan=lifespan)
@app.get("/accidents", response_model=list[Accident])
def get_accidents():
    return db.list_accidents()


@app.get("/route")
def get_route(from_lat: float, from_lon: float, to_lat: float, to_lon: float):
    result = route_between(from_lat, from_lon, to_lat, to_lon)
    if result is None:
        raise HTTPException(404, "ROUTE UNAVAILABLE")
    return result

@app.get("/map", include_in_schema=False)
def map_page():
    return FileResponse(ROOT / "dashboard" / "index.html")

class StatusChange(BaseModel):
    new_status: AccidentStatus


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ambulances", response_model=list[Ambulance])
def get_ambulances():
    return db.list_ambulances()


@app.post("/accidents", response_model=Accident, status_code=201)
def report_accident(report: AccidentReport):
    loc = report.location
    if not (LAT_MIN <= loc.lat <= LAT_MAX and LON_MIN <= loc.lon <= LON_MAX):
        raise HTTPException(422, "Location is outside the Indore map area")
    weather = get_weather(loc.lat, loc.lon)
    road = road_type_at(loc.lat, loc.lon)
    return db.add_accident(report, weather=weather, road_type=road)


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


NEXT_STATUS = {
    AccidentStatus.AMBULANCE_ASSIGNED: AccidentStatus.EN_ROUTE,
    AccidentStatus.EN_ROUTE: AccidentStatus.ARRIVED,
    AccidentStatus.ARRIVED: AccidentStatus.RESOLVED,
}


@app.post("/dispatch")
def dispatch(strategy: str = "hungarian"):
    if strategy not in STRATEGIES:
        raise HTTPException(400, f"strategy must be one of {list(STRATEGIES)}")
    return dispatch_pending(strategy)


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