# File: story.py
import mysql.connector
from db import get_mysql_connection, get_mongo_database

# FITUR SISI PENULIS
def buat_story(user_id):
    print("\n=== STUDIO: BUAT CERITA BARU ===")
    print("(Ketik '0' pada Judul untuk membatalkan)")
    title = input("Judul Cerita: ")
    
    if title == '0':
        print("Dibatalkan. Kembali ke menu utama.")
        return
        
    synopsis = input("Sinopsis: ")
    
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM genres ORDER BY genre_id ASC")
        daftar_genre = cursor.fetchall()
        
        if not daftar_genre:
            print("Peringatan: Tabel genre di database kosong.")
            cursor.close()
            conn.close()
            return
            
        print("\n--- PILIH GENRE UTAMA ---")
        for g in daftar_genre:
            print(f"[{g['genre_id']}] {g['genre_name']}")
            
        genre_id_input = input("\nPilih Nomor Genre: ")
        
        print("\n--- KATEGORI & TAGS TAMBAHAN ---")
        tags_bebas = input("Tags (pisahkan dengan koma): ")
        
        sql = "INSERT INTO story (user_id, title, synopsis, genre_id, tags, status) VALUES (%s, %s, %s, %s, %s, 'draft')"
        cursor.execute(sql, (user_id, title, synopsis, int(genre_id_input), tags_bebas))
        conn.commit()
        
        print("\nCerita berhasil dibuat dan masuk ke folder Draft!")
        
    except mysql.connector.Error as err:
        print(f"\nGagal menyimpan cerita: {err}")
    except ValueError:
        print("\nInput nomor genre tidak valid. Harap masukkan angka.")
    finally:
        cursor.close()
        conn.close()

