from collections import deque
from pathlib import Path


class StubDetector:
    def __init__(self, trigger="results/trigger"):
        self.trigger = Path(trigger)

    def score(self, frame) -> float:
        return 0.95 if self.trigger.exists() else 0.05

    
class TemporalRule:
    """Raise an incident only when `needed` of the last `window` frame scores are
    above `threshold`. After raising, stay quiet for `cooldown_s` seconds, so one
    accident seen in hundreds of frames creates one incident."""

    def __init__(self, window=6, needed=4, threshold=0.6, cooldown_s=120):
        self.window, self.needed = window, needed
        self.threshold, self.cooldown_s = threshold, cooldown_s
        self.scores = deque(maxlen=window)
        self.quiet_until = 0.0

    def update(self, score: float, now: float):
        """Feed one frame score. Returns the incident confidence when an accident
        should be raised, otherwise None."""
        self.scores.append(score)
        if now < self.quiet_until or len(self.scores) < self.window:
            return None
        hits = [s for s in self.scores if s >= self.threshold]
        if len(hits) < self.needed:
            return None
        self.quiet_until = now + self.cooldown_s
        self.scores.clear()
        return sum(hits) / len(hits)

    # ---- append to backend/app/services/detection.py ----

class YoloDetector:
    """YOLO vehicle detection plus the collision logic in tracker.py.
    The torch/ultralytics imports happen here, so the cloud server never needs them."""

    CLASSES = [0, 2, 3, 5, 7]          # person, car, motorcycle, bus, truck

    def __init__(self, weights="yolov8s.pt", imgsz=960, conf=0.25, trigger=None):
        import torch
        from ultralytics import YOLO

        from app.services.tracker import CollisionAnalyzer
        self.model = YOLO(weights)
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.imgsz, self.conf = imgsz, conf
        self.analyzer = CollisionAnalyzer()
        self.trigger = Path(trigger) if trigger else None   # optional manual override for demos
        self.info = {}

    def score(self, frame, t) -> float:
        r = self.model(frame, imgsz=self.imgsz, conf=self.conf, classes=self.CLASSES,
                       agnostic_nms=True, device=self.device, verbose=False)[0]
        names = self.model.names
        dets = [(names[int(c)], *map(float, b), float(p))
                for c, b, p in zip(r.boxes.cls, r.boxes.xyxy, r.boxes.conf)]
        score, self.info = self.analyzer.update(dets, t)
        if self.trigger and self.trigger.exists():
            return max(score, 0.95)
        return score
