from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core import db
from app.core.config import AMBULANCE_SEED, LAT_MAX, LAT_MIN, LON_MAX, LON_MIN
from app.core.enums import AccidentStatus
from app.core.schemas import Accident, AccidentReport, Ambulance
from app.core.seeds import load_ambulances


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    db.seed_ambulances(load_ambulances(AMBULANCE_SEED))
    yield


app = FastAPI(title="AI Emergency Response Network", lifespan=lifespan)


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
    return db.add_accident(report)


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