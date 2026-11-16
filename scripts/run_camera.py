import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

import cv2
import requests
from dotenv import load_dotenv

from app.services.detection import StubDetector, TemporalRule
from app.services.tracker import estimate_severity

load_dotenv(".env")
ap = argparse.ArgumentParser()
ap.add_argument("camera_id")
ap.add_argument("--detector", choices=["yolo", "stub"], default="yolo")
args = ap.parse_args()
CAMERA_ID = args.camera_id
cam = {c["id"]: c for c in json.load(open("cameras.local.json"))}[CAMERA_ID]
SRC, LAT, LON = cam["url"], cam["lat"], cam["lon"]
IS_FILE = not str(SRC).lower().startswith(("rtsp://", "http://", "https://"))
API = os.getenv("API_URL", "http://127.0.0.1:8000")
HEADERS = {"X-API-Key": os.getenv("AGENT_API_KEY", "")}
AUTH = ("agent", os.getenv("DASHBOARD_PIN", "")) if os.getenv("DASHBOARD_PIN") else None
SAMPLE_FPS, CONF_ACCEPT = 5, 0.75
FRAMES = Path("results/frames")
FRAMES.mkdir(parents=True, exist_ok=True)
TRIGGER = f"results/trigger_{CAMERA_ID}"

if args.detector == "yolo":
    from app.services.detection import YoloDetector
    detector = YoloDetector(trigger=TRIGGER)
else:
    detector = StubDetector(TRIGGER)
rule = TemporalRule()


def raise_incident(frame, confidence):
    info = getattr(detector, "info", {}) or {}
    path = FRAMES / f"{CAMERA_ID}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
    cv2.imwrite(str(path), frame)
    if confidence < CONF_ACCEPT:
        print(f"low confidence {confidence:.2f}: DETECTION REQUIRES VERIFICATION ({path})")
        return
    if info.get("involved"):
        severity, why = estimate_severity(info)
        description = "Accident detected by camera. Rule-based estimate: " + "; ".join(why)
    else:
        severity, description = "MEDIUM", "Accident detected by camera (manual trigger)"
    body = {
        "location": {"lat": LAT, "lon": LON},
        "severity": severity,
        "source": "camera", "camera_id": CAMERA_ID,
        "detection_confidence": round(confidence, 3),
        "frame_path": str(path),
        "vehicle_count": len(info.get("involved") or []) or info.get("vehicles_in_view"),
        "people_count": info.get("people_near", info.get("people_in_view")),
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "description": description,
    }
    try:
        r = requests.post(f"{API}/accidents", json=body, headers=HEADERS, auth=AUTH, timeout=10)
        print("incident posted:", r.status_code, severity, r.json().get("accident_id", r.text))
    except requests.RequestException as e:
        print("could not reach the API:", e)


cap, last, vt = None, -1e9, 0.0       # vt: a clock that keeps running, also across video loops
print(f"watching {CAMERA_ID} with the {args.detector} detector; "
      f"create {TRIGGER} to simulate an accident")
while True:
    if cap is None:
        cap = cv2.VideoCapture(SRC)
        if not cap.isOpened():
            cap = None
            print("camera unreachable, retrying in 60 s")
            time.sleep(60)
            continue
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
    if not cap.grab():                         # end of a video file: start again
        cap.release()
        cap = None
        continue
    if IS_FILE:
        vt += 1 / fps
        time.sleep(1 / fps)                    # play files in real time
        t = vt
    else:
        t = time.time()
    if t - last < 1 / SAMPLE_FPS:
        continue
    last = t
    ok, frame = cap.retrieve()
    if not ok:
        continue
    conf = rule.update(detector.score(frame, t) if args.detector == "yolo"
                       else detector.score(frame), t)
    if conf is not None:
        raise_incident(frame, conf)
