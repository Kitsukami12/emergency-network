from collections import deque
from pathlib import Path


class StubDetector:
    """PLACEHOLDER until the trained model exists.
    Scores 0.95 while the file results/trigger exists, otherwise 0.05.
    Create the file to simulate an accident; delete it to stop."""

    def score(self, frame) -> float:
        return 0.95 if Path("results/trigger").exists() else 0.05


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