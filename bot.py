import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import (
    get_settings, update_settings, set_thumbnail, get_thumbnail, clear_thumbnail,
    update_caption, get_caption, get_admins, is_admin_user,
    add_task, get_user_tasks, remove_task, save_file, get_saved_file, get_user_files
)
from utils import progress_bar, take_screenshots, cleanup

API_ID = 10811400
API_HASH = "191bf5ae7a6c39771e7b13cf4ffd1279"
BOT_TOKEN = "7097361755:AAHUd9LI4_JoAj57WfGbYVhG0msao8d04ck"
ADMIN = 6469754522

app = Client("RenameBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
QUEUE = asyncio.Semaphore(4)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("\U0001F44B Welcome to Rename Bot!\nUse /rename <newname> by replying to a file.")



@app.on_message(filters.command("rename"))
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


@app.on_message(filters.command("getfile"))
async def get_file(client: Client, message: Message):
    uid = message.from_user.id

    if len(message.command) < 2:
        return await message.reply("❗ Usage: /getfile <filename>")

    filename = message.text.split(None, 1)[1].strip().lower()
    files = get_user_files(uid)

    match = next((f["path"] for f in files if filename in f["name"].lower()), None)

    if match and os.path.exists(match):
        wait_msg = await message.reply("📤 Uploading your file, please wait...")
        try:
            await client.send_document(chat_id=message.chat.id, document=match)
            await wait_msg.delete()  # Remove the waiting message after successful send
        except Exception as e:
            await wait_msg.edit(f"❗ Failed to send file:\n`{e}`")
    else:
        await message.reply("❗ File not found or already deleted.")
        
@app.on_message(filters.command("tasks"))
async def list_tasks(client, message):
    user = message.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else f"ID: {user.id}"

    page = int(message.command[1]) if len(message.command) > 1 and message.command[1].isdigit() else 1
    tasks = get_user_tasks(user_id)
    items_per_page = 5
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paged_tasks = tasks[start:end]

    if not paged_tasks:
        return await message.reply("❗ No tasks found on this page.")

    text = f"📋 **Your Tasks ({username}):**\n\n"
    for i, task in enumerate(paged_tasks, start=start + 1):
        text += f"{i}. `{task}`\n\n"  # <-- DOUBLE NEWLINE for spacing

    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"task_page:{page - 1}"))
    if end < len(tasks):
        buttons.append(InlineKeyboardButton("➡️ Next", callback_data=f"task_page:{page + 1}"))

    if buttons:
        await message.reply(text, reply_markup=InlineKeyboardMarkup([buttons]))
    else:
        await message.reply(text)



@app.on_message(filters.command("removetask") & filters.user(ADMIN))
async def remove_user_task(client, message):
    if len(message.command) < 3:
        return await message.reply("❗ Usage: /removetask <user_id> <task_index>")
    try:
        user_id = int(message.command[1])
        index = int(message.command[2]) - 1
        if remove_task(user_id, index):
            await message.reply(f"✅ Task {index + 1} removed for user {user_id}.")
        else:
            await message.reply("❗ Invalid task index.")
    except Exception as e:
        await message.reply(f"❗ Error: {e}")

@app.on_message(filters.command("settings"))
async def setting(client, message):
    user_id = message.from_user.id
    s = get_settings(user_id)
    count = s.get("count", 3)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📸 Screenshot: {'✅' if s.get('screenshot') else '❌'}", callback_data="toggle_ss")],
        [
            InlineKeyboardButton("➖", callback_data="decrease_count"),
            InlineKeyboardButton(f"🧮 Count: {count}", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data="increase_count")
        ],
        [
            InlineKeyboardButton(f"📎 Prefix: {'✅' if s.get('prefix_enabled') else '❌'}", callback_data="toggle_prefix"),
            InlineKeyboardButton(f"📄 Type: {s.get('rename_type')}", callback_data="toggle_type")
        ],
        [InlineKeyboardButton("🖼️ Thumbnail", callback_data="thumb_menu")],
        [
            InlineKeyboardButton("🔤 Prefix Text", callback_data="show_prefix"),
            InlineKeyboardButton("📄 Caption", callback_data="show_caption")
        ]
    ])
    await message.reply("⚙️ Customize your bot settings:\u200b", reply_markup=markup)

"""
@app.on_message(filters.command("settings"))
async def setting(client, message):
    user_id = message.from_user.id
    s = get_settings(user_id)
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"📸 Screenshot: {'✅' if s.get('screenshot') else '❌'}", callback_data="toggle_ss"),
            InlineKeyboardButton(f"🧮 Count: {s.get('count')}", callback_data="noop")
        ],
        [
            InlineKeyboardButton(f"📎 Prefix: {'✅' if s.get('prefix_enabled') else '❌'}", callback_data="toggle_prefix"),
            InlineKeyboardButton(f"📄 Type: {s.get('rename_type')}", callback_data="toggle_type")
        ],
        [
            InlineKeyboardButton("🖼️ Thumbnail", callback_data="thumb_menu")
        ],
        [
            InlineKeyboardButton("🔤 Prefix Text", callback_data="show_prefix"),
            InlineKeyboardButton("📄 Caption", callback_data="show_caption")
        ]
    ])
    await message.reply("⚙️ Customize your bot settings:", reply_markup=markup)
"""
        
@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    user_id = message.from_user.id
    file_id = message.photo.file_id
    set_thumbnail(user_id, file_id)
    await message.reply_photo(file_id, caption="✅ Thumbnail saved.")
    await start(client, message)


@app.on_message(filters.command("setprefix"))
async def set_prefix_command(client, message):
    uid = message.from_user.id
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /setprefix <text>")
    prefix = message.text.split(None, 1)[1].strip()
    update_settings(uid, "prefix_text", prefix)
    await message.reply(f"✅ Prefix updated to:\n{prefix}")

