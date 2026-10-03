import sys
from ultralytics import YOLO

NAMES = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
m = YOLO("yolov8m.pt")
for imgsz, conf in [(960, 0.05), (1280, 0.05), (1280, 0.02)]:
    r = m(sys.argv[1], imgsz=imgsz, conf=conf, classes=list(NAMES), iou=0.5, verbose=False)[0]
    found = sorted(zip(r.boxes.cls.tolist(), r.boxes.conf.tolist()), key=lambda x: -x[1])
    print(imgsz, conf, [(NAMES[int(c)], round(p, 2)) for c, p in found])
    r.save(filename=f"results/yolo_low_{imgsz}_{conf}.jpg")