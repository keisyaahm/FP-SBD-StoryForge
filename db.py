#db.py
import mysql.connector
from pymongo import MongoClient

# ==========================
# MYSQL CONNECTION
# ==========================
def get_mysql_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3308,
        user="root",
        password="",
        database="fiction_platform"
    )

# ==========================
# MONGODB CONNECTION
# ==========================
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["fiction_platform"]

def get_mongo_database():
    return mongo_db

# ==========================
# MONGODB COLLECTIONS
# ==========================
chapters_content = mongo_db["chapters_content"] # Isi teks & embedded inline comments
character_lores  = mongo_db["character_lores"]  # Profil detail karakter (Schema-less)
author_notes     = mongo_db["author_notes"]     # Catatan riset draf rahasia penulis
read_logs        = mongo_db["read_logs"]        # Log aktivitas baca untuk sistem Rekomendasi Beranda
reading_lists    = mongo_db["reading_lists"]    # Folder daftar bacaan publik
conversations    = mongo_db["conversations"]    # Papan percakapan / Feed Profil Pengguna