import sys
from pathlib import Path

from ultralytics import YOLO

COCO = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
CONFIGS = [  # (weights, image size, confidence threshold)
    ("yolov8n.pt", 640, 0.25),
    ("yolov8n.pt", 960, 0.15),
    ("yolov8s.pt", 960, 0.15),
    ("yolov8m.pt", 960, 0.15),
]
src = sys.argv[1]
Path("results").mkdir(exist_ok=True)

for weights, imgsz, conf in CONFIGS:
    model = YOLO(weights)
    r = model(src, imgsz=imgsz, conf=conf, classes=list(COCO), agnostic_nms=True, verbose=False)[0]
    ids = [int(c) for c in r.boxes.cls]
    counts = {name: ids.count(i) for i, name in COCO.items() if i in ids}
    out = f"results/yolo_{Path(weights).stem}_{imgsz}.jpg"
    r.save(filename=out)
    print(f"{weights:<11} size={imgsz} conf={conf}: {counts} -> {out}")