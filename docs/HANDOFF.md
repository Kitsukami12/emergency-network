# Handoff notes

## Run
    # terminal 1, project root, venv active
    PYTHONPATH=backend python -m uvicorn app.main:app --port 8000
    # DEMO_SPEED=20 in front of the command makes ambulances finish their journeys 20x faster
    # terminal 2
    cd frontend && npm install && npm run dev

Copy `.env.example` to `.env`, `frontend/.env.example` to `frontend/.env.local` and
`cameras.local.example.json` to `cameras.local.json`, then fill in the keys (ask the owner).
Demo clips are not in git. Put the accident recordings in `data/clips/accident`, then run
`python scripts/make_demo_pool.py` and `PYTHONPATH=backend python scripts/seed_demo.py`.

## Endpoints the UI uses
GET /accidents, /ambulances, /hospitals, /cameras, /assignments (accident to hospital),
/accidents/{id}/media (frame and clip), /route, /notifications.
POST /accidents, /dispatch, /accidents/{id}/advance. Clips and frames are served under /clips, /frames.

## Behaviour
Incidents are assigned automatically. A timer (backend/app/services/progress.py) then moves each
one to en route, arrived and done at about its ETA plus or minus 2 minutes, and the ambulance
returns and becomes available again.

## Known gaps
- POST /demo/reset does not exist yet, so the Reset button fails.
- Ambulance markers change status but do not move along the route.
- Detector: 2 of 12 normal clips still false-alarm, and severity is inflated in dense scenes.
- "Ambulances free" counts the status string AVAILABLE; check it against /ambulances.
