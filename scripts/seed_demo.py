"""Seed one demo incident per site in demo_sites.json, each with a browser-playable clip.
Usage (server running): PYTHONPATH=backend python scripts/seed_demo.py [--only demo-rajwada]
Needs ffmpeg and the recordings in data/clips/accident."""
import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(".env")
ap = argparse.ArgumentParser()
ap.add_argument("--only")
args = ap.parse_args()

API = os.getenv("API_URL", "http://127.0.0.1:8000")
HEADERS = {"X-API-Key": os.getenv("AGENT_API_KEY", "")}
SRC = Path("data/clips/accident")
FRAMES, CLIPS = Path("results/frames"), Path("results/clips")
FRAMES.mkdir(parents=True, exist_ok=True)
CLIPS.mkdir(parents=True, exist_ok=True)


def duration(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


for site in json.load(open("demo_sites.json")):
    if args.only and site["id"] != args.only:
        continue
    src = SRC / site["clip"]
    if not src.exists():
        print(f"{site['id']}: missing {src}, skipped")
        continue
    stem = f"{site['id']}_{datetime.now():%Y%m%d_%H%M%S}"
    clip, frame = CLIPS / f"{stem}.mp4", FRAMES / f"{stem}.jpg"
    # H.264, no audio, faststart: plays in every browser, including Safari
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-t", "40",
                    "-vf", "scale=-2:480", "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "28", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart",
                    str(clip)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(duration(src) / 2),
                    "-i", str(src), "-frames:v", "1", str(frame)], check=True)
    body = {
        "location": {"lat": site["lat"], "lon": site["lon"]},
        "severity": site["severity"],
        "source": "camera", "camera_id": site["id"],
        "detection_confidence": 0.9,
        "frame_path": str(frame),
        "vehicle_count": None, "people_count": None,     # not measured in a replay
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "description": f"DEMO replay of a recorded clip at {site['name']}. "
                       "Severity set by hand for the demo.",
    }
    r = requests.post(f"{API}/accidents", json=body, headers=HEADERS, timeout=15)
    print(f"{site['id']}: {r.status_code} {r.json().get('accident_id', r.text[:80])}")
