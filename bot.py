import os
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from db import get_settings, update_settings, set_thumbnail, get_thumbnail, clear_thumbnail
from utils import progress_bar, take_screenshots, caption_styles, cleanup

API_ID = 10811400
API_HASH = "191bf5ae7a6c39771e7b13cf4ffd1279"
BOT_TOKEN = "7097361755:AAHUd9LI4_JoAj57WfGbYVhG0msao8d04ck"

app = Client("RenameBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    s = get_settings(user_id)
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"Screenshot: {'✅' if s['screenshot'] else '❌'}", callback_data="toggle_ss"),
            InlineKeyboardButton(f"Count: {s['count']}", callback_data="noop")
        ],
        [
            InlineKeyboardButton("➕", callback_data="inc_count"),
            InlineKeyboardButton("➖", callback_data="dec_count")
        ],
        [
            InlineKeyboardButton(f"Prefix: {'✅' if s['prefix_enabled'] else '❌'}", callback_data="toggle_prefix"),
            InlineKeyboardButton("✏️ View Prefix", callback_data="view_prefix") if s['prefix_enabled'] else InlineKeyboardButton("—", callback_data="noop")
        ],
        [
            InlineKeyboardButton(f"Type: {s['rename_type']}", callback_data="toggle_type"),
            InlineKeyboardButton("Style", callback_data="style_menu")
        ],
        [
            InlineKeyboardButton("Thumbnail", callback_data="thumb_menu")
        ]
    ])
    await message.reply("⚙️ Customize your bot settings:", reply_markup=markup)

@app.on_callback_query()
async def cb_handler(client, cb):
    user_id = cb.from_user.id
    s = get_settings(user_id)

    if cb.data == "toggle_ss":
        update_settings(user_id, "screenshot", not s["screenshot"])
    elif cb.data == "inc_count":
        update_settings(user_id, "count", min(10, s["count"] + 1))
    elif cb.data == "dec_count":
        update_settings(user_id, "count", max(1, s["count"] - 1))
    elif cb.data == "toggle_prefix":
        update_settings(user_id, "prefix_enabled", not s["prefix_enabled"])
    elif cb.data == "toggle_type":
        new_type = "video" if s["rename_type"] == "doc" else "doc"
        update_settings(user_id, "rename_type", new_type)
    elif cb.data == "style_menu":
        styles = ["bold", "italic", "mono", "code", "plain"]
        style_buttons = [InlineKeyboardButton(st, callback_data=f"set_style:{st}") for st in styles]
        markup = InlineKeyboardMarkup([style_buttons[i:i + 2] for i in range(0, len(style_buttons), 2)])
        await cb.message.edit("🎨 Choose caption style:", reply_markup=markup)
        return
    elif cb.data.startswith("set_style:"):
        _, style = cb.data.split(":")
        update_settings(user_id, "caption_style", style)
        await cb.message.delete()
        return
    elif cb.data == "thumb_menu":
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📌 Set Thumbnail (send photo)", callback_data="noop")],
            [InlineKeyboardButton("🗑️ Remove Thumbnail", callback_data="remove_thumb")]
        ])
        await cb.message.edit("🖼️ Thumbnail Settings:", reply_markup=markup)
        return
    elif cb.data == "remove_thumb":
        clear_thumbnail(user_id)
        await cb.answer("✅ Removed.")
        return await start(client, cb.message)
    elif cb.data == "view_prefix":
        prefix = s.get("prefix_text", "")
        await cb.answer(f"Prefix: {prefix}", show_alert=True)
        return

    await cb.answer("✅ Updated")
    return await start(client, cb.message)

@app.on_message(filters.photo & filters.private)
async def save_thumbnail(client, message):
    user_id = message.from_user.id
    set_thumbnail(user_id, message.photo.file_id)
    await message.reply("✅ Thumbnail saved!")

@app.on_message(filters.command("rename"))
async def rename_file(client, message: Message):
    user_id = message.from_user.id
    settings = get_settings(user_id)

    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("❗ Reply to a file to rename it.")

    if len(message.command) < 2:
        return await message.reply("❗ Provide a new name: `/rename newname.ext`")

    new_name = message.text.split(None, 1)[1]
    if settings["prefix_enabled"]:
        new_name = f"{settings['prefix_text']} {new_name}"

    task = {
        "message": await message.reply("📥 Downloading..."),
        "start_time": time.time(),
        "action": "📥 Downloading"
    }
    file_path = await message.reply_to_message.download(file_name=new_name, progress=progress_bar, progress_args=(task,))

    caption = caption_styles(settings["caption_style"], f"✅ File: `{new_name}`")
    task = {
        "message": await message.reply("📤 Uploading..."),
        "start_time": time.time(),
        "action": "📤 Uploading"
    }

    thumb = get_thumbnail(user_id)

    if settings["rename_type"] == "video":
        await message.reply_video(file_path, caption=caption, thumb=thumb, progress=progress_bar, progress_args=(task,))
    else:
        await message.reply_document(file_path, caption=caption, thumb=thumb, progress=progress_bar, progress_args=(task,))

    # screenshots after upload
    if settings["screenshot"] and new_name.endswith((".mp4", ".mkv", ".mov")):
        ss_dir = f"ss_{user_id}"
        os.makedirs(ss_dir, exist_ok=True)
        ss_list = take_screenshots(file_path, ss_dir, settings["count"])
        for s in ss_list:
            await message.reply_photo(s)
        cleanup(ss_dir)

    cleanup(file_path)

app.run()
