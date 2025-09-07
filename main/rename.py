#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
import os
import re
import time
import asyncio, math
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from main.utils import progress_bar, take_screenshots
from config import *
from main.db import (
    get_settings,
    update_settings,
    reset_settings,
    set_thumbnail,
    get_thumbnail,
    clear_thumbnail,
    update_caption,
    get_caption,
    add_task,
    get_user_tasks,
    get_all_user_tasks,
    remove_task,
    save_file,
    get_saved_file,
    get_user_files,
    clear_user_files,
    clear_database
)


# Reusable settings panel builder for edit_caption
async def send_settings_panel(client, message):
    user_id = message.from_user.id
    s = get_settings(user_id)
    count = s.get("count", 3)

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📸 Screenshot: {'✅' if s.get('screenshot') else '❌'}", callback_data="set_toggle_ss")],
        [
            InlineKeyboardButton("➖", callback_data="set_decrease_count"),
            InlineKeyboardButton(f"🧮 Count: {count}", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data="set_increase_count")
        ],
        [
            InlineKeyboardButton(f"📎 Prefix: {'✅' if s.get('prefix_enabled') else '❌'}", callback_data="set_toggle_prefix"),
            InlineKeyboardButton(f"📄 Type: {s.get('rename_type')}", callback_data="set_toggle_type")
        ],
        [InlineKeyboardButton("🖼️ Thumbnail", callback_data="set_thumb_menu")],
        [
            InlineKeyboardButton("🔤 Prefix Text", callback_data="set_show_prefix"),
            InlineKeyboardButton("📄 Caption", callback_data="set_show_caption")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="set_close")]
    ])

    await client.send_photo(
        chat_id=message.chat.id,
        photo=INFO_PIC,
        caption="⚙️ Customize your bot settings:",
        reply_markup=markup
    )


# /settings command
@Client.on_message(filters.command("settings"))
async def open_settings(client, message: Message):
    await send_settings_panel(client, message)


