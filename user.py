#user.py
import mysql.connector
from db import get_mysql_connection

def register():
    print("\n=== DAFTAR AKUN BARU ===")

    username = input("Username : ").strip()
    email = input("Email    : ").strip()
    password = input("Password : ").strip()

    # VALIDASI INPUT KOSONG
    if not username or not email or not password:
        print("GAGAL: Username, Email, dan Password tidak boleh dikosongkan!")
        return

    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # CEK APAKAH USERNAME ATAU EMAIL SUDAH ADA
        cursor.execute(
            "SELECT * FROM `user` WHERE username = %s OR email = %s",
            (username, email)
        )

        if cursor.fetchone():
            print("GAGAL: Username atau Email tersebut sudah terdaftar di sistem!")
            return

        sql = "INSERT INTO `user` (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(sql, (username, email, password))
        conn.commit()

        print("Registrasi berhasil! Silakan login.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()

def login():
    print("\n=== MASUK APLIKASI ===")

    email = input("Email    : ").strip()
    password = input("Password : ").strip()

    # VALIDASI INPUT KOSONG
    if not email or not password:
        print("GAGAL: Email dan Password tidak boleh dikosongkan!")
        return

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

def lihat_profil(user_data):
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM `user` WHERE user_id = %s",
        (user_data['user_id'],)
    )

    user_terbaru = cursor.fetchone()

    cursor.close()
    conn.close()

    print("\n=== PROFIL SAYA ===")
    print(f"Nama Pengguna : {user_terbaru['username']}")
    print(f"Email         : {user_terbaru['email']}")
    print(f"Koin Pembaca  : {user_terbaru['coin_balance']}")
    print(f"Saldo Penulis : {user_terbaru['author_balance']}")
    print("===================")