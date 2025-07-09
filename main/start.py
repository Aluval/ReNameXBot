import time
import datetime
from datetime import timedelta
import psutil
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, INFO_PIC, SUPPORT_GROUP, UPDATES_CHANNEL
from config import *
# Start time for uptime
START_TIME = datetime.datetime.now()

# Logging setup
logging.basicConfig(
    filename='PixelPulseBot.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
# /start command
@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
            InlineKeyboardButton("🛠 Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("📢 Updates", url=UPDATES_CHANNEL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)
        ]
    ])

    await message.reply_photo(
        photo=INFO_PIC,
        caption=(
            "**👋 Welcome to Rename Bot!**\n\n"
            "📁 Rename any document/video using:\n"
            "`/rename newname.ext` (by replying to a file)\n\n"
            "⚙️ Adjust your settings with /settings:\n"
            "➕ Add Prefix\n"
            "🖼️ Set Thumbnail\n"
            "📸 Enable Screenshot\n"
            "🔤 Custom Caption\n\n"
            "Use the buttons below to get started 👇"
        ),
        reply_markup=buttons
    )

# /help command
@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text(
        "**🛠 Help Menu for Rename Bot**\n\n"
        "`/rename newname.ext` - Reply to a file to rename it\n"
        "`/setprefix <text>` - Set custom prefix\n"
        "`/setcaption <text>` - Set custom caption\n"
        "`/getfile <filename>` - Retrieve a saved file\n"
        "`/settings` - Bot settings panel\n"
        "`/tasks` - View your rename tasks\n"
        "`/clear` - Clear DB (Admins only)\n"
        "`/stats` - Show system stats\n"
        "`/logs` - Bot logs (Admins only)"
    )

# /about command
@Client.on_message(filters.command("about"))
async def about_command(client: Client, message: Message):
    await message.reply_text(
        "**📦 About Rename Bot**\n\n"
        "🔹 Rename files with thumbnail, captions, and prefix\n"
        "🔹 Auto screenshot for videos (custom count)\n"
        "🔹 Stores renamed files for download\n"
        "🔹 Custom document/video mode toggle\n\n"
        "Built by: @Sunrises_24\n"
        "Powered by: Pyrogram + MongoDB"
    )

# /ping command
@Client.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    start = time.time()
    temp = await message.reply("🏓 Pinging...")
    end = time.time()
    duration = (end - start) * 1000
    await temp.edit(f"🏓 Pong! `{duration:.2f}ms`")

# /stats command
@Client.on_message(filters.command("stats"))
async def stats_command(client: Client, message: Message):
    uptime = datetime.datetime.now() - START_TIME
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    disk = psutil.disk_usage('/')
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    stats_text = (
        "**📊 Bot & Server Stats:**\n\n"
        f"⏱ Uptime: `{uptime_str}`\n"
        f"💾 Disk Used: `{disk.used / (1024**3):.2f} GB` / `{disk.total / (1024**3):.2f} GB`\n"
        f"🧠 RAM Usage: `{ram}%`\n"
        f"⚙️ CPU Load: `{cpu}%`\n"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")],
        [
            InlineKeyboardButton("📢 Updates", url=UPDATES_CHANNEL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)
        ]
    ])

    await message.reply_photo(INFO_PIC, caption=stats_text, reply_markup=buttons)

# /logs command (Admin only)
@Client.on_message(filters.command("logs"))
async def logs_command(client: Client, message: Message):
    if message.from_user.id not in get_admins():
        return await message.reply("❌ You are not authorized to access logs.")
    try:
        await message.reply_document("PixelPulseBot.txt", caption="📄 Bot Log File")
    except Exception as e:
        await message.reply(f"❗ Error: `{e}`")

  

@Client.on_callback_query()
async def callback_handler(client: Client, cb: CallbackQuery):
    data = cb.data

    if data == "about":
        await cb.message.edit_text(
            "**ℹ️ About Rename Bot**\n\n"
            "➕ Rename files with prefix\n"
            "🖼️ Add thumbnails\n"
            "📸 Generate video screenshots\n"
            "🧠 Caption customization\n\n"
            "Built with ❤️ by @Sunrises_24",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )

    elif data == "help":
        await cb.message.edit_text(
            "**🛠 Help Panel**\n\n"
            "`/rename newname.ext`\n"
            "`/setprefix <text>`\n"
            "`/setcaption <text>`\n"
            "`/getfile <filename>`\n"
            "`/settings`\n"
            "`/tasks`\n"
            "`/clear`\n"
            "`/stats`\n"
            "`/logs` (admin only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="start")]
            ])
        )

    elif data == "refresh_stats":
        uptime = datetime.datetime.now() - START_TIME
        uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

        disk = psutil.disk_usage('/')
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        stats_text = (
            "**📊 Refreshed Stats:**\n\n"
            f"⏱ Uptime: `{uptime_str}`\n"
            f"💾 Disk Used: `{disk.used / (1024**3):.2f} GB` / `{disk.total / (1024**3):.2f} GB`\n"
            f"🧠 RAM Usage: `{ram}%`\n"
            f"⚙️ CPU Load: `{cpu}%`\n"
        )

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")],
            [
                InlineKeyboardButton("📢 Updates", url=UPDATES_CHANNEL),
                InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)
            ]
        ])

        try:
            await cb.message.edit_text(stats_text, reply_markup=buttons)
            await cb.answer("✅ Stats refreshed!")
        except Exception as e:
            await cb.answer("⚠️ Failed to refresh.", show_alert=True)
            print("Edit error:", e)

    elif data == "start":
        await start_command(client, cb.message)

# ✅ Entry point
if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
