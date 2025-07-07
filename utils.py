import os
import time
from typing import Dict, List
from pathlib import Path
import subprocess

def progress_bar(current: int, total: int, task: Dict):
    now = time.time()

    # Limit update frequency to avoid Telegram FloodWait
    if "last_edit" in task and now - task["last_edit"] < 2:
        return

    task["last_edit"] = now
    diff = now - task["start_time"]
    diff = diff if diff != 0 else 1  # Avoid div by zero

    speed = current / diff
    eta = (total - current) / speed if speed else 0
    percent = current * 100 / total

    # Convert sizes to readable MB/GB
    def human_readable(size):
        if size > 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"
        else:
            return f"{size / (1024 * 1024):.2f} MB"

    current_str = human_readable(current)
    total_str = human_readable(total)

    # Visual progress bar
    bar_length = 20
    filled_len = int(bar_length * current / total)
    bar = "█" * filled_len + "░" * (bar_length - filled_len)

    # Construct the final message
    msg = (
        f"{task['action']}... [{bar}] {percent:.0f}%\n"
        f"Size: {current_str} / {total_str}\n"
        f"Speed: {speed / (1024 * 1024):.2f} MB/s\n"
        f"ETA: {int(eta)}s"
    )

    try:
        task["message"].edit(msg)
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
        return f"*{text}*"
    elif style == "italic":
        return f"_{text}_"
    elif style == "code":
        return f"`{text}`"
    else:
        return text
