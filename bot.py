import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import get_settings, update_settings
from utils import progress_bar, take_screenshots, cleanup

# 🧠 Bot Configuration
BOT_TOKEN = "7097361755:AAHUd9LI4_JoAj57WfGbYVhG0msao8d04ck"
API_ID = 10811400
API_HASH = "191bf5ae7a6c39771e7b13cf4ffd1279"

app = Client("RenameBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# ⚙️ Start Command – User Settings UI
@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    s = get_settings(user_id)
    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Screenshot: {'✅ ON' if s.get('screenshot') else '❌ OFF'}", callback_data="toggle_ss")],
        [InlineKeyboardButton("➕ Count", callback_data="inc_count"),
         InlineKeyboardButton("➖ Count", callback_data="dec_count")],
        [InlineKeyboardButton(f"Current Count: {s.get('count', 3)}", callback_data="noop")]
    ])
    await message.reply("⚙️ Bot Settings", reply_markup=btns)

# 🔘 Settings Buttons
@app.on_callback_query()
async def cb_settings(client, cb):
    user_id = cb.from_user.id
    data = get_settings(user_id)

    if cb.data == "toggle_ss":
        update_settings(user_id, "screenshot", not data.get("screenshot", False))
    elif cb.data == "inc_count":
        update_settings(user_id, "count", min(10, data.get("count", 3) + 1))
    elif cb.data == "dec_count":
        update_settings(user_id, "count", max(1, data.get("count", 3) - 1))

    data = get_settings(user_id)
    btns = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Screenshot: {'✅ ON' if data.get('screenshot') else '❌ OFF'}", callback_data="toggle_ss")],
        [InlineKeyboardButton("➕ Count", callback_data="inc_count"),
         InlineKeyboardButton("➖ Count", callback_data="dec_count")],
        [InlineKeyboardButton(f"Current Count: {data.get('count', 3)}", callback_data="noop")]
    ])
    await cb.message.edit("⚙️ Updated Settings", reply_markup=btns)
    await cb.answer()

# ✏️ /rename Handler
@app.on_message(filters.command("rename"))
async def rename_file(client, message: Message):
    user_id = message.from_user.id
    settings = get_settings(user_id)

    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("❗Reply to a file to rename.")

    if len(message.command) < 2:
        return await message.reply("❗Provide new name: `/rename newname.ext`")

    new_name = message.text.split(None, 1)[1]
    doc_msg = message.reply_to_message

    # ⏳ Start Download
    status = await message.reply("📥 Starting download...")
    task = {"message": status, "start_time": time.time(), "action": "📥 Downloading"}
    file_path = await doc_msg.download(file_name=new_name, progress=progress_bar, progress_args=(task,))
    result = f"✅ Renamed to `{new_name}`"

    # 🎞️ Screenshots if enabled and is video
    if settings.get('screenshot') and new_name.lower().endswith(('.mp4', '.mkv', '.mov', '.webm')):
        ss_dir = f"ss_{user_id}"
        os.makedirs(ss_dir, exist_ok=True)
        ss_list = take_screenshots(file_path, ss_dir, settings.get('count', 3))
        for ss in ss_list:
            if os.path.exists(ss):
                try:
                    await message.reply_photo(ss)
                except Exception as e:
                    await message.reply(f"❗ Failed to send screenshot: {e}")
        cleanup(ss_dir)
        result += f"\n📸 {len(ss_list)} screenshots attached."

    # 📤 Upload File
    status = await message.reply("📤 Starting upload...")
    task = {"message": status, "start_time": time.time(), "action": "📤 Uploading"}
    await message.reply_document(file_path, caption=result, progress=progress_bar, progress_args=(task,))
    cleanup(file_path)

app.run()
