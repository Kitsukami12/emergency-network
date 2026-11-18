"""Cut short clips and stills from the accident recordings for the demo pool.
Usage: python scripts/make_demo_pool.py   (needs ffmpeg; the server does not need to run)"""
import subprocess
from pathlib import Path

SRC, FRAMES, CLIPS = Path("data/clips/accident"), Path("results/frames"), Path("results/clips")
FRAMES.mkdir(parents=True, exist_ok=True)
CLIPS.mkdir(parents=True, exist_ok=True)


def duration(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


n = 0
for src in sorted(SRC.glob("*.mp4")):
    d = duration(src)
    for frac in (0.15, 0.4, 0.65):
        start, n = d * frac, n + 1
        name = f"demo_pool_{n:02d}"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.1f}", "-i", str(src),
                        "-t", "12", "-vf", "scale=-2:480", "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "28", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart",
                        str(CLIPS / f"{name}.mp4")], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{min(start + 4, d - 0.5):.1f}",
                        "-i", str(src), "-frames:v", "1", str(FRAMES / f"{name}.jpg")], check=True)
print(n, "pairs written")
