
import os
import re
import time
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from main.db import (
    get_settings, update_settings, set_thumbnail, get_thumbnail, clear_thumbnail,
    update_caption, get_caption, get_admins, is_admin_user,
    add_task, get_user_tasks, remove_task, save_file, get_saved_file, get_user_files, clear_database
)
from main.utils import progress_bar, take_screenshots, cleanup
from config import *

def change_video_metadata(input_path, video_title, audio_title, subtitle_title, output_path):
    command = [
        'ffmpeg',
        '-i', input_path,
        '-metadata', f'title={video_title}',
        '-metadata:s:v', f'title={video_title}',
        '-metadata:s:a', f'title={audio_title}',
        '-metadata:s:s', f'title={subtitle_title}',
        '-map', '0:v?',
        '-map', '0:a?',
        '-map', '0:s?',
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-c:s', 'copy',
        output_path,
        '-y'
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise Exception(f"FFmpeg error: {stderr.decode('utf-8')}")

@Client.on_message(filters.command("rename"))
async def rename_file(client, message: Message):
    user_id = message.from_user.id
    async with QUEUE:
        settings = get_settings(user_id)
        rename_type = settings.get("rename_type", "doc")
        prefix_on = settings.get("prefix_enabled", True)
        prefix_text = settings.get("prefix_text", "")
        metadata = settings.get("metadata", " | | ")
        caption_custom = get_caption(user_id)

        if len(message.command) >= 2:
            new_name = message.text.split(None, 1)[1]
        elif message.reply_to_message and message.reply_to_message.document:
            return await message.reply("❗ Provide a new filename after /rename")
        else:
            return await message.reply("❗ Reply to a document or provide filename.")

        if prefix_on:
            new_name = f"{prefix_text} {new_name}"

        add_task(user_id, new_name)

        thumb_id = get_thumbnail(user_id)
        thumb_path = None
        if thumb_id:
            try:
                thumb_path = await client.download_media(thumb_id, file_name=f"thumb_{user_id}.jpg")
            except:
                thumb_path = None

        task = {
            "message": await message.reply("📥 Starting download..."),
            "start_time": time.time(),
            "action": "📥 Downloading"
        }

        file_path = await message.reply_to_message.download(
            file_name=os.path.join(DOWNLOAD_DIR, new_name),
            progress=progress_bar,
            progress_args=(task,)
        )
        await task["message"].edit("✅ Download complete.")

        video_title, audio_title, subtitle_title = map(str.strip, metadata.split("|"))
        output_path = os.path.join(DOWNLOAD_DIR, f"meta_{new_name}")

        if rename_type == "video" and new_name.lower().endswith((".mp4", ".mkv", ".mov")):
            try:
                change_video_metadata(file_path, video_title, audio_title, subtitle_title, output_path)
                os.remove(file_path)
                file_path = output_path
            except Exception as e:
                await task["message"].edit(f"❌ Metadata Error: {e}")
                return

        caption = caption_custom.replace("{filename}", new_name) if caption_custom else f"📁 `{new_name}`"
        task = {
            "message": await message.reply("📤 Starting upload..."),
            "start_time": time.time(),
            "action": "📤 Uploading"
        }

        try:
            if rename_type == "video":
                await message.reply_video(file_path, caption=caption, thumb=thumb_path,
                                          progress=progress_bar, progress_args=(task,))
            else:
                await message.reply_document(file_path, caption=caption, thumb=thumb_path,
                                             progress=progress_bar, progress_args=(task,))
            await task["message"].edit("✅ Upload complete.")
        except Exception as e:
            await task["message"].edit(f"❌ Upload failed: {e}")
            return

        save_file(user_id, new_name, file_path)

        if settings.get("screenshot") and new_name.lower().endswith((".mp4", ".mkv", ".mov")):
            ss_dir = f"ss_{user_id}"
            os.makedirs(ss_dir, exist_ok=True)
            for ss in take_screenshots(file_path, ss_dir, settings.get("count", 3)):
                await message.reply_photo(ss)
            cleanup(ss_dir)

        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)

@Client.on_message(filters.command("setmeta"))
async def set_meta_command(client, message):
    uid = message.from_user.id
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /setmeta <video title | audio title | subtitle>")
    try:
        meta = message.text.split(None, 1)[1].strip()
        if meta.count("|") != 2:
            return await message.reply("❗ Use format: `video title | audio title | subtitle`")
        update_settings(uid, "metadata", meta)
        await message.reply("✅ Metadata updated.")
    except Exception as e:
        await message.reply(f"❗ Error: {e}")
