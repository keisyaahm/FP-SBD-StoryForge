import mysql.connector
from pymongo import MongoClient


# ==========================
# MYSQL CONNECTION
# ==========================

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
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
# COLLECTIONS
# ==========================

character_lores = mongo_db["character_lores"]
chapters_content = mongo_db["chapters_content"]