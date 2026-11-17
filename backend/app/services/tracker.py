"""Accident cues from vehicle tracks.

Pure logic: it takes detections (class, box, confidence) per time step and returns an
accident score plus details. It never touches YOLO or video, so it can be unit-tested.
All thresholds are first guesses: tune them with scripts/eval_clips.py on real clips.
"""
import math
from dataclasses import dataclass, field

VEHICLES = {"car", "motorcycle", "bus", "truck"}
CFG = dict(
    match_dist=1.2,    # max centroid jump (in box sizes) to link a detection to a track
    track_ttl=1.5,     # seconds a track survives without a match
    min_age=3,         # samples before a track is trusted
    moving=0.6,        # motion (box sizes per second) above this = moving
    stopped=0.2,       # smoothed motion below this = stopped
    window=2.0,        # seconds of history used to find a recent speed drop
    overlap_iou=0.12,  # boxes overlapping more than this are in contact
    dup_cover=0.85,    # same-class box mostly inside another = duplicate detection
    hold_s=2.5,        # keep the alarm up this long after a collision cue
    people_radius=1.5, # people within this many box sizes of the crash count as nearby
)


@dataclass
class Track:
    tid: int
    cls: str
    box: tuple
    last_t: float
    age: int = 1
    ema: float = 0.0
    hist: list = field(default_factory=list)      # (t, smoothed motion)
    votes: dict = field(default_factory=dict)

    def size(self):
        x1, y1, x2, y2 = self.box
        return math.sqrt(max((x2 - x1) * (y2 - y1), 1e-6))

    def centre(self):
        x1, y1, x2, y2 = self.box
        return (x1 + x2) / 2, (y1 + y2) / 2


def iou(a, b):
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def cover(a, b):
    """Share of the smaller box that lies inside the other."""
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return ix * iy / small if small > 0 else 0.0


def clean(dets):
    """Drop duplicate boxes (same class, one mostly inside the other), keep the more confident."""
    keep = []
    for d in sorted(dets, key=lambda d: -d[5]):
        if all(not (d[0] == k[0] and cover(d[1:5], k[1:5]) > CFG["dup_cover"]) for k in keep):
            keep.append(d)
    return keep


