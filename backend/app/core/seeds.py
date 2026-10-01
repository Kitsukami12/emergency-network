import json
from pathlib import Path

from app.core.schemas import Ambulance, Location


def load_ambulances(path: str | Path) -> list[Ambulance]:
    """Read the seed JSON and return validated Ambulance objects."""
    rows = json.loads(Path(path).read_text())
    return [
        Ambulance(
            ambulance_id=r["ambulance_id"],
            base_name=r["base_name"],
            location=Location(lat=r["lat"], lon=r["lon"]),
        )
        for r in rows
    ]