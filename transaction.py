from db import get_mysql_connection


<<<<<<< HEAD
=======
@contextmanager
def db_cursor():
    """Context manager untuk koneksi & cursor MySQL.
    - Otomatis rollback kalau ada error di tengah proses (biar gak ada data setengah jadi).
    - Otomatis nutup cursor & koneksi di akhir, gak peduli sukses atau gagal.
    """
    conn = get_mysql_connection()
    cursor = conn.cursor()
    try:
        yield conn, cursor
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def get_coin_balance(user_id):
    """Ambil saldo koin user saat ini. Return None kalau user tidak ditemukan."""
    with db_cursor() as (conn, cursor):
        cursor.execute("SELECT coin_balance FROM user WHERE user_id = %s", (user_id,))
        hasil = cursor.fetchone()
        return hasil[0] if hasil else None


def cek_saldo(user_id):
    """Menampilkan saldo koin user saat ini."""
    try:
        saldo = get_coin_balance(user_id)
        if saldo is None:
            print("[INFO] User tidak ditemukan.")
        else:
            print(f"\n[INFO] Saldo koin Anda saat ini: {saldo} koin.")
    except Exception as e:
        print(f"[ERROR] Gagal mengambil saldo: {e}")


MIN_TOPUP = 5000
MAX_TOPUP = 50000
KELIPATAN_TOPUP = 5000
KOIN_PER_KELIPATAN = 10  # tiap Rp5.000 = 10 koin


>>>>>>> f1fca7923d407f866af6f2a963173793d1516d25
def top_up(user_id):
    """Proses top-up saldo koin user.
    Nominal harus kelipatan Rp5.000 (min Rp5.000, max Rp500.000).
    Jumlah koin dihitung otomatis dari nominal, jadi user gak input koin manual.
    """
    print("\n--- Menu Top-Up ---")
    print(f"Nominal harus kelipatan Rp{KELIPATAN_TOPUP:,} (contoh: Rp5.000 = {KOIN_PER_KELIPATAN} koin).")
    print(f"Minimal Rp{MIN_TOPUP:,}, maksimal Rp{MAX_TOPUP:,}.")

    try:
        nominal = int(input("Masukkan nominal uang (Rp): "))
<<<<<<< HEAD
        koin = int(input("Masukkan jumlah koin yang didapat: "))

        conn = get_mysql_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO transaction_topup (user_id, amount_paid, coins_gained) VALUES (%s, %s, %s)",
            (user_id, nominal, koin)
        )
        cursor.execute(
            "UPDATE user SET coin_balance = coin_balance + %s WHERE user_id = %s",
            (koin, user_id)
        )
