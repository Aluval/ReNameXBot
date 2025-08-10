import os
import re
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from main.db import (
    get_settings, update_settings, set_thumbnail, get_thumbnail, clear_thumbnail,
    update_caption, files_col, get_caption, add_task, get_user_tasks, remove_task, save_file, get_saved_file, get_user_files, clear_database
)
from main.utils import progress_bar, take_screenshots, cleanup
from config import *




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



@Client.on_message(filters.command("getfile"))
async def get_file(client, message: Message):
    uid = message.from_user.id

    if len(message.command) < 2:
        return await message.reply("❗ Usage: `/getfile <filename>`", quote=True)

    search_name = message.text.split(None, 1)[1].strip().lower()

    # Fetch user files from DB
    user_data = await db.get_user(uid)
    if not user_data or "files" not in user_data:
        return await message.reply("❌ No files found in database.", quote=True)

    # Match by actual saved path or stored filename
    matched_file = None
    for f in user_data["files"]:
        if search_name in f["name"].lower() or search_name in f["path"].lower():
            matched_file = f["path"]
            break

    if not matched_file:
        return await message.reply("❌ File not found in database.", quote=True)

    # Check if file exists physically
    if not os.path.exists(matched_file):
        return await message.reply("❌ File not found on server.", quote=True)

    # Send file
    await message.reply_document(matched_file, quote=True)

@Client.on_message(filters.command("tasks"))
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



@Client.on_message(filters.command("removetask") & filters.user(ADMIN))
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
        
if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
