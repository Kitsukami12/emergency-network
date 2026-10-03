
import sys
from pathlib import Path

from ultralytics import YOLO

VEHICLES = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}   # COCO class ids
PERSON = 0

model = YOLO("yolov8n.pt")            # smallest model, downloaded on first use
Path("results").mkdir(exist_ok=True)

for src in sys.argv[1:]:
    r = model(src, verbose=False)[0]
    classes = [int(c) for c in r.boxes.cls]
    counts = {name: classes.count(cid) for cid, name in VEHICLES.items()}
    counts = {k: v for k, v in counts.items() if v}
    out = f"results/yolo_{Path(src).stem}.jpg"
    r.save(filename=out)
    print(f"{Path(src).name}: vehicles={sum(counts.values())} {counts} "
          f"people={classes.count(PERSON)} -> {out}")