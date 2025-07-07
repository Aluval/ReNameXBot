import os
import shutil
import subprocess
import time

# ✨ Format caption styles
def caption_styles(style: str, text: str) -> str:
    if style == "bold":
        return f"**{text}**"
    elif style == "italic":
        return f"__{text}__"
    elif style == "code":
        return f"`{text}`"
    elif style == "mono":
        return f"```{text}```"
    elif style == "plain":
        return text
    return text

# ⏳ Progress Bar
async def progress_bar(current, total, task):
    percent = int(current * 100 / total)
    speed = current / (time.time() - task["start_time"] + 1)
    eta = (total - current) / speed if speed else 0
    try:
        await task["message"].edit(
            f"{task['action']}... {percent}%\n"
            f"Speed: {speed / 1024:.2f} KB/s\n"
            f"ETA: {int(eta)}s"
        )
    except:
        pass

# 🎞️ Take Screenshots from a Video
def take_screenshots(video_path, output_dir, count=3):
    duration_cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    try:
        duration = float(subprocess.check_output(duration_cmd))
    except:
        duration = 60

    interval = duration / (count + 1)
    output_paths = []

    for i in range(count):
        timestamp = int((i + 1) * interval)
        output_path = os.path.join(output_dir, f"ss_{i + 1}.jpg")
        cmd = [
            'ffmpeg', '-ss', str(timestamp), '-i', video_path,
            '-frames:v', '1', '-q:v', '2', output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_path):
            output_paths.append(output_path)

    return output_paths

# 🧹 Cleanup Temporary Files/Folders
def cleanup(*paths):
    for path in paths:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        elif os.path.exists(path):
            os.remove(path)
