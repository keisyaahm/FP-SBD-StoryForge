from db import get_mysql_connection, get_mongo_database
import mysql.connector

def register():
    print("\n=== REGISTER ===")
    username = input("Username: ")
    email = input("Email: ")
    password = input("Password: ")
    role = input("Role (author/reader): ")
    
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO `user` (username, email, password, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (username, email, password, role))
        conn.commit()
        print("Registrasi berhasil! Silakan login.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def login():
    print("\n=== LOGIN ===")
    email = input("Email: ")
    password = input("Password: ")
    
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)
    sql = "SELECT * FROM `user` WHERE email = %s AND password = %s"
    cursor.execute(sql, (email, password))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if user:
        print(f"\nSelamat datang, {user['username']}!")
        return user
    else:
        print("Email atau password salah.")
        return None

def create_story(user_id):
    print("\n=== BUAT CERITA BARU ===")
    title = input("Judul Cerita: ")
    synopsis = input("Sinopsis: ")
    genre = input("Genre (romance/fantasy/thriller/horror/slice_of_life/other): ")
    
    conn = get_mysql_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO story (user_id, title, synopsis, genre, status) VALUES (%s, %s, %s, %s, 'draft')"
    cursor.execute(sql, (user_id, title, synopsis, genre))
    conn.commit()
    print("Cerita berhasil dibuat sebagai Draft!")
    cursor.close()
    conn.close()

def add_chapter(user_id):
    print("\n=== TAMBAH BAB (HYBRID) ===")
    story_id = input("Masukkan ID Cerita milikmu: ")
    chapter_num = input("Bab Ke-Berapa: ")
    chapter_title = input("Judul Bab: ")
    is_premium = input("Berbayar? (1 untuk Ya, 0 untuk Tidak): ")
    coin_cost = input("Harga Koin (0 jika gratis): ")
    isi_teks = input("Ketik isi paragraf cerita di sini:\n")
    
    # STEP 1: Masukkan metadata ke MySQL
    conn = get_mysql_connection()
    cursor = conn.cursor()
    sql_mysql = """INSERT INTO chapter (story_id, chapter_number, chapter_title, is_premium, coin_cost, status) 
                   VALUES (%s, %s, %s, %s, %s, 'published')"""
    cursor.execute(sql_mysql, (story_id, chapter_num, chapter_title, is_premium, coin_cost))
    conn.commit()
    
    # Ambil ID chapter yang baru saja dibuat di MySQL
    new_chapter_id = cursor.lastrowid 
    cursor.close()
    conn.close()
    
    # STEP 2: Masukkan teks konten ke MongoDB
    mongo_db = get_mongo_database()
    chapters_content = mongo_db["chapters_content"]
    
    dokumen_mongodb = {
        "chapter_id": new_chapter_id,  # Ini jembatan penghubungnya!
        "paragraf": [
            {
                "urutan_paragraf": 1,
                "teks": isi_teks,
                "komentar_inline": []
            }
        ]
    }
    chapters_content.insert_one(dokumen_mongodb)
    print("Bab berhasil ditambahkan secara Hybrid (Metadata di MySQL, Teks di MongoDB)!")

def main_menu():
    current_user = None
    while True:
        print("\n================================")
        print("   STORYFORGE CLI INTERFACE")
        print("================================")
        if not current_user:
            print("1. Register")
            print("2. Login")
            print("0. Keluar")
            pilihan = input("Pilih menu: ")
            
            if pilihan == '1': register()
            elif pilihan == '2': current_user = login()
            elif pilihan == '0': break
        else:
            print("1. Buat Cerita Baru")
            print("2. Tambah Bab (Hybrid)")
            print("9. Logout")
            pilihan = input("Pilih menu: ")
            
            if pilihan == '1': create_story(current_user['user_id'])
            elif pilihan == '2': add_chapter(current_user['user_id'])
            elif pilihan == '9': current_user = None

if __name__ == "__main__":
    main_menu()