def buat_chapter(user_id):
    print("\n=== STUDIO: TAMBAH BAB BARU (HYBRID) ===")
    print("(Ketik '0' pada ID Cerita untuk membatalkan)")
    story_id = input("Masukkan ID Cerita milikmu: ")
    
    if story_id == '0':
        print("Dibatalkan. Kembali ke menu utama.")
        return
    
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    # VALIDASI KEAMANAN: Cek apakah cerita ini benar milik user yang sedang login
    try:
        cursor.execute("SELECT story_id FROM story WHERE story_id = %s AND user_id = %s", (story_id, user_id))
        cek_milik = cursor.fetchone()
        
        if not cek_milik:
            print("Akses Ditolak: Cerita tidak ditemukan atau Anda bukan penulis cerita ini.")
            cursor.close()
            conn.close()
            return
            
        chapter_num = input("Bab Ke-Berapa: ")
        chapter_title = input("Judul Bab: ")
        is_premium = input("Berbayar? (1 untuk Ya, 0 untuk Tidak): ")
        coin_cost = input("Harga Koin (0 jika gratis): ")
        status_input = input("Langsung Publish atau Simpan Draft? (p/d): ").lower()
        
        status_db = 'published' if status_input == 'p' else 'draft'
        isi_teks = input("Ketik isi paragraf cerita di sini:\n")
        
        sql_mysql = """INSERT INTO chapter (story_id, chapter_number, chapter_title, is_premium, coin_cost, status) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_mysql, (story_id, chapter_num, chapter_title, is_premium, coin_cost, status_db))
        conn.commit()
        
        new_chapter_id = cursor.lastrowid 
        
        mongo_db = get_mongo_database()
        chapters_content = mongo_db["chapters_content"]
        
        dokumen_mongodb = {
            "chapter_id": new_chapter_id,
            "paragraf": [
                {
                    "urutan_paragraf": 1,
                    "teks": isi_teks,
                    "komentar_inline": []
                }
            ]
        }
        chapters_content.insert_one(dokumen_mongodb)
        print(f"Bab berhasil ditambahkan dengan status [{status_db.upper()}]!")
        
    except Exception as err:
        print(f"Gagal: {err}")
    finally:
        cursor.close()
        conn.close()

def lihat_story_ku(user_id):
    print("\n=== DAFTAR KARYA SAYA ===")
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT story_id, title, status FROM story WHERE user_id = %s", (user_id,))
    stories = cursor.fetchall()
    
    if not stories:
        print("Kamu belum menulis cerita apapun.")
    else:
        for s in stories:
            print(f"ID: {s['story_id']} | Judul: {s['title']} | Status: [{s['status'].upper()}]")
            
            # Cek daftar bab di dalam cerita ini
            cursor.execute("SELECT chapter_id, chapter_title, status FROM chapter WHERE story_id = %s", (s['story_id'],))
            chapters = cursor.fetchall()
            for c in chapters:
                print(f"  -> Bab ID: {c['chapter_id']} - {c['chapter_title']} [{c['status'].upper()}]")
                
    cursor.close()
    conn.close()

def publish_chapter_draft():
    print("\n=== PUBLISH BAB DRAFT ===")
    chapter_id = input("Masukkan ID Bab yang ingin di-publish: ")
    
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE chapter SET status = 'published' WHERE chapter_id = %s", (chapter_id,))
        conn.commit()
        print("Bab berhasil di-publish ke publik!")
    except mysql.connector.Error as err:
        print(f"Gagal: {err}")
    finally:
        cursor.close()
        conn.close()

# FITUR SISI PEMBACA
def lihat_semua_published():
    print("\n=== EKSPLORASI CERITA STORYFORGE ===")
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT story_id, title, synopsis FROM story WHERE status = 'published'")
    stories = cursor.fetchall()
    
    if not stories:
        print("Belum ada cerita yang dipublish.")
    else:
        for s in stories:
            print(f"ID: {s['story_id']} | Judul: {s['title']}")
            print(f"Sinopsis: {s['synopsis']}\n")
    cursor.close()
    conn.close()

def baca_chapter(user_id):
    print("\n=== MESIN PEMBACAAN ===")
    chapter_id = input("Masukkan ID Bab yang ingin dibaca: ")

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM chapter WHERE chapter_id = %s AND status = 'published'", (chapter_id,))
    chapter_meta = cursor.fetchone()

    if not chapter_meta:
        print("Bab tidak ditemukan atau masih berstatus Draft.")
        cursor.close()
        conn.close()
        return

    if chapter_meta['is_premium']:
        cursor.execute("SELECT * FROM purchase_chapter WHERE user_id = %s AND chapter_id = %s", (user_id, chapter_id))
        if not cursor.fetchone():
            print(f"Bab ini Premium! Silakan beli seharga {chapter_meta['coin_cost']} Koin.")
            cursor.close()
            conn.close()
            return

    try:
        cursor.execute("INSERT INTO read_history (user_id, chapter_id) VALUES (%s, %s)", (user_id, chapter_id))
        conn.commit()
    except:
        pass 

    cursor.close()
    conn.close()

    mongo_db = get_mongo_database()
    content_data = mongo_db["chapters_content"].find_one({"chapter_id": int(chapter_id)})

    if content_data:
        print(f"\n[ {chapter_meta['chapter_title'].upper()} ]")
        print("-" * 50)
        for p in content_data['paragraf']:
            print(p['teks'])
        print("-" * 50)
        
        # LOGIKA SIMULASI POP-UP LORE KARAKTER
        while True:
            print("\nOpsi Pembaca:")
            print("[Ketik nama karakter] -> Untuk melihat Info Detail (Pop-Up Lore)")
            print("[Ketik 'X'] -> Selesai membaca dan keluar")
            opsi = input("Masukkan pilihan: ").strip().lower()

            if opsi == 'x':
                print("Keluar dari mode membaca.")
                break
            elif opsi != '':
                # Mencari lore karakter di MongoDB berdasarkan nama dan story_id bab ini
                lore = mongo_db["character_lores"].find_one({
                    "story_id": chapter_meta['story_id'],
                    "character_name": opsi
                })

                if lore:
                    print("\n" + "=" * 40)
                    print(f" POP-UP INFO: {lore['character_name'].upper()}")
                    print("=" * 40)
                    for key, value in lore.items():
                        if key not in ["_id", "character_id", "story_id", "character_name"]:
                            print(f" - {key.title()}: {value}")
                    print("=" * 40)
                    input("(Tekan Enter untuk menutup pop-up dan lanjut membaca)")
                else:
                    print(f"Karakter dengan nama '{opsi}' tidak ditemukan di sistem lore.")
    else:
        print("Teks cerita tidak ditemukan di MongoDB.")