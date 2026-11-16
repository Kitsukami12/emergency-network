import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

import requests
from dotenv import load_dotenv

from app.services.detection import StubDetector, TemporalRule

load_dotenv()
ap = argparse.ArgumentParser()
ap.add_argument("camera_id")
CAMERA_ID = ap.parse_args().camera_id
cam = {c["id"]: c for c in json.load(open("cameras.local.json"))}[CAMERA_ID]
SRC, LAT, LON = cam["url"], cam["lat"], cam["lon"]
API = os.getenv("API_URL", "http://127.0.0.1:8000")
HEADERS = {"X-API-Key": os.getenv("AGENT_API_KEY", "")}
SAMPLE_FPS, CONF_ACCEPT = 3, 0.75
FRAMES = Path("results/frames")
FRAMES.mkdir(parents=True, exist_ok=True)

detector = StubDetector(f"results/trigger_{CAMERA_ID}")
rule = TemporalRule()


def raise_incident(frame, confidence):
    path = FRAMES / f"{CAMERA_ID}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
    cv2.imwrite(str(path), frame)
    if confidence < CONF_ACCEPT:
        print(f"low confidence {confidence:.2f}: DETECTION REQUIRES VERIFICATION ({path})")
        return
    body = {
        "location": {"lat": LAT, "lon": LON},
        "severity": "MEDIUM",                 # PLACEHOLDER until severity rules exist
        "source": "camera", "camera_id": CAMERA_ID,
        "detection_confidence": round(confidence, 3),
        "frame_path": str(path),
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "description": "Accident detected by camera",
    }
    try:
        r = requests.post(f"{API}/accidents", json=body, headers=HEADERS, timeout=10)
        print("incident posted:", r.status_code, r.json().get("accident_id", r.text))
    except requests.RequestException as e:
        print("could not reach the API:", e)


cap, last = None, 0.0
print(f"watching {CAMERA_ID}; create results/trigger_{CAMERA_ID} to simulate an accident")
while True:
    if cap is None:
        cap = cv2.VideoCapture(SRC)
        if not cap.isOpened():
            cap = None
            print("camera unreachable, retrying in 5 s")
            time.sleep(5)
            continue
    if not cap.grab():                         # also restarts a video file when it ends
        cap.release()
        cap = None
        continue
    now = time.time()
    if now - last < 1 / SAMPLE_FPS:
        continue
    last = now
    ok, frame = cap.retrieve()
    if not ok:
        continue
    confidence = rule.update(detector.score(frame), now)
    if confidence is not None:
        raise_incident(frame, confidence)