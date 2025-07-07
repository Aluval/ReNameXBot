from pymongo import MongoClient

MONGO_URL = "mongodb+srv://HARSHA24:HARSHA24@cluster0.sxaj8up.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URL)
db = client.rename_bot

settings_col = db.settings
thumbs_col = db.thumbnails
captions_col = db.captions
admin_col = db.admins
limits_col = db.limits

# ---------- User Settings ----------
def get_settings(uid):
    data = settings_col.find_one({"_id": uid})
    if not data:
        default = {
            "_id": uid,
            "screenshot": False,
            "count": 3,
            "rename_type": "doc",
            "prefix_enabled": True,
            "caption_style": "bold",
            "prefix_text": "@sunriseseditsoffical6 -"
        }
        settings_col.insert_one(default)
        return default
    return data

def update_settings(uid, key, value):
    settings_col.update_one({"_id": uid}, {"$set": {key: value}}, upsert=True)

def update_prefix(uid, prefix):
    update_settings(uid, "prefix_text", prefix)

# ---------- Thumbnail ----------
def set_thumbnail(uid, file_id):
    thumbs_col.update_one({"_id": uid}, {"$set": {"thumb": file_id}}, upsert=True)

def get_thumbnail(uid):
    data = thumbs_col.find_one({"_id": uid})
    return data["thumb"] if data else None

def clear_thumbnail(uid):
    thumbs_col.delete_one({"_id": uid})

# ---------- Caption ----------
def update_caption(uid, text):
    captions_col.update_one({"_id": uid}, {"$set": {"caption": text}}, upsert=True)

def get_caption(uid):
    data = captions_col.find_one({"_id": uid})
    return data["caption"] if data else None

# ---------- Admin ----------
def get_admins():
    return [admin["_id"] for admin in admin_col.find()]

def is_admin_user(uid):
    return admin_col.find_one({"_id": uid}) is not None

def add_admin(uid):
    admin_col.update_one({"_id": uid}, {"$set": {"role": "admin"}}, upsert=True)

def remove_admin(uid):
    admin_col.delete_one({"_id": uid})

# ---------- Limits ----------
def get_max_concurrent():
    val = limits_col.find_one({"_id": "global"})
    return val["limit"] if val else 4

def set_max_concurrent(new_limit):
    limits_col.update_one({"_id": "global"}, {"$set": {"limit": new_limit}}, upsert=True)

def increase_limit():
    curr = get_max_concurrent()
    set_max_concurrent(curr + 1)
    return curr + 1

def decrease_limit():
    curr = get_max_concurrent()
    if curr > 1:
        set_max_concurrent(curr - 1)
        return curr - 1
    return curr