# Callback handler for all setting actions
@Client.on_callback_query(filters.regex("^set_"))
async def settings_callback_handler(client, cb: CallbackQuery):
    uid = cb.from_user.id
    s = get_settings(uid)
    data = cb.data

    if data == "set_toggle_ss":
        update_settings(uid, "screenshot", not s.get("screenshot", False))

    elif data == "set_toggle_prefix":
        update_settings(uid, "prefix_enabled", not s.get("prefix_enabled", True))

    elif data == "set_toggle_type":
        new_type = "video" if s.get("rename_type") == "doc" else "doc"
        update_settings(uid, "rename_type", new_type)

    elif data == "set_increase_count":
        current = s.get("count", 3)
        if current < 20:
            update_settings(uid, "count", current + 1)

    elif data == "set_decrease_count":
        current = s.get("count", 3)
        if current > 1:
            update_settings(uid, "count", current - 1)

    elif data == "set_show_prefix":
        await cb.answer()
        return await cb.message.reply(f"📎 Current Prefix:\n{ s.get('prefix_text', '-') }")

    elif data == "set_show_caption":
        cap = get_caption(uid) or "None"
        await cb.answer()
        return await cb.message.reply(f"📄 Current Custom Caption:\n{cap}")

    elif data == "set_thumb_menu":
        await cb.message.edit_caption(
            caption="🖼️ **Thumbnail Options:**\n\n📌 Send photo to set thumbnail or use below options.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🗑️ Remove Thumbnail", callback_data="set_remove_thumb")],
                [InlineKeyboardButton("🔙 Back", callback_data="settings_back")]
            ])
        )
        return await cb.answer()

    elif data == "set_remove_thumb":
        clear_thumbnail(uid)
        await cb.answer("✅ Thumbnail removed")
        return await cb.message.edit_caption(
            caption="⚙️ Customize your bot settings:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"📸 Screenshot: {'✅' if s.get('screenshot') else '❌'}", callback_data="set_toggle_ss")],
                [
                    InlineKeyboardButton("➖", callback_data="set_decrease_count"),
                    InlineKeyboardButton(f"🧮 Count: {s.get('count', 3)}", callback_data="noop"),
                    InlineKeyboardButton("➕", callback_data="set_increase_count")
                ],
                [
                    InlineKeyboardButton(f"📎 Prefix: {'✅' if s.get('prefix_enabled') else '❌'}", callback_data="set_toggle_prefix"),
                    InlineKeyboardButton(f"📄 Type: {s.get('rename_type')}", callback_data="set_toggle_type")
                ],
                [InlineKeyboardButton("🖼️ Thumbnail", callback_data="set_thumb_menu")],
                [
                    InlineKeyboardButton("🔤 Prefix Text", callback_data="set_show_prefix"),
                    InlineKeyboardButton("📄 Caption", callback_data="set_show_caption")
                ],
                [InlineKeyboardButton("❌ Close", callback_data="set_close")]
            ])
        )

    elif data == "settings_back":
        # Reuse updated settings and use edit_caption
        updated = get_settings(uid)
        count = updated.get("count", 3)
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"📸 Screenshot: {'✅' if updated.get('screenshot') else '❌'}", callback_data="set_toggle_ss")],
            [
                InlineKeyboardButton("➖", callback_data="set_decrease_count"),
                InlineKeyboardButton(f"🧮 Count: {count}", callback_data="noop"),
                InlineKeyboardButton("➕", callback_data="set_increase_count")
            ],
            [
                InlineKeyboardButton(f"📎 Prefix: {'✅' if updated.get('prefix_enabled') else '❌'}", callback_data="set_toggle_prefix"),
                InlineKeyboardButton(f"📄 Type: {updated.get('rename_type')}", callback_data="set_toggle_type")
            ],
            [InlineKeyboardButton("🖼️ Thumbnail", callback_data="set_thumb_menu")],
            [
                InlineKeyboardButton("🔤 Prefix Text", callback_data="set_show_prefix"),
                InlineKeyboardButton("📄 Caption", callback_data="set_show_caption")
            ],
            [InlineKeyboardButton("❌ Close", callback_data="set_close")]
        ])
        await cb.message.edit_caption("⚙️ Customize your bot settings:", reply_markup=markup)
        return await cb.answer()

    elif data == "set_close":
        try:
            await cb.message.delete()
        except:
            await cb.message.edit_caption("❌ Closed.")
        return await cb.answer()

    # Final fallback: refresh settings panel
    new_data = get_settings(uid)
    count = new_data.get("count", 3)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📸 Screenshot: {'✅' if new_data.get('screenshot') else '❌'}", callback_data="set_toggle_ss")],
        [
            InlineKeyboardButton("➖", callback_data="set_decrease_count"),
            InlineKeyboardButton(f"🧮 Count: {count}", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data="set_increase_count")
        ],
        [
            InlineKeyboardButton(f"📎 Prefix: {'✅' if new_data.get('prefix_enabled') else '❌'}", callback_data="set_toggle_prefix"),
            InlineKeyboardButton(f"📄 Type: {new_data.get('rename_type')}", callback_data="set_toggle_type")
        ],
        [InlineKeyboardButton("🖼️ Thumbnail", callback_data="set_thumb_menu")],
        [
            InlineKeyboardButton("🔤 Prefix Text", callback_data="set_show_prefix"),
            InlineKeyboardButton("📄 Caption", callback_data="set_show_caption")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="set_close")]
    ])
    await cb.message.edit_caption("⚙️ Customize your bot settings:", reply_markup=markup)
    await cb.answer()

    



"""
#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
@Client.on_message(filters.command("rename"))
async def rename_file(client, message: Message):
    user_id = message.from_user.id
    async with QUEUE:
        settings = get_settings(user_id)
        rename_type = settings.get("rename_type", "doc")
        prefix_on = settings.get("prefix_enabled", True)
        prefix_text = settings.get("prefix_text", "")
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
"""


