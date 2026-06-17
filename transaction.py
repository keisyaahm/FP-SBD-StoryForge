#transaction.py
from db import get_mysql_connection

def top_up(user_id):
    """Proses top-up saldo koin user."""
    print("\n--- Menu Top-Up ---")
    try:
        nominal = int(input("Masukkan nominal uang (Rp): "))
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

        if not result:
            print("[INFO] User tidak ditemukan.")
            return

        author_balance, role = result

        if role != 'author':
            print("[FAILED] Hanya penulis yang bisa melakukan withdrawal.")
            return

        if author_balance < jumlah:
            print(f"[FAILED] Saldo tidak cukup. Saldo saat ini: {author_balance} koin.")
            return

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
        print("\n--- MENU TRANSAKSI ---")
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