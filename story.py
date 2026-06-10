# File: story.py
import mysql.connector
from db import get_mysql_connection, get_mongo_database

# FITUR SISI PENULIS
def buat_story(user_id):
    print("\n=== STUDIO: BUAT CERITA BARU ===")
    title = input("Judul Cerita: ")
    synopsis = input("Sinopsis: ")
    
    # 1=Fantasy, 2=Romance, 3=Thriller (Sesuai seed data di schema.sql)
    genre_id = input("ID Genre (1/2/3): ") 
    tags = input("Tags (pisahkan dengan koma): ")
    
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO story (user_id, title, synopsis, genre_id, tags, status) VALUES (%s, %s, %s, %s, %s, 'draft')"
        cursor.execute(sql, (user_id, title, synopsis, genre_id, tags))
        conn.commit()
        print("📝 Cerita berhasil dibuat dan masuk ke Draft!")
    except mysql.connector.Error as err:
        print(f"❌ Gagal: {err}")
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

def buat_chapter(user_id):
    print("\n=== STUDIO: TAMBAH BAB BARU (HYBRID) ===")
    story_id = input("Masukkan ID Cerita milikmu: ")
    chapter_num = input("Bab Ke-Berapa: ")
    chapter_title = input("Judul Bab: ")
    is_premium = input("Berbayar? (1 untuk Ya, 0 untuk Tidak): ")
    coin_cost = input("Harga Koin (0 jika gratis): ")
    status_input = input("Langsung Publish atau Simpan Draft? (p/d): ").lower()
    
    status_db = 'published' if status_input == 'p' else 'draft'
    isi_teks = input("Ketik isi paragraf cerita di sini:\n")
    
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        # STEP 1: Metadata ke MySQL
        sql_mysql = """INSERT INTO chapter (story_id, chapter_number, chapter_title, is_premium, coin_cost, status) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_mysql, (story_id, chapter_num, chapter_title, is_premium, coin_cost, status_db))
        conn.commit()
        
        new_chapter_id = cursor.lastrowid 
        
        # STEP 2: Konten teks ke MongoDB
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
        print(f"🎉 Bab berhasil ditambahkan dengan status [{status_db.upper()}]!")
    except Exception as err:
        print(f"❌ Gagal: {err}")
    finally:
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
    
    # 1. Cek keamanan bab di MySQL
    cursor.execute("SELECT * FROM chapter WHERE chapter_id = %s AND status = 'published'", (chapter_id,))
    chapter_meta = cursor.fetchone()

    if not chapter_meta:
        print("Bab tidak ditemukan atau masih berstatus Draft.")
        cursor.close(); conn.close()
        return

    # 2. Cek pembayaran jika premium
    if chapter_meta['is_premium']:
        cursor.execute("SELECT * FROM purchase_chapter WHERE user_id = %s AND chapter_id = %s", (user_id, chapter_id))
        if not cursor.fetchone():
            print(f"Bab ini Premium! Silakan beli seharga {chapter_meta['coin_cost']} Koin.")
            cursor.close(); conn.close()
            return

    # 3. Otomatis catat ke read_history
    try:
        cursor.execute("INSERT INTO read_history (user_id, chapter_id) VALUES (%s, %s)", (user_id, chapter_id))
        conn.commit()
    except:
        pass # Abaikan jika gagal mencatat log

    cursor.close()
    conn.close()

    # 4. Tarik Teks dari MongoDB
    mongo_db = get_mongo_database()
    content_data = mongo_db["chapters_content"].find_one({"chapter_id": int(chapter_id)})

    if content_data:
        print(f"\n📖 [ {chapter_meta['chapter_title'].upper()} ] 📖")
        print("--------------------------------------------------")
        for p in content_data['paragraf']:
            print(p['teks'])
        print("--------------------------------------------------")
        print("Selesai membaca bab ini.")
    else:
        print("Teks cerita tidak ditemukan di MongoDB.")