#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
@Client.on_message(filters.command("rename"))
async def rename_file(client, message: Message):
    user_id = message.from_user.id
    async with QUEUE:
        settings = get_settings(user_id)
        rename_type = settings.get("rename_type", "doc")
        prefix_on = settings.get("prefix_enabled", True)
        prefix_text = settings.get("prefix_text", "")
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

        # Download original file temporarily
        file_path = await message.reply_to_message.download(
            file_name=os.path.join(DOWNLOAD_DIR, new_name),
            progress=progress_bar,
            progress_args=(task,)
        )
        await task["message"].edit("✅ Download complete.")

        caption = caption_custom.replace("{filename}", new_name) if caption_custom else f"📁 `{new_name}`"
        task = {
            "message": await message.reply("📤 Starting upload..."),
            "start_time": time.time(),
            "action": "📤 Uploading"
        }

        try:
            if rename_type == "video":
                sent_msg = await message.reply_video(
                    file_path, caption=caption, thumb=thumb_path,
                    progress=progress_bar, progress_args=(task,)
                )
            else:
                sent_msg = await message.reply_document(
                    file_path, caption=caption, thumb=thumb_path,
                    progress=progress_bar, progress_args=(task,)
                )
            await task["message"].edit("✅ Upload complete.")
        except Exception as e:
            await task["message"].edit(f"❌ Upload failed: {e}")
            return

        # ✅ Save only file_id (no local path)
        if sent_msg.document:
            file_id = sent_msg.document.file_id
        elif sent_msg.video:
            file_id = sent_msg.video.file_id
        else:
            file_id = None

        if file_id:
            save_file(user_id, new_name, file_id)

        # Screenshot support (still needs file_path, so keep temp file until done)
        if settings.get("screenshot") and new_name.lower().endswith((".mp4", ".mkv", ".mov")):
            ss_dir = f"ss_{user_id}"
            os.makedirs(ss_dir, exist_ok=True)
            for ss in take_screenshots(file_path, ss_dir, settings.get("count", 3)):
                await message.reply_photo(ss)
            cleanup(ss_dir)

        # Cleanup
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)
        if os.path.exists(file_path):  # remove local copy
            os.remove(file_path)

import shutil, os

def cleanup(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"Cleanup failed: {e}")

# Function to reuse for both /tasks and callbacks
def build_tasks_page(page: int = 1):
    all_tasks_data = get_all_user_tasks()
    all_tasks = []
    for entry in all_tasks_data:
        uid = entry["_id"]
        uname = f"@{entry.get('username', '')}" if entry.get("username") else f"ID:{uid}"
        for task in entry.get("tasks", []):
            all_tasks.append((uid, uname, task))

    total_tasks = len(all_tasks)
    if total_tasks == 0:
        return "❗ No tasks found for any users.", None

    per_page = 10
    total_pages = math.ceil(total_tasks / per_page)
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    paged_tasks = all_tasks[start:end]

    text = f"📋 **All Tasks (Page {page}/{total_pages}):**\n\n"
    for i, (uid, uname, task) in enumerate(paged_tasks, start=start + 1):
        text += f"{i}. {uname} - `{task}`\n\n"

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"tasks_page:{page-1}"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"tasks_page:{page+1}"))

    markup = InlineKeyboardMarkup([buttons]) if buttons else None
    return text, markup


@Client.on_message(filters.command("tasks"))
async def list_all_tasks(client, message):
    page = int(message.command[1]) if len(message.command) > 1 and message.command[1].isdigit() else 1
    text, markup = build_tasks_page(page)
    await message.reply(text, reply_markup=markup)


