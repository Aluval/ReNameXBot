import os
import time
from typing import Dict, List
from pathlib import Path
import subprocess

def progress_bar(current: int, total: int, task: Dict):
    now = time.time()
    diff = now - task["start_time"]
    if diff == 0:
        diff = 1
    speed = current / diff
    eta = (total - current) / speed if speed != 0 else 0
    percent = current * 100 / total

    try:
        text = (
            f"{task['action']}... {percent:.0f}%\n"
            f"Speed: {speed / (1024 * 1024):.2f} MB/s\n"
            f"ETA: {int(eta)}s"
        )
        task["message"].edit(text)
    except:
        pass

def take_screenshots(path: str, output_dir: str, count: int = 3) -> List[str]:
    try:
        duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path
        ]
        duration = float(subprocess.check_output(duration_cmd).decode().strip())
        interval = duration / (count + 1)
        screenshots = []

        for i in range(1, count + 1):
            timestamp = int(i * interval)
            output = f"{output_dir}/ss_{i}.jpg"
            cmd = ["ffmpeg", "-ss", str(timestamp), "-i", path, "-vframes", "1", "-q:v", "2", output]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(output):
                screenshots.append(output)

        return screenshots
    except Exception as e:
        print(f"[ERROR] Screenshot error: {e}")
        return []

def cleanup(path: str):
    if os.path.isdir(path):
        for f in os.listdir(path):
            os.remove(os.path.join(path, f))
        os.rmdir(path)
    elif os.path.isfile(path):
        os.remove(path)

def caption_styles(style: str, text: str) -> str:
    if style == "bold":
        return f"**{text}**"
    elif style == "italic":
        return f"__{text}__"
    elif style == "mono":
        return f"```{text}```"
    elif style == "code":
        return f"`{text}`"
    else:
        return text
