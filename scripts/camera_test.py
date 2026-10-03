import os
import sys
import time

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"   # more reliable than UDP

import cv2
from dotenv import load_dotenv

load_dotenv()
src = sys.argv[1] if len(sys.argv) > 1 else os.getenv("CAMERA_HOME_URL")
if not src:
    sys.exit("Give a source: python scripts/camera_test.py <rtsp-url | video-file | 0>")
if src.isdigit():
    src = int(src)                       # 0 = laptop webcam

cap = cv2.VideoCapture(src)
if not cap.isOpened():
    sys.exit("Could not open the source. Check the address, login, and that you are on the same Wi-Fi.")

ok, frame = cap.read()
if not ok:
    sys.exit("Opened, but no frame arrived.")
print(f"first frame: {frame.shape[1]}x{frame.shape[0]}")

start, n = time.time(), 0
while time.time() - start < 5:
    if cap.read()[0]:
        n += 1
print(f"{n / 5:.1f} frames per second over 5 s")

os.makedirs("results", exist_ok=True)
cv2.imwrite("results/frame_test.jpg", frame)
print("saved results/frame_test.jpg, open it and check it shows your road")