@Client.on_callback_query(filters.regex(r"^tasks_page:(\d+)$"))
async def paginate_tasks(client, callback_query: CallbackQuery):
    page = int(callback_query.data.split(":")[1])
    text, markup = build_tasks_page(page)
    await callback_query.message.edit_text(text, reply_markup=markup)
    await callback_query.answer()  # removes the "loading..." animation

"""
# ------------------- GET FILE (SELF OR OTHERS) -------------------
@Client.on_message(filters.command("getfile"))
async def get_file(client, message: Message):
    parts = message.command
    if len(parts) < 2:
        return await message.reply(
            "❗ Usage:\n"
            "`/getfile <filename>` (your files)\n"
            "`/getfile <user_id> <filename>` (other user's files)",
            quote=True
        )

    if len(parts) >= 3 and parts[1].isdigit():
        uid = int(parts[1])
        raw_input = " ".join(parts[2:])
    else:
        uid = message.from_user.id
        raw_input = " ".join(parts[1:])

    status_msg = await message.reply("⏳ Searching files, please wait…", quote=True)
    filename = re.sub(r"^@\w+\s*[-:]\s*", "", raw_input).strip().lower()

    files = get_user_files(uid)
    if not files:
        await status_msg.delete()
        return await message.reply("❗ No files found for that user.", quote=True)

    match = next((f["path"] for f in files if filename in f["name"].lower()), None)

    if match:
        if os.path.exists(match):
            await status_msg.edit_text("✅ File found! Uploading now…")
            sent_msg = await message.reply_document(match, caption=f"📂 File from `{uid}`")
            await status_msg.edit_text("📤 Upload completed successfully!")
            return sent_msg
        else:
            await status_msg.delete()
            return await message.reply(f"⚠️ File entry found but missing on disk:\n`{match}`", quote=True)

    await status_msg.delete()
    return await message.reply(
        f"❗ File not found.\n\n🔎 You entered:\n`{filename}`\n\n📂 Available files:\n" +
        "\n".join([f"`{f['name']}`" for f in files]),
        quote=True
    )
"""
# ─── Get File Command ─────────────────────────────────────────────────────────
@Client.on_message(filters.command("getfile"))
async def get_file(client, message: Message):
    parts = message.command
    if len(parts) < 2:
        return await message.reply(
            "❗ Usage:\n"
            "`/getfile <filename>` (your files)\n"
            "`/getfile <user_id> <filename>` (other user's files)",
            quote=True
        )

    if len(parts) >= 3 and parts[1].isdigit():
        uid = int(parts[1])
        filename = " ".join(parts[2:])
    else:
        uid = message.from_user.id
        filename = " ".join(parts[1:])

    status_msg = await message.reply("⏳ Searching files, please wait…", quote=True)
    filename = filename.strip().lower()

    files = get_user_files(uid)
    if not files:
        await status_msg.delete()
        return await message.reply("❗ No files found for that user.", quote=True)

    match = next((f for f in files if filename in f["name"].lower()), None)

    if match:
        await status_msg.edit_text("✅ File found! Uploading now…")
        sent_msg = await message.reply_document(
            match["file_id"],
            caption=f"📂 File from `{uid}`\n**Name:** `{match['name']}`"
        )
        await status_msg.edit_text("📤 Upload completed successfully!")
        return sent_msg

    await status_msg.delete()
    return await message.reply(
        f"❗ File not found.\n\n🔎 You entered:\n`{filename}`\n\n📂 Available files:\n" +
        "\n".join([f"`{f['name']}`" for f in files]),
        quote=True
    )
    

# ------------------- REMOVE TASK (ADMIN ONLY) -------------------
@Client.on_message(filters.command("removetask") & filters.user(ADMIN))
async def remove_user_task_cmd(client, message: Message):
    if len(message.command) < 3:
        return await message.reply("❗ Usage: /removetask <user_id> <task_index>")
    try:
        target_id = int(message.command[1])
        index = int(message.command[2]) - 1
        if remove_task(target_id, index):
            await message.reply(f"✅ Task {index + 1} removed for user {target_id}.")
        else:
            await message.reply("❗ Invalid task index.")
    except ValueError:
        await message.reply("❗ Invalid user ID or index.")

        
