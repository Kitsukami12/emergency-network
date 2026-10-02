from app.core.enums import AccidentStatus as S
from app.core.transitions import can_transition

def test_normal_flow_is_allowed():
    assert can_transition(S.DETECTED, S.ASSESSING)

def test_cannot_skip_to_resolved():
    assert not can_transition(S.DETECTED, S.RESOLVED)

def test_resolved_cannot_be_reopened():
    assert not can_transition(S.RESOLVED, S.DETECTED)

def test_cancelled_cannot_be_reopened():
    assert not can_transition(S.CANCELLED, S.DETECTED)

def test_needs_verification_can_go_to_assessing():
    assert can_transition(S.NEEDS_VERIFICATION, S.ASSESSING)

def test_needs_verification_can_go_to_cancelled():
    assert can_transition(S.NEEDS_VERIFICATION, S.CANCELLED)

def test_en_route_can_be_cancelled():
    assert can_transition(S.EN_ROUTE, S.CANCELLED)

def test_breakdown_returns_to_awaiting():
    assert can_transition(S.AMBULANCE_ASSIGNED, S.AWAITING_AMBULANCE)

def test_cannot_cancel_after_arrival():
    assert not can_transition(S.ARRIVED, S.CANCELLED)