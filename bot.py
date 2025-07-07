import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import get_settings, update_settings, set_thumbnail, get_thumbnail, clear_thumbnail
from utils import progress_bar, take_screenshots, cleanup, caption_styles

# 🧠 Bot Configuration
API_ID = 10811400
API_HASH = "191bf5ae7a6c39771e7b13cf4ffd1279"
BOT_TOKEN = "7097361755:AAHUd9LI4_JoAj57WfGbYVhG0msao8d04ck"

app = Client("RenameBot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)


# ⚙️ Start Command – User Settings
@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    s = get_settings(user_id)
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"📸 Screenshot: {'✅' if s.get('screenshot') else '❌'}", callback_data="toggle_ss"),
            InlineKeyboardButton(f"🧮 Count: {s.get('count', 3)}", callback_data="noop")
        ],
        [
            InlineKeyboardButton("➕", callback_data="inc_count"),
            InlineKeyboardButton("➖", callback_data="dec_count")
        ],
        [
            InlineKeyboardButton(f"🏷 Prefix: {'✅' if s.get('prefix_enabled') else '❌'}", callback_data="toggle_prefix"),
            InlineKeyboardButton(f"📦 Type: {s.get('rename_type')}", callback_data="toggle_type")
        ],
        [
            InlineKeyboardButton("🎨 Style", callback_data="style_menu"),
            InlineKeyboardButton("🖼️ Thumbnail", callback_data="thumb_menu")
        ]
    ])
    await message.reply("⚙️ Customize your bot settings:", reply_markup=markup)


# 🧩 Callback Button Settings
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
    elif cb.data == "toggle_prefix":
        update_settings(user_id, "prefix_enabled", not data.get("prefix_enabled", True))
    elif cb.data == "toggle_type":
        new_type = "video" if data.get("rename_type") == "doc" else "doc"
        update_settings(user_id, "rename_type", new_type)
    elif cb.data == "style_menu":
        styles = ["bold", "italic", "code", "mono", "plain"]
        buttons = [InlineKeyboardButton(st, callback_data=f"set_style:{st}") for st in styles]
        await cb.message.edit("🎨 Choose Caption Style:", reply_markup=InlineKeyboardMarkup([buttons[i:i+2] for i in range(0, len(buttons), 2)]))
        await cb.answer()
        return
    elif cb.data.startswith("set_style"):
        _, style = cb.data.split(":")
        update_settings(user_id, "caption_style", style)
        await cb.message.delete()
        return
    elif cb.data == "thumb_menu":
        btns = [
            [InlineKeyboardButton("📌 Set Thumb (send photo)", callback_data="noop")],
            [InlineKeyboardButton("🗑️ Remove Thumbnail", callback_data="remove_thumb")]
        ]
        await cb.message.edit("🖼️ Thumbnail Options:", reply_markup=InlineKeyboardMarkup(btns))
        await cb.answer()
        return
    elif cb.data == "remove_thumb":
        clear_thumbnail(user_id)

    await start(client, cb.message)
    await cb.answer()


# 📸 Set Thumbnail
@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    user_id = message.from_user.id
    set_thumbnail(user_id, message.photo.file_id)
    await message.reply("✅ Thumbnail saved!")


# ✏️ Rename File
@app.on_message(filters.command("rename"))
async def rename_file(client, message: Message):
    user_id = message.from_user.id
    settings = get_settings(user_id)
    rename_type = settings.get("rename_type", "doc")
    prefix_enabled = settings.get("prefix_enabled", True)
    prefix_text = settings.get("prefix_text", "@sunriseseditsoffical6 -")
    style = settings.get("caption_style", "bold")
    thumb_id = get_thumbnail(user_id)

    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("❗ Reply to a file to rename it.")
    
    if len(message.command) < 2:
        return await message.reply("❗ Usage: `/rename newname.ext`")

    new_name = message.text.split(None, 1)[1]
    if prefix_enabled:
        new_name = f"{prefix_text} {new_name}"

    task = {"message": await message.reply("📥 Starting download..."), "start_time": time.time(), "action": "📥 Downloading"}
    file_path = await message.reply_to_message.download(file_name=new_name, progress=progress_bar, progress_args=(task,))

    caption = caption_styles(style, f"✅ File: `{new_name}`")

    task = {"message": await message.reply("📤 Uploading..."), "start_time": time.time(), "action": "📤 Uploading"}
    try:
        if rename_type == "video":
            await message.reply_video(file_path, caption=caption, thumb=thumb_id, progress=progress_bar, progress_args=(task,))
        else:
            await message.reply_document(file_path, caption=caption, thumb=thumb_id, progress=progress_bar, progress_args=(task,))
    except Exception as e:
        await message.reply(f"❗ Upload failed: `{e}`")

    if settings.get("screenshot") and new_name.lower().endswith((".mp4", ".mkv", ".mov", ".webm")):
        ss_dir = f"ss_{user_id}"
        os.makedirs(ss_dir, exist_ok=True)
        ss = take_screenshots(file_path, ss_dir, settings.get("count", 3))
        for s in ss:
            await message.reply_photo(s)
        cleanup(ss_dir)

    cleanup(file_path)


# 📝 Set custom prefix command
@app.on_message(filters.command("prefix"))
async def custom_prefix(client, message: Message):
    user_id = message.from_user.id
    if len(message.command) == 1:
        prefix = get_settings(user_id).get("prefix_text", "@sunriseseditsoffical6 -")
        return await message.reply(f"Current prefix:\n`{prefix}`\nUse `/prefix NewPrefix:` to change.")
    
    prefix_text = message.text.split(None, 1)[1]
    if prefix_text.lower() == "reset":
        prefix_text = "@sunriseseditsoffical6 -"

    if not prefix_text.endswith(":"):
        return await message.reply("❗ Prefix must end with `:` (e.g., `/prefix MyBot:`)")

    update_settings(user_id, "prefix_text", prefix_text.strip())
    await message.reply(f"✅ Prefix updated:\n`{prefix_text.strip()}`")


app.run()
