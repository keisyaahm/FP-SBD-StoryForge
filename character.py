from bson import ObjectId
from FP_SBD.db import get_mongo_database

db = get_mongo_database()

character_collection = db["character_lores"]


# ===================================
# TAMBAH KARAKTER
# ===================================

def add_character():
    print("\n=== Tambah Karakter ===")

    character_id = int(input("Character ID : "))
    story_id = int(input("Story ID : "))
    character_name = input("Nama Karakter : ")

    character_data = {
        "character_id": character_id,
        "story_id": story_id,
        "character_name": character_name
    }

    while True:
        tambah = input("Tambah atribut lain? (y/n): ")

        if tambah.lower() != "y":
            break

        key = input("Nama atribut : ")
        value = input("Nilai atribut : ")

        character_data[key] = value

    character_collection.insert_one(character_data)

    print("Karakter berhasil ditambahkan.")


# ===================================
# LIHAT SEMUA KARAKTER DARI STORY
# ===================================

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
        print("Nama :", char["character_name"])

        for key, value in char.items():
            if key not in ["_id", "character_id", "story_id", "character_name"]:
                print(f"{key} : {value}")

    if not found:
        print("Tidak ada karakter.")


# ===================================
# DETAIL KARAKTER
# ===================================

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
            print(f"{key} : {value}")


# ===================================
# EDIT ATRIBUT KARAKTER
# ===================================

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
        {
            "character_id": character_id
        },
        {
            "$set": {
                field: value
            }
        }
    )

    if result.modified_count > 0:
        print("Data berhasil diperbarui.")
    else:
        print("Tidak ada perubahan.")


# ===================================
# HAPUS KARAKTER
# ===================================

def delete_character():
    print("\n=== Hapus Karakter ===")

    character_id = int(input("Character ID : "))

    result = character_collection.delete_one({
        "character_id": character_id
    })

    if result.deleted_count > 0:
        print("Karakter berhasil dihapus.")
    else:
        print("Karakter tidak ditemukan.")


# ===================================
# DASHBOARD MONGODB
# ===================================

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
            f"Story {item['_id']} "
            f"memiliki {item['total_character']} karakter"
        )