@app.on_message(filters.command("setcaption"))
async def set_caption_command(client, message):
    uid = message.from_user.id
    if len(message.command) < 2:
        return await message.reply("❗ Usage: /setcaption <text>")
    cap = message.text.split(None, 1)[1].strip()
    update_caption(uid, cap)
    await message.reply("✅ Custom caption updated!")

@app.on_callback_query()
async def cb_settings(client, cb):
    uid = cb.from_user.id
    data = get_settings(uid)

    # Logic toggles
    if cb.data == "toggle_ss":
        update_settings(uid, "screenshot", not data.get("screenshot", False))
    elif cb.data == "toggle_prefix":
        update_settings(uid, "prefix_enabled", not data.get("prefix_enabled", True))
    elif cb.data == "toggle_type":
        new_type = "video" if data.get("rename_type") == "doc" else "doc"
        update_settings(uid, "rename_type", new_type)
    elif cb.data == "increase_count":
        current = data.get("count", 3)
        if current < 20:
            update_settings(uid, "count", current + 1)
    elif cb.data == "decrease_count":
        current = data.get("count", 3)
        if current > 1:
            update_settings(uid, "count", current - 1)
    elif cb.data == "show_prefix":
        await cb.answer()
        return await cb.message.reply(f"📎 Current Prefix:\n{data.get('prefix_text', '-')}")
    elif cb.data == "show_caption":
        cap = get_caption(uid) or "None"
        await cb.answer()
        return await cb.message.reply(f"📄 Current Custom Caption:\n{cap}")
    elif cb.data == "thumb_menu":
        await cb.message.edit("🖼️ Thumbnail Options:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Send Photo to Set", callback_data="noop")],
            [InlineKeyboardButton("🗑️ Remove Thumbnail", callback_data="remove_thumb")]
        ]))
        return await cb.answer()
    elif cb.data == "remove_thumb":
        clear_thumbnail(uid)
        await cb.answer("✅ Thumbnail removed")
        return await start(client, cb.message)

    # Refresh settings panel
    new_data = get_settings(uid)
    count = new_data.get("count", 3)
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📸 Screenshot: {'✅' if new_data.get('screenshot') else '❌'}", callback_data="toggle_ss")],
        [
            InlineKeyboardButton("➖", callback_data="decrease_count"),
            InlineKeyboardButton(f"🧮 Count: {count}", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data="increase_count")
        ],
        [
            InlineKeyboardButton(f"📎 Prefix: {'✅' if new_data.get('prefix_enabled') else '❌'}", callback_data="toggle_prefix"),
            InlineKeyboardButton(f"📄 Type: {new_data.get('rename_type')}", callback_data="toggle_type")
        ],
        [InlineKeyboardButton("🖼️ Thumbnail", callback_data="thumb_menu")],
        [
            InlineKeyboardButton("🔤 Prefix Text", callback_data="show_prefix"),
            InlineKeyboardButton("📄 Caption", callback_data="show_caption")
        ]
    ])
    try:
        await cb.message.edit("⚙️ Customize your bot settings:\u200b", reply_markup=markup)
        await cb.answer()
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" in str(e):
            await cb.answer("⚠️ No changes to update.")
        else:
            print("[Edit Error]", e)

"""
@app.on_callback_query()
async def cb_settings(client, cb):
    uid = cb.from_user.id
    data = get_settings(uid)

    if cb.data == "toggle_ss":
        update_settings(uid, "screenshot", not data.get("screenshot", False))
    elif cb.data == "toggle_prefix":
        update_settings(uid, "prefix_enabled", not data.get("prefix_enabled", True))
    elif cb.data == "toggle_type":
        new_type = "video" if data.get("rename_type") == "doc" else "doc"
        update_settings(uid, "rename_type", new_type)
    elif cb.data == "show_prefix":
        await cb.answer()
        return await cb.message.reply(f"📎 Current Prefix:\n{data.get('prefix_text', '-')}")
    elif cb.data == "show_caption":
        cap = get_caption(uid) or "None"
        await cb.answer()
        return await cb.message.reply(f"📄 Current Custom Caption:\n{cap}")
    elif cb.data == "thumb_menu":
        await cb.message.edit("🖼️ Thumbnail Options:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Send Photo to Set", callback_data="noop")],
            [InlineKeyboardButton("🗑️ Remove Thumbnail", callback_data="remove_thumb")]
        ]))
        return await cb.answer()
    elif cb.data == "remove_thumb":
        clear_thumbnail(uid)
        await cb.answer("✅ Thumbnail removed")
        return await start(client, cb.message)

    try:
        new_data = get_settings(uid)
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(f"📸 Screenshot: {'✅' if new_data.get('screenshot') else '❌'}", callback_data="toggle_ss"),
                InlineKeyboardButton(f"🧮 Count: {new_data.get('count')}", callback_data="noop")
            ],
            [
                InlineKeyboardButton(f"📎 Prefix: {'✅' if new_data.get('prefix_enabled') else '❌'}", callback_data="toggle_prefix"),
                InlineKeyboardButton(f"📄 Type: {new_data.get('rename_type')}", callback_data="toggle_type")
            ],
            [
                InlineKeyboardButton("🖼️ Thumbnail", callback_data="thumb_menu")
            ],
            [
                InlineKeyboardButton("🔤 Prefix Text", callback_data="show_prefix"),
                InlineKeyboardButton("📄 Caption", callback_data="show_caption")
            ]
        ])
        await cb.message.edit("⚙️ Customize your bot settings:", reply_markup=markup)
        await cb.answer()
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" in str(e):
            await cb.answer("⚠️ No changes to update.")
        else:
            print("[Edit Error]", e)
"""
app.run()
