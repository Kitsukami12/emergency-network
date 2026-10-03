import os
import time
from datetime import datetime, timezone
from pathlib import Path

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"

import cv2
import requests
from dotenv import load_dotenv

from app.core import config
from app.services.detection import StubDetector, TemporalRule

load_dotenv()
SRC = os.environ["CAMERA_HOME_URL"]
LAT, LON = float(os.environ["CAMERA_HOME_LAT"]), float(os.environ["CAMERA_HOME_LON"])
API = os.getenv("API_URL", "http://127.0.0.1:8000")
CAMERA_ID = "home-1"
SAMPLE_FPS = 3
CONF_ACCEPT = getattr(config, "CONF_ACCEPT", 0.75)
CONF_VERIFY = getattr(config, "CONF_VERIFY", 0.50)
FRAMES = Path("results/frames")
FRAMES.mkdir(parents=True, exist_ok=True)

detector = StubDetector()          # swap for the trained model later
rule = TemporalRule()


def open_camera():
    cap = cv2.VideoCapture(SRC)
    return cap if cap.isOpened() else None


def raise_incident(frame, confidence):
    path = FRAMES / f"{CAMERA_ID}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
    cv2.imwrite(str(path), frame)
    if confidence < CONF_ACCEPT:
        # TODO: a human review queue. For now we only save the frame and log it.
        print(f"low confidence {confidence:.2f}: DETECTION REQUIRES VERIFICATION ({path})")
        return
    body = {
        "location": {"lat": LAT, "lon": LON},
        "severity": "MEDIUM",                 # PLACEHOLDER until the severity model exists
        "source": "camera",
        "camera_id": CAMERA_ID,
        "detection_confidence": round(confidence, 3),
        "frame_path": str(path),
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "description": "Accident detected by camera",
    }
    try:
        r = requests.post(f"{API}/accidents", json=body, timeout=10)
        print("incident posted:", r.status_code, r.json().get("accident_id"))
    except requests.RequestException as e:
        print("could not reach the API:", e)


def main():
    cap = None
    last = 0.0
    print(f"watching {CAMERA_ID}; create results/trigger to simulate an accident")
    while True:
        if cap is None:
            cap = open_camera()
            if cap is None:
                print("camera unreachable, retrying in 5 s")
                time.sleep(5)
                continue
        if not cap.grab():                       # cheap: keeps the buffer from lagging
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


if __name__ == "__main__":
    main()