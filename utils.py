import os
import shutil
import subprocess
import time

# ⏳ Real-time Animated Progress Bar
async def progress_bar(current, total, message, action):
    percent = int(current * 100 / total)
    speed = current / (time.time() - message.date.timestamp() + 1)
    eta = (total - current) / speed if speed else 0
    try:
        await message.edit(f"{action}... {percent}%\nSpeed: {speed/1024:.2f} KB/s\nETA: {int(eta)}s")
    except:
        pass

# 🎞️ High-performance Screenshot Taker
def take_screenshots(video_path, output_dir, count=3):
    duration_cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path
    ]
    duration = float(subprocess.check_output(duration_cmd))
    interval = duration / (count + 1)
    output_paths = []

    for i in range(count):
        timestamp = int((i + 1) * interval)
        output_path = os.path.join(output_dir, f"ss_{i+1}.jpg")
        cmd = [
            'ffmpeg', '-ss', str(timestamp), '-i', video_path,
            '-frames:v', '1', '-q:v', '2', output_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        output_paths.append(output_path)

    return output_paths

# 🧹 Auto Cleanup
def cleanup(*paths):
    for path in paths:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        elif os.path.exists(path):
            os.remove(path)