class CollisionAnalyzer:
    def __init__(self, cfg=None):
        self.cfg = {**CFG, **(cfg or {})}
        self.tracks: dict[int, Track] = {}
        self.next_id = 1
        self.hold_until = -1e9
        self.hold_info = None

    # ---- tracking -------------------------------------------------------------
    def _update_tracks(self, vehicles, t):
        c = self.cfg
        free = list(range(len(vehicles)))
        pairs = []
        for tid, tr in self.tracks.items():
            tx, ty = tr.centre()
            for i in free:
                d = vehicles[i]
                cx, cy = (d[1] + d[3]) / 2, (d[2] + d[4]) / 2
                size = max(tr.size(), math.sqrt(max((d[3] - d[1]) * (d[4] - d[2]), 1e-6)))
                dist = math.hypot(cx - tx, cy - ty) / size
                if dist <= c["match_dist"]:
                    pairs.append((dist, tid, i))
        used_t, used_d = set(), set()
        for dist, tid, i in sorted(pairs):
            if tid in used_t or i in used_d:
                continue
            used_t.add(tid); used_d.add(i)
            self._apply(self.tracks[tid], vehicles[i], t)
        for i in free:
            if i not in used_d:
                d = vehicles[i]
                self.tracks[self.next_id] = Track(self.next_id, d[0], tuple(d[1:5]), t,
                                                  votes={d[0]: 1})
                self.next_id += 1
        for tid in [k for k, tr in self.tracks.items() if t - tr.last_t > c["track_ttl"]]:
            del self.tracks[tid]

    def _apply(self, tr, d, t):
        dt = t - tr.last_t
        if dt <= 0:
            return
        nb = tuple(d[1:5])
        (x0, y0), s0 = tr.centre(), tr.size()
        tr.box = nb
        (x1, y1), s1 = tr.centre(), tr.size()
        m = (math.hypot(x1 - x0, y1 - y0) / ((s0 + s1) / 2)
             + 2 * abs(math.log(s1 / s0))) / dt
        m = min(m, 10.0)
        tr.ema = m if tr.age == 1 else 0.5 * m + 0.5 * tr.ema
        tr.age += 1
        tr.last_t = t
        tr.hist.append((t, tr.ema))
        tr.hist = [h for h in tr.hist if t - h[0] <= self.cfg["window"] + 1.0]
        tr.votes[d[0]] = tr.votes.get(d[0], 0) + 1
        tr.cls = max(tr.votes, key=tr.votes.get)

    def _peak(self, tr, t):
        vals = [v for (ht, v) in tr.hist if t - ht <= self.cfg["window"]]
        return max(vals) if vals else 0.0

    def _decelerated(self, tr, t):
        c, peak = self.cfg, self._peak(tr, t)
        return peak >= c["moving"] and tr.ema < 0.5 * peak

    def _stopped_suddenly(self, tr, t):
        return self._peak(tr, t) >= self.cfg["moving"] and tr.ema <= self.cfg["stopped"]

    # ---- one time step --------------------------------------------------------
    def update(self, dets, t):
        """dets: list of (class_name, x1, y1, x2, y2, conf). Returns (score, info)."""
        c = self.cfg
        dets = clean(dets)
        vehicles = [d for d in dets if d[0] in VEHICLES]
        people = [d for d in dets if d[0] == "person"]
        self._update_tracks(vehicles, t)
        trusted = [tr for tr in self.tracks.values()
                   if tr.age >= c["min_age"] and tr.last_t == t]

        involved, peak = set(), 0.0
        for i in range(len(trusted)):
            for j in range(i + 1, len(trusted)):
                a, b = trusted[i], trusted[j]
                if iou(a.box, b.box) >= c["overlap_iou"] and (
                        self._decelerated(a, t) or self._decelerated(b, t)):
                    involved |= {a.tid, b.tid}
        for tid in involved:
            peak = max(peak, self._peak(self.tracks[tid], t))
        lone_stop = any(self._stopped_suddenly(tr, t) for tr in trusted)

        if involved:
            boxes = [self.tracks[k].box for k in involved]
            cx = sum((b[0] + b[2]) / 2 for b in boxes) / len(boxes)
            cy = sum((b[1] + b[3]) / 2 for b in boxes) / len(boxes)
            span = max(self.tracks[k].size() for k in involved)
            near = sum(1 for p in people
                       if math.hypot((p[1] + p[3]) / 2 - cx, (p[2] + p[4]) / 2 - cy)
                       <= c["people_radius"] * span)
            self.hold_until = t + c["hold_s"]
            self.hold_info = {
                "involved": sorted(self.tracks[k].cls for k in involved),
                "peak_motion": round(peak, 2),
                "people_near": near,
            }
            score = 0.9
        elif t < self.hold_until:
            score = 0.85
        elif lone_stop:
            score = 0.45
        else:
            score = 0.05
        info = dict(self.hold_info or {})
        info.update(vehicles_in_view=len(vehicles), people_in_view=len(people))
        return score, info


def estimate_severity(info):
    """Rule-based incident severity (NOT a medical estimate). Returns (label, reasons)."""
    pts, why = 0, []
    inv = info.get("involved") or []
    if len(inv) >= 3:
        pts += 2; why.append(f"{len(inv)} vehicles involved")
    elif len(inv) == 2:
        pts += 1; why.append("2 vehicles in contact")
    if "motorcycle" in inv:
        pts += 1; why.append("two-wheeler involved")
    if any(v in inv for v in ("bus", "truck")):
        pts += 1; why.append("heavy vehicle involved")
    if info.get("people_near", 0) >= 1:
        pts += 1; why.append("people near the scene")
    if info.get("peak_motion", 0) >= 1.5:
        pts += 1; why.append("fast approach before the stop")
    label = "LOW" if pts <= 1 else "MEDIUM" if pts == 2 else "HIGH" if pts == 3 else "CRITICAL"
    return label, why
