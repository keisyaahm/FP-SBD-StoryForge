from bson import ObjectId
import mysql
from db import get_mysql_connection, get_mongo_database

db = get_mongo_database()
character_collection = db["character_lores"]

# MENU UTAMA KARAKTER
def menu_karakter(user_id):
    while True:
        print("\n=== STUDIO: KELOLA KARAKTER ===")
        print("1. Tambah Karakter Baru")
        print("2. Lihat Daftar Karakter Berdasarkan Cerita")
        print("3. Lihat Detail Lore Karakter")
        print("4. Edit Atribut Karakter")
        print("5. Hapus Karakter")
        print("6. Statistik Karakter (Dashboard)")
        print("0. Kembali ke Menu Utama")
        pilihan = input("Pilih menu: ")

        if pilihan == '1':
            add_character()
        elif pilihan == '2':
            view_characters_by_story()
        elif pilihan == '3':
            view_character_detail()
        elif pilihan == '4':
            update_character()
        elif pilihan == '5':
            delete_character()
        elif pilihan == '6':
            count_character_per_story()
        elif pilihan == '0':
            break
        else:
            print("Pilihan tidak valid.")

# TAMBAH KARAKTER (DIUBAH LOGIKA HYBRID)
def add_character():
    print("\n=== Tambah Karakter ===")
    
    story_id = int(input("Story ID : "))
    character_name = input("Nama Karakter : ")

    # PERUBAHAN: Masukkan ke MySQL terlebih dahulu
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        sql_mysql = "INSERT INTO `character` (story_id, character_name) VALUES (%s, %s)"
        cursor.execute(sql_mysql, (story_id, character_name))
        conn.commit()
        
        # Mengambil ID otomatis dari MySQL
        character_id = cursor.lastrowid
        print(f"[Sistem] Data dasar terkunci di MySQL dengan Character ID: {character_id}")
    except mysql.connector.Error as err:
        print(f"Gagal menyimpan ke MySQL: {err}")
        cursor.close()
        conn.close()
        return
    
    cursor.close()
    conn.close()

    # Melanjutkan penyimpanan atribut detail ke MongoDB
    character_data = {
        "character_id": character_id,
        "story_id": story_id,
        "character_name": character_name.lower() # Disimpan huruf kecil untuk pencarian pop-up
    }

    print("\n-- Masukkan Atribut Tambahan --")
    while True:
        tambah = input("Tambah atribut lain? (y/n): ")
        if tambah.lower() != "y":
            break

        key = input("Nama atribut (misal: Ras/Senjata) : ")
        value = input("Nilai atribut : ")

        character_data[key] = value

    character_collection.insert_one(character_data)
    print("Karakter berhasil ditambahkan ke keseluruhan sistem (Hybrid).")

# LIHAT SEMUA KARAKTER DARI STORY
def view_characters_by_story():
    print("\n=== Daftar Karakter Story ===")
    story_id = int(input("Story ID : "))

    characters = character_collection.find({
        "story_id": story_id
    })

    found = False
    for char in characters:
        found = True
        print("\n----------------------")
        print("Character ID :", char["character_id"])
        print("Nama :", char["character_name"].title())

        for key, value in char.items():
            if key not in ["_id", "character_id", "story_id", "character_name"]:
                print(f"{key.title()} : {value}")

    if not found:
        print("Tidak ada karakter untuk cerita ini.")

# DETAIL KARAKTER
def view_character_detail():
    print("\n=== Detail Karakter ===")
    character_id = int(input("Character ID : "))

    char = character_collection.find_one({
        "character_id": character_id
    })

    if not char:
        print("Karakter tidak ditemukan.")
        return

    print()
    for key, value in char.items():
        if key != "_id":
            print(f"{key.title()} : {value}")

# EDIT ATRIBUT KARAKTER
def update_character():
    print("\n=== Edit Karakter ===")
    character_id = int(input("Character ID : "))

    char = character_collection.find_one({
        "character_id": character_id
    })

    if not char:
        print("Karakter tidak ditemukan.")
        return

    field = input("Field yang ingin diubah : ")
    value = input("Nilai baru : ")

    result = character_collection.update_one(
        {"character_id": character_id},
        {"$set": {field: value}}
    )

    if result.modified_count > 0:
        print("Data berhasil diperbarui.")
    else:
        print("Tidak ada perubahan.")

# HAPUS KARAKTER (DIUBAH LOGIKA HYBRID)
def delete_character():
    print("\n=== Hapus Karakter ===")
    character_id = int(input("Character ID : "))

    # PERUBAHAN: Hapus data dari MySQL
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM `character` WHERE character_id = %s", (character_id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error menghapus dari MySQL: {err}")
    finally:
        cursor.close()
        conn.close()

    # Hapus data dari MongoDB
    result = character_collection.delete_one({
        "character_id": character_id
    })

    if result.deleted_count > 0:
        print("Karakter berhasil dihapus dari sistem.")
    else:
        print("Karakter tidak ditemukan di MongoDB.")

# DASHBOARD MONGODB
def count_character_per_story():
    print("\n=== Statistik Karakter ===")

    pipeline = [
        {
            "$group": {
                "_id": "$story_id",
                "total_character": {
                    "$sum": 1
                }
            }
        }
    ]

    result = character_collection.aggregate(pipeline)

    for item in result:
        print(
            f"Story ID {item['_id']} "
            f"memiliki {item['total_character']} karakter terdaftar."
        )