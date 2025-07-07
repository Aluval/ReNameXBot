
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import get_settings, update_settings, set_thumbnail, get_thumbnail, clear_thumbnail
from utils import progress_bar, take_screenshots, cleanup, caption_styles

API_ID = 10811400
API_HASH = "191bf5ae7a6c39771e7b13cf4ffd1279"
BOT_TOKEN = "7097361755:AAHUd9LI4_JoAj57WfGbYVhG0msao8d04ck"

app = Client("RenameBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ Unified settings menu
async def show_settings(client, message_or_cb):
    user_id = message_or_cb.from_user.id
    s = get_settings(user_id)
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"📸 Screenshot: {'✅' if s.get('screenshot') else '❌'}", callback_data="toggle_ss"),
            InlineKeyboardButton(f"🔢 Count: {s.get('count')}", callback_data="noop")
        ],
        [
            InlineKeyboardButton("➕", callback_data="inc_count"),
            InlineKeyboardButton("➖", callback_data="dec_count")
        ],
        [
            InlineKeyboardButton(f"📛 Prefix: {'✅' if s.get('prefix_enabled') else '❌'}", callback_data="toggle_prefix"),
            InlineKeyboardButton(f"📂 Type: {s.get('rename_type')}", callback_data="toggle_type")
        ],
        [
            InlineKeyboardButton("🎨 Style", callback_data="style_menu"),
            InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb_menu")
        ],
        [
            InlineKeyboardButton("🔍 Prefix View", callback_data="show_prefix")
        ]
    ])
    try:
        if hasattr(message_or_cb, 'edit_text'):
            await message_or_cb.edit_text("⚙️ Customize your bot settings:", reply_markup=markup)
        else:
            await message_or_cb.reply("⚙️ Customize your bot settings:", reply_markup=markup)
    except Exception as e:
        print(f"[UI Error] {e}")

@app.on_message(filters.command("start"))
async def start(client, message):
    await show_settings(client, message)

@app.on_callback_query()
async def handle_cb(client, cb):
    user_id = cb.from_user.id
    data = get_settings(user_id)

    if cb.data == "toggle_ss":
        update_settings(user_id, "screenshot", not data.get("screenshot", False))

    elif cb.data == "inc_count":
        update_settings(user_id, "count", min(10, data.get("count", 3) + 1))
        await cb.message.reply("🔧 Made by Sunrises 24 Bots", quote=True)

    elif cb.data == "dec_count":
        update_settings(user_id, "count", max(1, data.get("count", 3) - 1))

    elif cb.data == "toggle_prefix":
        update_settings(user_id, "prefix_enabled", not data.get("prefix_enabled", True))

    elif cb.data == "toggle_type":
        update_settings(user_id, "rename_type", "video" if data.get("rename_type") == "doc" else "doc")

    elif cb.data == "show_prefix":
        await cb.answer()
        return await cb.message.reply(f"📛 Current Prefix:\n`{data.get('prefix_text')}`", quote=True)

    elif cb.data == "thumb_menu":
        await cb.message.edit("🖼 Thumbnail Options:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Send Photo to Set", callback_data="noop")],
            [InlineKeyboardButton("🗑 Remove Thumbnail", callback_data="remove_thumb")]
        ]))
        await cb.answer()
        return

    elif cb.data == "remove_thumb":
        clear_thumbnail(user_id)
        await cb.answer("✅ Removed thumbnail")
        return

    elif cb.data == "style_menu":
        styles = ["bold", "italic", "code", "mono", "plain"]
        buttons = [InlineKeyboardButton(f"{'✅' if data.get('caption_style') == s else ''} {s.title()}", callback_data=f"set_style:{s}") for s in styles]
        await cb.message.edit("🎨 Choose Style:", reply_markup=InlineKeyboardMarkup([buttons[i:i+2] for i in range(0, len(buttons), 2)]))
        await cb.answer()
        return

    elif cb.data.startswith("set_style:"):
        _, style = cb.data.split(":")
        update_settings(user_id, "caption_style", style)
        await show_settings(client, cb)
        return

    await show_settings(client, cb)
    await cb.answer()

# 📸 Save thumbnail
@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    set_thumbnail(message.from_user.id, message.photo.file_id)
    await message.reply("✅ Thumbnail saved.")

# 🔁 /prefix command to view
@app.on_message(filters.command("prefix"))
async def show_prefix_cmd(client, message):
    prefix = get_settings(message.from_user.id).get("prefix_text", "@sunriseseditsoffical6 -")
    await message.reply(f"📛 Current prefix:\n`{prefix}`", quote=True)

# ✏️ /rename handler
@app.on_message(filters.command("rename"))
async def rename_file(client, message: Message):
    user_id = message.from_user.id
    s = get_settings(user_id)

    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("❗ Reply to a file to rename it.")

    if len(message.command) < 2:
        return await message.reply("❗ Provide a new filename: `/rename newname.ext`")

    new_name = message.text.split(None, 1)[1]
    if s.get("prefix_enabled"):
        new_name = f"{s.get('prefix_text')} {new_name}"

    # 🔽 Download
    task = {"message": await message.reply("📥 Downloading..."), "start_time": time.time(), "action": "📥 Downloading"}
    file_path = await message.reply_to_message.download(file_name=new_name, progress=progress_bar, progress_args=(task,))

    cap = caption_styles(s.get("caption_style", "bold"), f"✅ File: `{new_name}`")
    task = {"message": await message.reply("📤 Uploading..."), "start_time": time.time(), "action": "📤 Uploading"}

    try:
        if s.get("rename_type") == "video":
            await message.reply_video(file_path, caption=cap, thumb=get_thumbnail(user_id), progress=progress_bar, progress_args=(task,))
        else:
            await message.reply_document(file_path, caption=cap, thumb=get_thumbnail(user_id), progress=progress_bar, progress_args=(task,))
    except Exception as e:
        await message.reply(f"❗ Upload failed: `{e}`")
        return

    # 📸 Screenshots
    if s.get("screenshot") and new_name.lower().endswith((".mp4", ".mkv", ".mov", ".webm")):
        ss_dir = f"ss_{user_id}"
        os.makedirs(ss_dir, exist_ok=True)
        ss_list = take_screenshots(file_path, ss_dir, s.get("count", 3))
        for ss in ss_list:
            if os.path.exists(ss):
                try:
                    await message.reply_photo(ss)
                except Exception as e:
                    await message.reply(f"❗ Screenshot error: {e}")
        cleanup(ss_dir)

    cleanup(file_path)

app.run()
