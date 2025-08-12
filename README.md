![Typing SVG](https://readme-typing-svg.herokuapp.com/?lines=𝐖𝐄𝐋𝐂𝐎𝐌𝐄+𝐓𝐎+🫆+𝐑𝐞𝐍𝐚𝐦𝐞𝐗𝐁𝐨𝐭+🫆;𝗖𝗥𝗘𝗔𝗧𝗘𝗗+𝗕𝗬+𝗧𝗘𝗔𝗠+𝐒𝐔𝐍𝐑𝐈𝐒𝐄𝐒+𝐇𝐀𝐑𝐒𝐇𝐀+𝟐𝟒✨!;🫆𝐑𝐞𝐍𝐚𝐦𝐞𝐗𝐁𝐨𝐭🫆!)</p>
<img src="https://envs.sh/dc0.jpg" alt="logo" target="/blank">

<h1 align="center">
 <b><a href="https://t.me/Sunrises_24" target="/blank">🫆 𝐑𝐞𝐍𝐚𝐦𝐞𝐗𝐁𝐨𝐭 🫆</a> 
</h1>

<p align="center">🫆 PUBLIC REPO 🫆</p>

## Deploy To Koyeb

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/yourusername/ReNameXBot&env[BOT_TOKEN]&env[API_ID]&env[API_HASH]&env[ADMIN]&env[MONGO_URL]&env[SUNRISES_PIC]&env[INFO_PIC]&env[WEBHOOK]=True&env[PORT]=8080&run_command=python%20bot.py&branch=main&name=ReNameXBot) 

## Deploy To Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/aluval/ReNameXBot)



## Deploy to Heroku

Press Below Button to Deploy!

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/aluval/ReNameXBot)

### **BOT INFO**

**ADD YOUR BOT TOKEN / CREDENTIALS IN `config.py` OR ENVIRONMENT VARIABLES**

**This Branch / Repo Supports: ReNameXBot — Rename, upload & manage files.**

**Behavior:**  
- Files **≤ 2GB** are re-uploaded to Telegram.  
---

## Features

- `Rename` — Rename files/videos and re-upload them with a custom name.
- `Settings` — Per-user settings panel (screenshot toggle, count, prefix, rename type).
- `Thumbnail` — Save & use custom thumbnails for uploads.
- `Screenshots` — Auto-capture screenshots from videos (configurable count).
- `Tasks` — Track rename/upload tasks (admin view with pagination).
- `Getfile` — Retrieve previously saved/uploaded files.
- `Custom Caption / Prefix` — Set caption text and prefix for uploaded files.
- `Admin` — Remove tasks and clear old database collections.

---

###  **𝑅𝐸𝑄𝑈𝐼𝑅𝐸𝐷 𝑉𝐴𝑅𝐼𝑀𝐴𝐵𝐿𝐸𝑆 (ENV / config.py)** 

* `BOT_TOKEN`  - Get bot token from [@BotFather](https://t.me/BotFather)  
* `API_ID` - From [my.telegram.org](https://my.telegram.org)  
* `API_HASH` - From [my.telegram.org](https://my.telegram.org)  
* `ADMIN` - Admin Telegram ID (comma-separated allowed if extended)  
* `MONGO_URL` - MongoDB connection string (Atlas or local)  
* `SUNRISES_PIC` - Start / welcome picture (telegraph or https link)  
* `INFO_PIC` - Settings / info picture (telegraph or https link)  
* `WEBHOOK` - `True` or `False` (if using webhook deployment)  
* `PORT` - Port used for webhook deployments (e.g., `8080`)  
* `DOWNLOAD_DIR` - Local downloads folder (default: `downloads`)  

> Example `config.py` env-vars used in this repo:
> ```py
> BOT_TOKEN = os.environ.get("BOT_TOKEN")
> API_ID = os.environ.get("API_ID")
> API_HASH = os.environ.get("API_HASH")
> ADMIN = int(os.environ.get("ADMIN", "123456789"))
> MONGO_URL = os.environ.get("MONGO_URL")
> SUNRISES_PIC = os.environ.get("SUNRISES_PIC", "https://envs.sh/eer.jpg")
> INFO_PIC = os.environ.get("INFO_PIC", "https://envs.sh/ees.jpg")
> WEBHOOK = bool(os.environ.get("WEBHOOK", True))
> PORT = int(os.environ.get("PORT", 8081))
> DOWNLOAD_DIR = "downloads"
> ```

---

### Commands (Core)

/start         - Bot alive check & welcome /settings      - Open settings panel (screenshot, count, prefix, type, thumb, caption) /rename        - Reply to a file + /rename <new_name> to rename & re-upload /tasks [page]  - List all tasks (admin view available) |getfile       - /getfile <filename> (or /getfile <user_id> <filename>) to download stored files /removetask    - /removetask <user_id> <task_index> (Admin only) /setprefix     - /setprefix <text> to set prefix /setcaption    - /setcaption <text> to set custom caption /clear         - Clear database (Admin only) help           - Get help & usage info about          - Learn about the bot ping           - Check bot latency / status

---

## Example Usage

1. **Rename a file**
   - Reply to a document/video with:
     ```
     /rename new_name.mp4
     ```
   - Bot will download, rename, and re-upload the file.

2. **Set a custom prefix**

/setprefix MyPrefix

3. **Save thumbnail**
- Send an image privately to the bot. The bot saves it as your thumbnail.

4. **Get a stored file**

/getfile movie.mkv or /getfile userid movie.mkv

- Bot searches your saved files and returns a match (case-insensitive, partial match supported).

---

## File Storage & DB Collections

The bot stores user data in MongoDB. Typical collections:
- `settings` — per-user settings (screenshot, count, prefix, rename_type)
- `thumbnails` — saved thumbnail file_ids
- `captions` — custom captions
- `tasks` — user tasks (rename/upload tracking)
- `user_files` — stored file metadata `{ user_id, name, path }`

---

## Deployment Notes

- For **Webhook deployments** (Koyeb / Render / Heroku) set `WEBHOOK=True` and provide `PORT`.  
- For **long-running** processes prefer hosting on a VPS / Docker with sufficient storage for downloads.  
- Ensure `DOWNLOAD_DIR` has enough disk space and is persisted between restarts if you want to keep files locally.

---

### 🔗 𝐂𝐨𝐧𝐭𝐚𝐜𝐓 𝐔𝐬!
- [Owner / Credits](https://telegram.me/Sunrises_24)  
- [Channel](https://telegram.me/sunriseseditsoffical6)  
- [Updates](https://telegram.me/Sunrises24BotUpdates)  
- [Support](https://telegram.me/Sunrises24BotSupport)

### Copyright ©️ [𝗦ᴜɴʀɪ𝘀ᴇ𝘀 𝗛ᴀʀ𝘀ʜᴀ 𝟸𝟺 🇮🇳 ᵀᴱᴸ](https://telegram.me/Sunrises_24)

<b>Selling This Repo For Money Is Strictly Prohibited 🚫</b>

#### THANK YOU ALL FOR THE SUPPORT 💫
#### 𝗧𝗛𝗔𝗡𝗞𝗦 𝗧𝗢 𝗠𝗬 𝗧𝗘𝗟𝗨𝗚𝗨 𝗔𝗗𝗠𝗜𝗡𝗦 𝗙𝗢𝗥 𝗦𝗨𝗣𝗣𝗢𝗥𝗧 ❤️

