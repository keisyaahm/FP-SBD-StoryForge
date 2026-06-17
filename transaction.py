import mysql.connector
from db import get_mysql_connection

def top_up(user_id):
    """Proses top-up koin pembaca dengan batasan minimal, maksimal, dan kelipatan."""
    print("\n--- Menu Top-Up Koin ---")
    print("Aturan: Minimal Rp 5.000 | Maksimal Rp 50.000 | Kelipatan Rp 5.000")
    print("Konversi: Setiap Rp 5.000 = 10 Koin Pembaca")
    
    try:
        nominal = int(input("Masukkan nominal uang yang dibayarkan (Rp): "))
        
        # Validasi Batas Bawah dan Batas Atas
        if nominal < 5000:
            print("[FAILED] Transaksi Ditolak: Nominal top-up minimal adalah Rp 5.000.")
            return
        if nominal > 50000:
            print("[FAILED] Transaksi Ditolak: Nominal top-up maksimal per transaksi adalah Rp 50.000.")
            return
            
        # Validasi Kelipatan Rp 5.000
        if nominal % 5000 != 0:
            print("[FAILED] Transaksi Ditolak: Nominal harus kelipatan Rp 5.000 (Contoh: 5000, 10000, 15000).")
            return

        # Perhitungan Koin Otomatis Berdasarkan Aturan Bisnis Baru
        koin = (nominal // 5000) * 10

        conn = get_mysql_connection()
        cursor = conn.cursor()

        # Rekam Log Riwayat Transaksi
        cursor.execute(
            "INSERT INTO transaction_topup (user_id, amount_paid, coins_gained) VALUES (%s, %s, %s)",
            (user_id, nominal, koin)
        )
        # Tambah Saldo Koin User
        cursor.execute(
            "UPDATE user SET coin_balance = coin_balance + %s WHERE user_id = %s",
            (koin, user_id)
        )
        conn.commit()
        
        # Ambil Saldo Terbaru untuk Ditampilkan ke Layar
        cursor.execute("SELECT coin_balance FROM user WHERE user_id = %s", (user_id,))
        saldo_terbaru = cursor.fetchone()[0]

        print(f"[SUCCESS] Top-up berhasil! Anda mendapatkan {koin} koin.")
        print(f"Saldo koin pembaca Anda saat ini: {saldo_terbaru} koin.")
        
    except ValueError:
        print("[ERROR] Input tidak valid. Silakan masukkan angka bulat.")
    except Exception as e:
        print(f"[ERROR] Gagal memproses top-up: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def sudah_beli(user_id, chapter_id):
    """Memeriksa riwayat pembelian bab agar user tidak membeli dua kali."""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT purchase_id FROM purchase_chapter WHERE user_id = %s AND chapter_id = %s",
            (user_id, chapter_id)
        )
        return cursor.fetchone() is not None
    except Exception as e:
        print(f"[ERROR] Gagal memeriksa riwayat: {e}")
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def beli_bab(user_id):
    """Membeli bab cerita premium dengan notifikasi kekurangan saldo dan sisa saldo akhir."""
    print("\n--- Menu Pembelian Bab Premium ---")
    try:
        chapter_id = int(input("Masukkan ID Bab yang ingin dibeli: "))
    except ValueError:
        print("[ERROR] Input tidak valid. ID Bab harus berupa angka.")
        return

    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()

        # Ambil spesifikasi naskah bab
        cursor.execute(
            "SELECT is_premium, coin_cost, status FROM chapter WHERE chapter_id = %s",
            (chapter_id,)
        )
        chapter = cursor.fetchone()

        if not chapter:
            print("[INFO] Bab tidak ditemukan di dalam sistem.")
            return

        is_premium, coin_cost, status = chapter

        if status != 'published':
            print("[INFO] Akses Ditutup: Bab ini masih berstatus Draft.")
            return

        if not is_premium:
            print("[INFO] Bab ini gratis. Anda bisa langsung membacanya di menu baca.")
            return

        if sudah_beli(user_id, chapter_id):
            print("[INFO] Anda sudah memiliki bab ini. Akses langsung terbuka!")
            return

        # Periksa kecukupan dompet koin pembaca
        cursor.execute("SELECT coin_balance FROM user WHERE user_id = %s", (user_id,))
        saldo = cursor.fetchone()[0]

        if saldo < coin_cost:
            kurang = coin_cost - saldo
            print(f"[FAILED] Transaksi Gagal: Saldo koin tidak mencukupi.")
            print(f"Harga Bab: {coin_cost} koin | Saldo Anda: {saldo} koin.")
            print(f"Pemberitahuan: Anda kekurangan {kurang} koin. Silakan lakukan Top-Up terlebih dahulu pada menu 8.")
            return

        # Eksekusi Pembelian (Trigger database otomatis memotong saldo pembaca & menambah saldo penulis)
        cursor.execute(
            "INSERT INTO purchase_chapter (user_id, chapter_id, coins_spent) VALUES (%s, %s, %s)",
            (user_id, chapter_id, coin_cost)
        )
        conn.commit()
        
        saldo_akhir = saldo - coin_cost
        print(f"[SUCCESS] Pembelian berhasil! Akses bab premium terbuka. Terpotong {coin_cost} koin.")
        print(f"Sisa saldo koin pembaca Anda sekarang: {saldo_akhir} koin.")
        
    except Exception as e:
        print(f"[ERROR] Transaksi gagal: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def request_withdrawal(author_id):
    """Mengajukan penarikan saldo pendapatan penulis (Maksimal Rp 1.000.000 / 2.000 koin per transaksi)."""
    print("\n--- Menu Penarikan Saldo Penulis (Withdrawal) ---")
    print("Kurs Konversi: 1 Koin Penulis = Rp 500")
    print("Batas Maksimal Penarikan: Rp 1.000.000 (Setara 2.000 Koin) per transaksi")
    
    try:
        jumlah = int(input("Masukkan jumlah koin yang ingin dicairkan ke rekening: "))
        if jumlah <= 0:
            print("[FAILED] Input harus lebih besar dari 0 koin.")
            return

        # Validasi Batas Atas Transaksi Sesuai Hasil Demo (Maksimal Rp 1 Juta = 2.000 Koin)
        if jumlah > 2000:
            print("[FAILED] Ditolak: Batas maksimal pencairan per transaksi adalah 2.000 koin (Rp 1.000.000).")
            return

        conn = get_mysql_connection()
        cursor = conn.cursor()

        # FIX BUG: Menghapus kolom 'role' dari kueri karena sudah dihapus di skema tabel baru
        cursor.execute(
            "SELECT author_balance FROM user WHERE user_id = %s",
            (author_id,)
        )
        result = cursor.fetchone()

        if not result:
            print("[INFO] Akun tidak ditemukan.")
            return

        author_balance = result[0]

        if author_balance < jumlah:
            print(f"[FAILED] Saldo tidak mencukupi untuk melakukan penarikan sebesar {jumlah} koin.")
            print(f"Saldo pendapatan Anda saat ini: {author_balance} koin.")
            return

        # Simpan draf pengajuan dengan status pending (menunggu verifikasi transfer manual oleh admin)
        cursor.execute(
            "INSERT INTO withdrawal (user_id, amount, status) VALUES (%s, %s, 'pending')",
            (author_id, jumlah)
        )
        conn.commit()
        
        nominal_rupiah = jumlah * 500
        print(f"[SUCCESS] Pengajuan sukses! Mencairkan {jumlah} koin menjadi Rp {nominal_rupiah:,}.")
        print("Status: [PENDING]. Dana akan masuk ke rekening Anda setelah disetujui oleh admin.")
        
    except ValueError:
        print("[ERROR] Masukan harus berupa angka bulat.")
    except Exception as e:
        print(f"[ERROR] Gagal mengajukan withdrawal: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def lihat_riwayat_withdrawal(author_id):
    """Melihat status lembar pengajuan penarikan dana penulis."""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT withdrawal_id, amount, status, requested_at FROM withdrawal WHERE user_id = %s ORDER BY requested_at DESC",
            (author_id,)
        )
        riwayat = cursor.fetchall()

        print(f"\n--- Riwayat Penarikan Dana Penulis ---")
        if not riwayat:
            print("Belum ada riwayat pengajuan penarikan.")
        else:
            for row in riwayat:
                nominal_rp = row[1] * 500
                print(f"ID Pengajuan: {row[0]} | Koin: {row[1]} (Rp {nominal_rp:,}) | Status: [{row[2].upper()}] | Tanggal: {row[3]}")
    except Exception as e:
        print(f"[ERROR] Gagal menarik riwayat: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()