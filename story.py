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

    # Tampilkan draft cerita milik sendiri sebagai referensi (FIX: jangan sampai error/keluar program kalau belum ada draft)
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT story_id, title FROM story WHERE user_id = %s AND status = 'draft' ORDER BY story_id ASC",
            (user_id,)
        )
        draft_stories = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not draft_stories:
        print("Belum ada draft cerita.")
    else:
        print("\n--- DRAFT CERITA MILIKMU ---")
        for s in draft_stories:
            print(f"[{s['story_id']}] {s['title']}")

    story_id = input("\nMasukkan ID Cerita milikmu: ")
    
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
            return

        # VALIDASI NOMOR BAB: harus berurutan, bab baru = bab terakhir + 1, tidak boleh sama/asal angka
        cursor.execute("SELECT MAX(chapter_number) FROM chapter WHERE story_id = %s", (story_id,))
        hasil_max = cursor.fetchone()
        nomor_terakhir = hasil_max[0] if hasil_max and hasil_max[0] is not None else 0
        nomor_seharusnya = nomor_terakhir + 1

        chapter_num_input = input(f"Bab Ke-Berapa (bab selanjutnya wajib Bab {nomor_seharusnya}): ")
        try:
            chapter_num = int(chapter_num_input)
        except ValueError:
            print("Nomor bab harus berupa angka.")
            return

        if chapter_num != nomor_seharusnya:
            print(f"Nomor bab tidak valid! Bab baru harus berurutan dan tidak boleh sama dengan bab lain. "
                  f"Nomor yang diizinkan sekarang hanya Bab {nomor_seharusnya} (bab terakhir + 1).")
            return

        chapter_title = input("Judul Bab: ")

        # VALIDASI BERBAYAR/GRATIS: kalau gratis, tidak perlu masuk opsi harga
        is_premium_input = input("Berbayar? (1 untuk Ya, 0 untuk Tidak): ").strip()
        if is_premium_input == '1':
            is_premium = 1
            while True:
                coin_cost_input = input("Harga Koin (lebih dari 0): ").strip()
                try:
                    coin_cost = int(coin_cost_input)
                except ValueError:
                    print("Harga koin harus berupa angka.")
                    continue
                if coin_cost <= 0:
                    print("Harga koin untuk bab berbayar harus lebih dari 0.")
                    continue
                break
        else:
            is_premium = 0
            coin_cost = 0  # Tidak berbayar -> otomatis 0, tanpa ditanya harga

        status_input = input("Langsung Publish atau Simpan Draft? (p/d): ").lower()
        status_db = 'published' if status_input == 'p' else 'draft'

        # PENULISAN ISI BAB: boleh lebih dari satu paragraf
        print("\nKetik isi paragraf cerita. Ketik 'selesai' (tanpa tanda kutip) pada baris baru jika sudah selesai menulis.")
        paragraf_list = []
        urutan = 1
        while True:
            teks = input(f"Paragraf {urutan} (atau ketik 'selesai' untuk berhenti): ")

            if teks.strip().lower() == 'selesai':
                if not paragraf_list:
                    print("Minimal harus ada satu paragraf sebelum mengakhiri penulisan.")
                    continue
                break

            if teks.strip() == '':
                print("Paragraf tidak boleh kosong.")
                continue

            paragraf_list.append({
                "urutan_paragraf": urutan,
                "teks": teks,
                "komentar_inline": []
            })
            urutan += 1
        
        sql_mysql = """INSERT INTO chapter (story_id, chapter_number, chapter_title, is_premium, coin_cost, status) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(sql_mysql, (story_id, chapter_num, chapter_title, is_premium, coin_cost, status_db))
        conn.commit()
        
        new_chapter_id = cursor.lastrowid 
        
        if status_db == 'published':
            cursor.execute("UPDATE story SET status = 'published' WHERE story_id = %s AND status = 'draft'", (story_id,))
            conn.commit()

        mongo_db = get_mongo_database()
        chapters_content = mongo_db["chapters_content"]
        
        dokumen_mongodb = {
            "chapter_id": new_chapter_id,
            "paragraf": paragraf_list
        }
        chapters_content.insert_one(dokumen_mongodb)
        print(f"Bab berhasil ditambahkan dengan status [{status_db.upper()}]!")
        
    except Exception as err:
        print(f"Gagal: {err}")
    finally:
        cursor.close()
        conn.close()

def tambah_komentar(user_id, username, chapter_id):
    mongo_db = get_mongo_database()
    chapters_content = mongo_db["chapters_content"]

    data = chapters_content.find_one({"chapter_id": int(chapter_id)})

    if not data:
        print("Isi bab tidak ditemukan.")
        return

    jumlah_paragraf = len(data["paragraf"])

    print("\n===== DAFTAR PARAGRAF =====")

    for p in data["paragraf"]:
        teks_pendek = p["teks"][:50]
        print(f"{p['urutan_paragraf']}. {teks_pendek}...")

    while True:
        pilihan = input(
            "\nKomentar pada paragraf ke (0 untuk batal): "
        )

        try:
            nomor_paragraf = int(pilihan)
        except ValueError:
            print("Nomor paragraf harus berupa angka.")
            continue

        if nomor_paragraf == 0:
            print("Penambahan komentar dibatalkan.")
            return

        if nomor_paragraf < 1 or nomor_paragraf > jumlah_paragraf:
            print("Nomor paragraf tidak valid.")
            continue

        break

    komentar = input("Komentar: ")

    hasil = chapters_content.update_one(
        {"chapter_id": int(chapter_id)},
        {
            "$push": {
                f"paragraf.{nomor_paragraf-1}.komentar_inline": {
                    "user_id": user_id,
                    "username": username,
                    "isi": komentar
                }
            }
        }
    )

    if hasil.modified_count > 0:
        print("Komentar berhasil ditambahkan!")
    else:
        print("Gagal menambahkan komentar.")

def lihat_komentar(chapter_id):
    mongo_db = get_mongo_database()

    data = mongo_db["chapters_content"].find_one(
        {"chapter_id": int(chapter_id)}
    )

    if not data:
        print("Bab tidak ditemukan.")
        return

    print("\n===== DAFTAR KOMENTAR =====")

    for paragraf in data["paragraf"]:
        nomor = paragraf["urutan_paragraf"]

        print(f"\n--- Paragraf {nomor} ---")

        komentar_list = paragraf.get("komentar_inline", [])

        if len(komentar_list) == 0:
            print("Belum ada komentar.")
        else:
            for i, k in enumerate(komentar_list, start=1):
                print(f"{i}. {k['username']}")
                print(f"   {k['isi']}")

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

def publish_story(user_id):
    print("\n=== PUBLISH CERITA ===")

    # Tampilkan daftar draft cerita milik sendiri (FIX: jangan error/keluar program kalau belum ada draft)
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT story_id, title FROM story WHERE user_id = %s AND status = 'draft' ORDER BY story_id ASC",
            (user_id,)
        )
        draft_stories = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not draft_stories:
        print("Belum ada draft cerita.")
        return

    print("\n--- DRAFT CERITA MILIKMU ---")
    for s in draft_stories:
        print(f"[{s['story_id']}] {s['title']}")

    story_id = input("\nMasukkan ID Cerita yang ingin dipublikasikan (0 untuk batal): ")
    if story_id == '0':
        print("Dibatalkan.")
        return

    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        # Pastikan cerita milik user
        cursor.execute("SELECT story_id FROM story WHERE story_id = %s AND user_id = %s AND status = 'draft'", (story_id, user_id))
        if not cursor.fetchone():
            print("Cerita tidak ditemukan, bukan milikmu, atau sudah dipublish sebelumnya.")
            return
        cursor.execute("UPDATE story SET status = 'published' WHERE story_id = %s", (story_id,))
        conn.commit()
        print("Cerita berhasil dipublikasikan!")
    except mysql.connector.Error as err:
        print(f"Gagal: {err}")
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

def baca_chapter(session_user):
    user_id = session_user['user_id']
    username = session_user['username']

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
            print("[Ketik nama karakter] -> Melihat lore karakter")
            print("[Ketik C] -> Tambah komentar")
            print("[Ketik V] -> Lihat komentar")
            print("[Ketik X] -> Keluar")

            opsi = input("Masukkan pilihan: ").strip().lower()

            if opsi == 'x':
                print("Keluar dari mode membaca.")
                break

            elif opsi == 'c':
                tambah_komentar(
                    user_id,
                    username,
                    chapter_id
                )

            elif opsi == 'v':
                lihat_komentar(chapter_id)

            elif opsi != '':
                lore = mongo_db["character_lores"].find_one({
                    "story_id": chapter_meta['story_id'],
                    "character_name": opsi
                })

                if lore:
                    print("\n" + "=" * 40)
                    print(f" POP-UP INFO: {lore['character_name'].upper()}")
                    print("=" * 40)

                    for key, value in lore.items():
                        if key not in [
                            "_id",
                            "character_id",
                            "story_id",
                            "character_name"
                        ]:
                            print(f" - {key.title()}: {value}")

                    print("=" * 40)
                    input("(Tekan Enter untuk menutup pop-up)")
                else:
                    print(
                        f"Karakter dengan nama '{opsi}' tidak ditemukan."
                    )
    else:
        print("Teks cerita tidak ditemukan di MongoDB.")