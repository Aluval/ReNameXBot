import os
import time
import subprocess

def progress_bar(current, total, task):
    now = time.time()
    elapsed = now - task["start_time"]
    speed = current / elapsed if elapsed > 0 else 0
    eta = (total - current) / speed if speed > 0 else 0
    percent = (current / total) * 100

    bar = f"{task['action']}... {percent:.0f}%\nSpeed: {speed/1024:.2f} KB/s\nETA: {int(eta)}s"
    try:
        task["message"].edit_text(bar)
    except:
        pass

def take_screenshots(file_path, output_dir, count=3):
    duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
    try:
        duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())
    except:
        duration = 0
    interval = duration // (count + 1)
    output_files = []

    for i in range(1, count + 1):
        timestamp = int(interval * i)
        out_file = os.path.join(output_dir, f"ss_{i}.jpg")
        cmd = f'ffmpeg -ss {timestamp} -i "{file_path}" -frames:v 1 "{out_file}" -q:v 2 -y'
        subprocess.call(cmd, shell=True)
        if os.path.exists(out_file):
            output_files.append(out_file)
    return output_files

def cleanup(path):
    if os.path.isdir(path):
        for f in os.listdir(path):
            os.remove(os.path.join(path, f))
        os.rmdir(path)
    elif os.path.isfile(path):
        os.remove(path)

def caption_styles(style, text):
    if style == "bold":
        return f"**{text}**"
    elif style == "italic":
        return f"__{text}__"
    elif style == "code":
        return f"`{text}`"
    elif style == "mono":
        return f"```{text}```"
    else:
        return text
