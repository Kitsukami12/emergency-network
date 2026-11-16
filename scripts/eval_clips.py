"""Measure the detector on whole clips.
Usage: PYTHONPATH=backend python scripts/eval_clips.py data/clips/accident data/clips/normal
Prints, per clip, whether an incident was raised, so you get a detection rate on accident
clips and a false-alarm rate on normal clips."""
import sys
from pathlib import Path

import cv2

from app.services.detection import TemporalRule, YoloDetector
from app.services.tracker import estimate_severity

EXT = {".mp4", ".avi", ".mov", ".mkv"}
SAMPLE_FPS = 5


def run_clip(path):
    det, rule = YoloDetector(), TemporalRule(cooldown_s=1e9)
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    step, i, best, first, sev = max(1, round(fps / SAMPLE_FPS)), 0, 0.0, None, None
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % step == 0:
            t = i / fps
            s = det.score(frame, t)
            best = max(best, s)
            if rule.update(s, t) is not None and first is None:
                first, sev = t, estimate_severity(det.info)[0]
        i += 1
    return best, first, sev


def folder(name):
    files = sorted(f for f in Path(name).glob("*") if f.suffix.lower() in EXT)
    print(f"\n{name}: {len(files)} clips")
    return [(f, *run_clip(f)) for f in files]


acc, norm = folder(sys.argv[1]), folder(sys.argv[2])
for label, rows in (("ACCIDENT", acc), ("NORMAL", norm)):
    print(f"\n{label} clips")
    for f, best, first, sev in rows:
        print(f"  {f.name[:40]:<40} max score {best:.2f}  "
              f"{'RAISED at %.1fs, severity %s' % (first, sev) if first is not None else 'no incident'}")
hit = sum(r[2] is not None for r in acc)
fa = sum(r[2] is not None for r in norm)
print(f"\nDetected {hit}/{len(acc)} accident clips; false alarms on {fa}/{len(norm)} normal clips")