=======
    except ValueError:
        print("[ERROR] Nominal harus berupa angka.")
        return

    if nominal < MIN_TOPUP:
        print(f"[ERROR] Nominal top-up minimal Rp{MIN_TOPUP:,}.")
        return

    if nominal > MAX_TOPUP:
        print(f"[ERROR] Nominal top-up maksimal Rp{MAX_TOPUP:,}.")
        return

    if nominal % KELIPATAN_TOPUP != 0:
        print(f"[ERROR] Nominal top-up harus kelipatan Rp{KELIPATAN_TOPUP:,}.")
        return

    koin = (nominal // KELIPATAN_TOPUP) * KOIN_PER_KELIPATAN

    try:
        with db_cursor() as (conn, cursor):
            cursor.execute(
                "INSERT INTO transaction_topup (user_id, amount_paid, coins_gained) VALUES (%s, %s, %s)",
                (user_id, nominal, koin)
            )
            cursor.execute(
                "UPDATE user SET coin_balance = coin_balance + %s WHERE user_id = %s",
                (koin, user_id)
            )
            conn.commit()
>>>>>>> f1fca7923d407f866af6f2a963173793d1516d25

        conn.commit()
        print(f"[SUCCESS] Top-up {koin} koin berhasil!")
    except Exception as e:
        print(f"[ERROR] Gagal top-up: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def sudah_beli(user_id, chapter_id):
    """Cek apakah user sudah pernah beli chapter ini."""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT purchase_id FROM purchase_chapter WHERE user_id = %s AND chapter_id = %s",
            (user_id, chapter_id)
        )
        hasil = cursor.fetchone()
        return hasil is not None  # True = sudah beli
    except Exception as e:
        print(f"[ERROR] Cek pembelian gagal: {e}")
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def beli_bab(user_id):
    """Membeli bab premium (Trigger MySQL otomatis memproses saldo)."""
    chapter_id = int(input("Masukkan ID Chapter yang ingin dibeli: "))
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()

        # Ambil info chapter: is_premium, coin_cost, status
        cursor.execute(
            "SELECT is_premium, coin_cost, status FROM chapter WHERE chapter_id = %s",
            (chapter_id,)
        )
        chapter = cursor.fetchone()

        if not chapter:
            print("[INFO] Chapter tidak ditemukan.")
            return

        is_premium, coin_cost, status = chapter

        # Cek sudah published
        if status != 'published':
            print("[INFO] Chapter belum dipublish, tidak bisa dibeli.")
            return

        # Cek apakah premium
        if not is_premium:
            print("[INFO] Chapter ini gratis, langsung bisa dibaca!")
            return

        # Cek sudah pernah beli
        if sudah_beli(user_id, chapter_id):
            print("[INFO] Kamu sudah pernah membeli chapter ini. Akses terbuka!")
            return

        # Cek saldo koin cukup
        cursor.execute(
            "SELECT coin_balance FROM user WHERE user_id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        if not user or user[0] < coin_cost:
            saldo = user[0] if user else 0
            print(f"[FAILED] Saldo tidak cukup. Butuh {coin_cost} koin, saldo kamu {saldo} koin.")
            return

        # Insert ke purchase_chapter → trigger otomatis potong koin & tambah saldo penulis
        cursor.execute(
            "INSERT INTO purchase_chapter (user_id, chapter_id, coins_spent) VALUES (%s, %s, %s)",
            (user_id, chapter_id, coin_cost)
        )
        conn.commit()
        print(f"[SUCCESS] Pembelian berhasil! Akses terbuka. -{coin_cost} koin.")
    except Exception as e:
        print(f"[ERROR] Gagal membeli: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def request_withdrawal(author_id):
    """Meminta penarikan saldo pendapatan penulis (status pending, saldo TIDAK langsung dikurangi)."""
    jumlah = int(input("Masukkan jumlah koin untuk ditarik: "))
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT author_balance, role FROM user WHERE user_id = %s",
            (author_id,)
        )
        result = cursor.fetchone()

<<<<<<< HEAD
        if not result:
            print("[INFO] User tidak ditemukan.")
            return
=======
    try:
        with db_cursor() as (conn, cursor):
            cursor.execute(
                "SELECT author_balance FROM user WHERE user_id = %s",
                (author_id,)
            )
            result = cursor.fetchone()
>>>>>>> f1fca7923d407f866af6f2a963173793d1516d25

        author_balance, role = result

<<<<<<< HEAD
        if role != 'author':
            print("[FAILED] Hanya penulis yang bisa melakukan withdrawal.")
            return

        if author_balance < jumlah:
            print(f"[FAILED] Saldo tidak cukup. Saldo saat ini: {author_balance} koin.")
            return
=======
            author_balance = result[0]
>>>>>>> f1fca7923d407f866af6f2a963173793d1516d25

        # Hanya insert pengajuan, TIDAK kurangi saldo (tunggu admin approve)
        cursor.execute(
            "INSERT INTO withdrawal (user_id, amount, status) VALUES (%s, %s, 'pending')",
            (author_id, jumlah)
        )
        conn.commit()
        print("[SUCCESS] Permintaan withdrawal berhasil diajukan. Menunggu persetujuan admin.")
    except Exception as e:
        print(f"[ERROR] Gagal withdrawal: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def lihat_riwayat_withdrawal(author_id):
    """Menampilkan riwayat penarikan milik penulis."""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT withdrawal_id, amount, status, requested_at FROM withdrawal WHERE user_id = %s ORDER BY requested_at DESC",
            (author_id,)
        )
        riwayat = cursor.fetchall()

        print(f"\n--- Riwayat Penarikan (User ID: {author_id}) ---")
        if not riwayat:
            print("Belum ada riwayat penarikan.")
        else:
            for row in riwayat:
                print(f"ID: {row[0]} | Jumlah: {row[1]} | Status: {row[2]} | Waktu: {row[3]}")
    except Exception as e:
        print(f"[ERROR] Gagal ambil riwayat: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


# ============================================================
# MENU TRANSAKSI (Integrasi dengan main.py Keisya)
# ============================================================

def menu_transaksi(user_id):
    while True:
        print("\n--- MENU TRANSAKSI 💰 ---")
        print("1. Top-Up Koin")
        print("2. Beli Bab")
        print("3. Request Withdrawal")
        print("4. Lihat Riwayat Withdrawal")
        print("0. Kembali ke Menu Utama")

        pilihan = input("Pilih menu: ")

        if pilihan == '1':   top_up(user_id)
        elif pilihan == '2': beli_bab(user_id)
        elif pilihan == '3': request_withdrawal(user_id)
        elif pilihan == '4': lihat_riwayat_withdrawal(user_id)
        elif pilihan == '0': break
        else: print("Pilihan tidak valid.")


# ============================================================
# TESTING MANDIRI (jalan kalau file ini dieksekusi langsung)
# Hapus/comment blok ini saat sudah digabung ke main.py
# ============================================================
if __name__ == "__main__":
    print("=== MODE TEST transaction.py ===")
    test_user_id = int(input("Masukkan User ID untuk testing: "))
    menu_transaksi(test_user_id)