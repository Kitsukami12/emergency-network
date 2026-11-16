from app.services.tracker import CollisionAnalyzer, estimate_severity

DT = 0.2


def car(x, y=300, w=100, h=60, cls="car"):
    return (cls, x, y, x + w, y + h, 0.9)


def run(frames):
    a, scores, last = CollisionAnalyzer(), [], {}
    for k, dets in enumerate(frames):
        s, info = a.update(dets, k * DT)
        scores.append(s); last = info
    return scores, last


def fired(scores):          # same idea as the temporal rule: 4 of 6 frames >= 0.6
    return any(sum(s >= 0.6 for s in scores[i:i + 6]) >= 4 for i in range(len(scores) - 5))


def test_head_on_crash_fires():
    frames = []
    for k in range(30):
        if k <= 7:
            xa, xb = 40 * k, 640 - 40 * k      # driving towards each other at speed
        else:
            xa, xb = 300, 340                  # both stop, boxes overlap
        frames.append([car(xa), car(xb)])
    scores, info = run(frames)
    assert fired(scores)
    assert info["involved"] == ["car", "car"]


def test_normal_traffic_stays_quiet():
    frames = [[car(60 * k), car(500 + 55 * k, y=400)] for k in range(30)]
    scores, _ = run(frames)
    assert max(scores) < 0.6


def test_slow_braking_without_contact_is_not_an_accident():
    xs, x = [], 0.0
    for k in range(40):
        v = max(0.0, 40 - 2.0 * k)           # gradual braking to a stop
        x += v; xs.append(x)
    scores, _ = run([[car(x)] for x in xs])
    assert not fired(scores)


def test_queue_of_overlapping_stopped_cars_is_ignored():
    frames = [[car(100), car(150)] for _ in range(30)]      # never moved
    scores, _ = run(frames)
    assert not fired(scores)


def test_duplicate_boxes_do_not_count_as_a_crash():
    frames = [[car(100 + 50 * k), ("car", 105 + 50 * k, 305, 190 + 50 * k, 350, 0.3)]
              for k in range(20)]
    scores, _ = run(frames)
    assert max(scores) < 0.6


def test_severity_rules():
    assert estimate_severity({"involved": ["car", "car"]})[0] == "LOW"
    assert estimate_severity({"involved": ["car", "car"], "peak_motion": 2.0})[0] == "MEDIUM"
    assert estimate_severity({"involved": ["car", "motorcycle"], "people_near": 1})[0] == "HIGH"
    label, _ = estimate_severity({"involved": ["bus", "car", "car"], "people_near": 2,
                                  "peak_motion": 2.0})
    assert label == "CRITICAL"
