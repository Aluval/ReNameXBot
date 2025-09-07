import time
import datetime
from datetime import timedelta
import psutil
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, INFO_PIC, SUNRISES_PIC, SUPPORT_GROUP, UPDATES_CHANNEL, ADMIN

START_TIME = datetime.datetime.now()

logging.basicConfig(
    filename='ReNameXBot.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



# Function to return the main inline keyboard
def get_start_markup():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about_info"),
            InlineKeyboardButton("🛠 Help", callback_data="help_info")
        ],
        [
            InlineKeyboardButton("📢 Updates", url=UPDATES_CHANNEL),
            InlineKeyboardButton("💬 Support", url=SUPPORT_GROUP)
        ]
    ])

# /start command
@Client.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_photo(
        photo=SUNRISES_PIC,
        caption=(
            "👋 Welcome to ReNameXBot!\n\n"
            "📁 Rename any document/video using:\n"
            "`/rename newname.ext` (by replying to a file)\n"
            "`/renamelink newname.ext <link>` (for direct links)\n\n"
            "⚙️ Adjust your settings with `/settings`:\n"
            "➕ Add Prefix\n"
            "🖼️ Set Thumbnail\n"
            "📸 Enable Screenshot\n"
            "🔤 Custom Caption\n\n"
            "Use the buttons below to get started 👇"
        ),
        reply_markup=get_start_markup()
    )

# Callback for About
@Client.on_callback_query(filters.regex("about_info"))
async def about_panel(client: Client, cb: CallbackQuery):
    await cb.message.edit_text(
        "ℹ️ **About ReNameXBot**\n\n"
        "➕ Rename files with prefix\n"
        "➕ Rename Link(Direct Links) files with prefix\n"
        "🖼️ Add thumbnails\n"
        "📸 Generate video screenshots\n"
        "🧠 Caption customization\n\n"
        "Built with ❤️ by [@Sunrises_24](https://t.me/Sunrises_24)",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="go_start")]
        ]),
        disable_web_page_preview=True
    )


# Callback for Help
@Client.on_callback_query(filters.regex("help_info"))
async def help_panel(client: Client, cb: CallbackQuery):
    await cb.message.edit_text(
        "🛠 **Help Panel**\n\n"
        "`/rename newname.ext` - Rename file\n"
        "`/renamelink newname.ext <url>` - Rename from direct links (Pixeldrain, FastCloud, Workers.dev, Seedr, etc.)\n"
        "`/setprefix <text>` - Set file name prefix\n"
        "`/setcaption <text>` - Custom caption\n"
        "`/getfile <filename>` - Retrieve a saved file - Ownerfile\n"
        "`/getfile <userid> <filename>` - Retrieve a saved file - Othersfile\n"
        "`/settings` - Open settings\n"
        "`/tasks` - Show task list\n"
        "`/clear` - Clear your files\n"
        "`/stats` - Show usage stats\n"
        "`/logs` - Admin only",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="go_start")]
        ])
    )

# Back button to main menu
@Client.on_callback_query(filters.regex("go_start"))
async def back_to_start(client: Client, cb: CallbackQuery):
    await cb.message.edit_caption(
        caption=(
            "👋 Welcome to ReNameXBot!\n\n"
            "📁 Rename any document/video using:\n"
            "`/rename newname.ext` (by replying to a file)\n\n"
            "⚙️ Adjust your settings with `/settings`:\n"
            "➕ Add Prefix\n"
            "🖼️ Set Thumbnail\n"
            "📸 Enable Screenshot\n"
            "🔤 Custom Caption\n\n"
            "Use the buttons below to get started 👇"
        ),
        reply_markup=get_start_markup()
    )
    
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

@Client.on_callback_query(filters.regex("refresh_stats"))
async def refresh_stats(client: Client, cb: CallbackQuery):
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


# /help command
@Client.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    await message.reply_text(
        "**🛠 Help Menu for ReNameXBot**\n\n"
        "`/rename newname.ext` - Reply to a file to rename it\n"
        "`/renamelink newname.ext <url>` - Rename from direct links\n"
        "   (Supports: Seedr, Pixeldrain, FastCloud, Cloudflare - Workers.dev, Googleusercontent, Heroku(Some links) etc.)\n"
        "`/setprefix <text>` - Set custom prefix\n"
        "`/setcaption <text>` - Set custom caption\n"
        "`/getfile <filename>` - Retrieve a saved file - Ownerfile\n"
        "`/getfile <userid> <filename>` - Retrieve a saved file - Othersfile\n"
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
        "**📦 About ReNameXBot**\n\n"
        "🔹 Rename files with thumbnail, captions, and prefix\n"
        "🔹 Auto screenshot for videos (custom count)\n"
        "🔹 Rename files from direct links with `/renamelink`\n"
        "   (Supported: seedr, Pixeldrain, FastCloud, Workers.dev, Googleusercontent, heroku(somelinks) etc.)\n"
        "🔹 Stores renamed files for download\n"
        "🔹 Custom document/video mode toggle\n\n"
        "Built by: @Sunrises_24\n"
        "Powered by: Pyrogram + MongoDB"
    )

# /ping
@Client.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    start = time.time()
    temp = await message.reply("🏓 Pinging...")
    end = time.time()
    await temp.edit(f"🏓 Pong! `{(end - start) * 1000:.2f}ms`")


# /logs command (Admin only)
@Client.on_message(filters.command("logs") & filters.user(ADMIN))
async def logs_command(client: Client, message: Message):
    try:
        await message.reply_document("ReNameXBot.txt", caption="📄 Bot Log File")
    except Exception as e:
        await message.reply(f"❗ Error: `{e}`")

if __name__ == '__main__':
    app = Client("my_bot", bot_token=BOT_TOKEN)
    app.run()
