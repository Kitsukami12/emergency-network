from app.services.detection import TemporalRule


def feed(rule, scores, start=0.0, step=0.33):
    """Feed a list of scores, return every confidence that was raised."""
    out = []
    for i, s in enumerate(scores):
        r = rule.update(s, start + i * step)
        if r is not None:
            out.append(r)
    return out


def test_sustained_accident_raises_once():
    raised = feed(TemporalRule(), [0.9] * 20)
    assert len(raised) == 1


def test_single_spike_is_ignored():
    raised = feed(TemporalRule(), [0.05, 0.05, 0.95, 0.05, 0.05, 0.05, 0.05, 0.05])
    assert raised == []

# TODO 1: a cooldown test. Feed 20 high scores (one incident), then 20 more high
#         scores with `start=5` (still inside the 120 s cooldown). Total raised must be 1.
def test_cooldown():
    rule = TemporalRule()
    raised1 = feed(rule, [0.9] * 20)
    raised2 = feed(rule, [0.9] * 20, start=5)
    assert len(raised1) == 1
    assert len(raised2) == 0

# TODO 2: after the cooldown. Same as above but the second batch uses `start=200`.
#         Total raised must be 2.
def test_after_cooldown():
    rule = TemporalRule()
    raised1 = feed(rule, [0.9] * 20)
    raised2 = feed(rule, [0.9] * 20, start=200)
    assert len(raised1) == 1
    assert len(raised2) == 1

# TODO 3: low scores forever (0.1 x 50) raise nothing.
def test_low_scores_raise_nothing():
    raised = feed(TemporalRule(), [0.1] * 50)
    assert raised == []