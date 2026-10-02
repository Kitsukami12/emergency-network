from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.core import db
from app.core.config import AMBULANCE_SEED, LAT_MAX, LAT_MIN, LON_MAX, LON_MIN
from app.core.logger import get_logger
from app.core.schemas import Accident, AccidentReport, Ambulance
from app.core.seeds import load_ambulances

log = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    db.seed_ambulances(load_ambulances(AMBULANCE_SEED))
    log.info("database ready")
    yield


app = FastAPI(title="AI Emergency Response Network", lifespan=lifespan)


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
    accident = db.add_accident(report)
    log.info("accident %s reported, severity %s",
             accident.accident_id, accident.severity.value)
    return accident


@app.get("/accidents/{accident_id}", response_model=Accident)
def get_accident(accident_id: str):
    accident = db.get_accident(accident_id)
    if accident is None:
        raise HTTPException(404, "Accident not found")
    return accident