@Client.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    user_id = message.from_user.id
    file_id = message.photo.file_id
    set_thumbnail(user_id, file_id)
    await message.reply_photo(file_id, caption="✅ Thumbnail saved.")
    await start(client, message)


@Client.on_message(filters.command("setprefix"))
async def set_prefix_command(client, message):
    uid = message.from_user.id
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /setprefix <text>")
    prefix = message.text.split(None, 1)[1].strip()
    update_settings(uid, "prefix_text", prefix)
    await message.reply(f"✅ Prefix updated to:\n{prefix}")

@Client.on_message(filters.command("setcaption"))
async def set_caption_command(client, message):
    uid = message.from_user.id
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /setcaption <text>")
    cap = message.text.split(None, 1)[1].strip()
    update_caption(uid, cap)
    await message.reply("✅ Custom caption updated!")



@Client.on_message(filters.command("clear") & filters.user(ADMIN))
async def clear_database_handler(client: Client, msg: Message):
    try:
        clear_database()  # ✅ Call the imported function directly
        await msg.reply_text("Old database collections have been cleared ✅.")
    except Exception as e:
        await msg.reply_text(f"An error occurred: {e}")

 #renamelink
import aiohttp
import urllib.parse
import re
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message

MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB


@Client.on_message(filters.command("renamelink"))
async def rename_link(client, message: Message):
    user_id = message.from_user.id
    async with QUEUE:
        settings = get_settings(user_id)
        rename_type = settings.get("rename_type", "doc")
        prefix_on = settings.get("prefix_enabled", True)
        prefix_text = settings.get("prefix_text", "")
        caption_custom = get_caption(user_id)

        if len(message.command) < 3:
            return await message.reply("❗ Usage: `/renamelink <newname> <link>`")

        # Extract the URL from the message text
        match = re.search(r'(https?://\S+)', message.text)
        if not match:
            return await message.reply("❌ No valid URL found.")

        link = match.group(1).strip()

        # The new name is whatever is left after removing the command and the URL
        new_name = message.text.replace(f"/renamelink", "").replace(link, "").strip()

        # Fix link by encoding spaces and special characters
        link = urllib.parse.quote(link, safe=":/?&=%@[]+!$&'()*+,;")

        # Validate link
        if not ("seedr.cc" in link or "workers.dev" in link):
            return await message.reply("❌ Link must be Seedr or Workers link.")

        # Check file size
        async with aiohttp.ClientSession() as session:
            async with session.head(link) as resp:
                size = int(resp.headers.get("Content-Length", 0))
                if size == 0:
                    return await message.reply("❌ Could not determine file size.")
                if size > MAX_SIZE:
                    return await message.reply("❌ File is larger than 2GB. Not allowed.")

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

        # Download file
        task = {
            "message": await message.reply("📥 Starting download..."),
            "start_time": time.time(),
            "action": "📥 Downloading"
        }

        file_path = os.path.join(DOWNLOAD_DIR, new_name)
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                total_size = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                with open(file_path, "wb") as f:
                    async for chunk in resp.content.iter_chunked(1024 * 1024):
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress_bar(downloaded, total_size, task)
        await task["message"].edit("✅ Download complete.")

        # Caption
        caption = caption_custom.replace("{filename}", new_name) if caption_custom else f"📁 `{new_name}`"

        # Upload
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

        # Screenshots for videos
        if settings.get("screenshot") and new_name.lower().endswith((".mp4", ".mkv", ".mov")):
            ss_dir = f"ss_{user_id}"
            os.makedirs(ss_dir, exist_ok=True)
            for ss in take_screenshots(file_path, ss_dir, settings.get("count", 3)):
                await message.reply_photo(ss)
            cleanup(ss_dir)

        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)


if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
