#character.py 
from bson import ObjectId
import mysql.connector
from db import get_mysql_connection, get_mongo_database

db = get_mongo_database()
character_collection = db["character_lores"]

# ===== HELPER: VALIDASI KEPEMILIKAN CERITA =====
def get_story_milik_user(user_id):
    """Mengambil semua cerita milik user yang sedang login (untuk referensi pemilihan)."""
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT story_id, title, status FROM story WHERE user_id = %s ORDER BY story_id ASC",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def is_story_owner(story_id, user_id):
    """Mengecek apakah story_id benar-benar milik user_id yang sedang login."""
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT story_id FROM story WHERE story_id = %s AND user_id = %s",
            (story_id, user_id)
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()

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
            add_character(user_id)
        elif pilihan == '2':
            view_characters_by_story(user_id)
        elif pilihan == '3':
            view_character_detail(user_id)
        elif pilihan == '4':
            update_character(user_id)
        elif pilihan == '5':
            delete_character(user_id)
        elif pilihan == '6':
            count_character_per_story()
        elif pilihan == '0':
            break
        else:
            print("Pilihan tidak valid.")

# TAMBAH KARAKTER (DIUBAH LOGIKA HYBRID + VALIDASI KEPEMILIKAN)
def add_character(user_id):
    print("\n=== Tambah Karakter ===")

    # Tampilkan cerita milik sendiri sebagai referensi, supaya tidak asal input Story ID
    daftar_cerita = get_story_milik_user(user_id)
    if not daftar_cerita:
        print("Belum ada draft cerita.")
        return

    print("\n--- CERITA MILIKMU ---")
    for s in daftar_cerita:
        print(f"[{s['story_id']}] {s['title']} ({s['status'].upper()})")

    try:
        story_id = int(input("\nStory ID : "))
    except ValueError:
        print("Story ID harus berupa angka.")
        return

    # VALIDASI KEPEMILIKAN: hanya boleh menambah karakter pada cerita milik sendiri
    if not is_story_owner(story_id, user_id):
        print("Akses Ditolak: Cerita tidak ditemukan atau bukan milikmu.")
        return

    character_name = input("Nama Karakter : ")
    if not character_name.strip():
        print("Nama karakter tidak boleh kosong.")
        return

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

# LIHAT SEMUA KARAKTER DARI STORY (HANYA MILIK SENDIRI)
def view_characters_by_story(user_id):
    print("\n=== Daftar Karakter Story ===")
    try:
        story_id = int(input("Story ID : "))
    except ValueError:
        print("Story ID harus berupa angka.")
        return

    # VALIDASI KEPEMILIKAN: hanya boleh melihat/kelola karakter cerita milik sendiri
    if not is_story_owner(story_id, user_id):
        print("Akses Ditolak: Cerita tidak ditemukan atau bukan milikmu.")
        return

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

# DETAIL KARAKTER (HANYA MILIK SENDIRI)
def view_character_detail(user_id):
    print("\n=== Detail Karakter ===")
    try:
        character_id = int(input("Character ID : "))
    except ValueError:
        print("Character ID harus berupa angka.")
        return

    char = character_collection.find_one({
        "character_id": character_id
    })

    if not char:
        print("Karakter tidak ditemukan.")
        return

    # VALIDASI KEPEMILIKAN: hanya boleh melihat detail karakter cerita milik sendiri
    if not is_story_owner(char["story_id"], user_id):
        print("Akses Ditolak: Karakter ini bukan bagian dari cerita milikmu.")
        return

    print()
    for key, value in char.items():
        if key != "_id":
            print(f"{key.title()} : {value}")

# EDIT ATRIBUT KARAKTER (SINKRONISASI HYBRID + VALIDASI KEPEMILIKAN)
def update_character(user_id):
    print("\n=== Edit Karakter ===")
    try:
        character_id = int(input("Character ID : "))
    except ValueError:
        print("Character ID harus berupa angka.")
        return

    char = character_collection.find_one({
        "character_id": character_id
    })

    if not char:
        print("Karakter tidak ditemukan.")
        return

    # VALIDASI KEPEMILIKAN: hanya boleh mengedit karakter cerita milik sendiri
    if not is_story_owner(char["story_id"], user_id):
        print("Akses Ditolak: Karakter ini bukan bagian dari cerita milikmu.")
        return

    field = input("Field yang ingin diubah (contoh: character_name / Hobi) : ")
    value = input("Nilai baru : ")

    # 1. Update ke database MongoDB
    result = character_collection.update_one(
        {"character_id": character_id},
        {"$set": {field: value}}
    )

    # 2. SINKRONISASI KE MYSQL: Jika yang diubah adalah nama, update juga MySQL-nya
    if field.lower() == "character_name":
        try:
            conn = get_mysql_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE `character` SET character_name = %s WHERE character_id = %s",
                (value, character_id)
            )
            conn.commit()
            print("[Sistem] Nama karakter di MySQL juga berhasil diperbarui.")
        except mysql.connector.Error as err:
            print(f"[ERROR] Gagal sinkronisasi MySQL: {err}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    if result.modified_count > 0:
        print("Data berhasil diperbarui secara menyeluruh.")
    else:
        print("Tidak ada perubahan (nilai yang Anda masukkan sama dengan sebelumnya).")

# HAPUS KARAKTER (DIUBAH LOGIKA HYBRID + VALIDASI KEPEMILIKAN)
def delete_character(user_id):
    print("\n=== Hapus Karakter ===")
    try:
        character_id = int(input("Character ID : "))
    except ValueError:
        print("Character ID harus berupa angka.")
        return

    char = character_collection.find_one({
        "character_id": character_id
    })

    if not char:
        print("Karakter tidak ditemukan.")
        return

    # VALIDASI KEPEMILIKAN: hanya boleh menghapus karakter cerita milik sendiri
    if not is_story_owner(char["story_id"], user_id):
        print("Akses Ditolak: Karakter ini bukan bagian dari cerita milikmu.")
        return

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