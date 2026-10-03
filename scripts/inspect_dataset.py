import re
import sys
from collections import defaultdict
from pathlib import Path

import cv2

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "data/videos/data")
EXT = {".jpg", ".jpeg", ".png"}


def group_of(p: Path) -> str:
    """Guess which source video a frame came from: the name before the last underscore."""
    stem = p.stem
    return re.sub(r"^\D+", "", stem.rsplit("_", 1)[0]) if "_" in stem else stem


counts, groups = {}, defaultdict(set)
for split in ["train", "val", "test"]:
    for cls in ["Accident", "Non Accident"]:
        files = [f for f in (ROOT / split / cls).glob("*") if f.suffix.lower() in EXT]
        counts[(split, cls)] = len(files)
        groups[split] |= {group_of(f) for f in files}

print(f"{'split':<7}{'Accident':>10}{'Non Accident':>14}")
for s in ["train", "val", "test"]:
    print(f"{s:<7}{counts[(s, 'Accident')]:>10}{counts[(s, 'Non Accident')]:>14}")

print("\nunique source groups:", {s: len(g) for s, g in groups.items()})
print("shared train/test groups:", len(groups["train"] & groups["test"]))
print("shared train/val groups :", len(groups["train"] & groups["val"]))

print("\nsample names:")
for s in ["train", "val", "test"]:
    names = sorted(f.name for f in (ROOT / s / "Accident").glob("*") if f.suffix.lower() in EXT)[:4]
    print(f"  {s}: {names}")

img = cv2.imread(str(next((ROOT / "train" / "Accident").glob("*.jpg"))))
print("\nexample image size (w x h):", img.shape[1], "x", img.shape[0])