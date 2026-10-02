from app.core.enums import AccidentStatus as S

ALLOWED = {
    S.DETECTED: {S.ASSESSING, S.NEEDS_VERIFICATION, S.CANCELLED},
    S.ASSESSING: {S.AWAITING_AMBULANCE, S.CANCELLED},
    S.AWAITING_AMBULANCE: {S.AMBULANCE_ASSIGNED, S.CANCELLED},
    # can go back to AWAITING if the ambulance breaks down, or be cancelled
    S.AMBULANCE_ASSIGNED: {S.EN_ROUTE, S.AWAITING_AMBULANCE, S.CANCELLED},
    # operator can recall the ambulance if it was a false alarm;
    # AWAITING_AMBULANCE allowed in case the vehicle breaks down mid-route
    S.EN_ROUTE: {S.ARRIVED, S.AWAITING_AMBULANCE, S.CANCELLED},
    # once on scene, the only way forward is resolving it
    S.ARRIVED: {S.RESOLVED},
    # a human decides: confirm -> assess, reject -> cancel
    S.NEEDS_VERIFICATION: {S.ASSESSING, S.CANCELLED},
    S.RESOLVED: set(),     # finished, nowhere to go
    S.CANCELLED: set(),    # finished, nowhere to go
}

def can_transition(current: S, new: S) -> bool:
    return new in ALLOWED.get(current, set())