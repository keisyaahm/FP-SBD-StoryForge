import mysql.connector
from db import get_mysql_connection

def top_up(user_id):
    print("\n--- MENU TOP-UP KOIN ---")
    print("Aturan: 10 Koin = Rp 5.000 (Berlaku Kelipatan)")
    print("Maksimal Top-Up: Rp 1.000.000")
    
    try:
        nominal = int(input("Masukkan nominal uang (Rp): "))
        
        # VALIDASI BATAS DAN KELIPATAN
        if nominal < 5000:
            print("GAGAL: Minimal top-up adalah Rp 5.000.")
            return
        if nominal > 1000000:
            print("GAGAL: Maksimal transaksi adalah Rp 1.000.000.")
            return
        if nominal % 5000 != 0:
            print("GAGAL: Nominal harus kelipatan genap dari Rp 5.000.")
            return

        # SIMULASI PEMBAYARAN (Validasi Saldo Rekening/E-Wallet)
        print("\n[Membuka Gateway Pembayaran...]")
        saldo_rekening = int(input("Masukkan saldo rekening/OVO/SPay Anda saat ini (Simulasi): Rp "))
        
        if saldo_rekening < nominal:
            print("TRANSAKSI DITOLAK: Saldo rekening Anda tidak mencukupi.")
            return

        # LOGIKA PERHITUNGAN KOIN OTOMATIS
        koin_didapat = (nominal // 5000) * 10

        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        # Insert riwayat
        cursor.execute(
            "INSERT INTO transaction_topup (user_id, amount_paid, coins_gained) VALUES (%s, %s, %s)",
            (user_id, nominal, koin_didapat)
        )
        # Update saldo koin
        cursor.execute(
            "UPDATE user SET coin_balance = coin_balance + %s WHERE user_id = %s",
            (koin_didapat, user_id)
        )
        conn.commit()
        
        # Tarik saldo terbaru untuk ditampilkan
        cursor.execute("SELECT coin_balance FROM user WHERE user_id = %s", (user_id,))
        saldo_baru = cursor.fetchone()['coin_balance']
        
        print(f"\n[SUCCESS] Pembayaran Rp {nominal} berhasil!")
        print(f"Koin bertambah: +{koin_didapat}")
        print(f"Saldo Koin Anda sekarang: {saldo_baru}")
        
    except ValueError:
        print("[ERROR] Masukkan angka yang valid tanpa titik atau koma.")
    except Exception as e:
        print(f"[ERROR SYSTEM] Gagal top-up: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def sudah_beli(user_id, chapter_id):
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT purchase_id FROM purchase_chapter WHERE user_id = %s AND chapter_id = %s",
            (user_id, chapter_id)
        )
        hasil = cursor.fetchone()
        return hasil is not None 
    except Exception:
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def beli_bab(user_id):
    print("\n--- BELI BAB PREMIUM ---")
    try:
        chapter_id = int(input("Masukkan ID Chapter yang ingin dibeli: "))
        
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT is_premium, coin_cost, status FROM chapter WHERE chapter_id = %s",
            (chapter_id,)
        )
        chapter = cursor.fetchone()

        if not chapter:
            print("[INFO] Chapter tidak ditemukan di database.")
            return

        if chapter['status'] != 'published':
            print("[INFO] Chapter belum dipublish. Tidak bisa dibeli.")
            return

        if not chapter['is_premium']:
            print("[INFO] Chapter ini gratis. Silakan langsung baca di menu Eksplorasi.")
            return

        if sudah_beli(user_id, chapter_id):
            print("[INFO] Kamu sudah pernah membeli chapter ini. Akses terbuka selamanya!")
            return

        # Cek ketersediaan koin
        cursor.execute("SELECT coin_balance FROM user WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        saldo_koin = user_data['coin_balance'] if user_data else 0

        # NOTIFIKASI JIKA SALDO KURANG
        if saldo_koin < chapter['coin_cost']:
            print(f"\n[FAILED] Saldo Koin Anda ({saldo_koin}) tidak cukup untuk membeli bab ini seharga {chapter['coin_cost']} koin.")
            print("-> Silakan masuk ke Menu Top-Up Koin terlebih dahulu.")
            return

        # Eksekusi Pembelian (Trigger MySQL akan otomatis potong koin & tambah saldo penulis)
        cursor.execute(
            "INSERT INTO purchase_chapter (user_id, chapter_id, coins_spent) VALUES (%s, %s, %s)",
            (user_id, chapter_id, chapter['coin_cost'])
        )
        conn.commit()
        
        # Tarik saldo terbaru setelah terpotong trigger
        cursor.execute("SELECT coin_balance FROM user WHERE user_id = %s", (user_id,))
        saldo_baru = cursor.fetchone()['coin_balance']
        
        print(f"\n[SUCCESS] Pembelian berhasil! Akses bab terbuka.")
        print(f"Koin terpotong: -{chapter['coin_cost']}")
        print(f"Sisa Saldo Koin Anda: {saldo_baru}")
        
    except ValueError:
        print("[ERROR] Masukkan angka ID yang valid.")
    except Exception as e:
        print(f"[ERROR] Gagal membeli: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def request_withdrawal(author_id):
    print("\n--- PENARIKAN PENDAPATAN (WITHDRAWAL) ---")
    try:
        jumlah = int(input("Masukkan jumlah koin yang ingin ditarik: "))
        
        if jumlah <= 0:
            print("GAGAL: Jumlah penarikan harus lebih dari 0.")
            return

        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)

        # Cek saldo penulis (Tanpa cek kolom role yang sudah dihapus)
        cursor.execute("SELECT author_balance FROM user WHERE user_id = %s", (author_id,))
        result = cursor.fetchone()

        if not result:
            print("[INFO] User tidak ditemukan.")
            return

        author_balance = result['author_balance']

        if author_balance < jumlah:
            print(f"[FAILED] Saldo Penulis tidak cukup. Saldo Anda saat ini: {author_balance} koin.")
            return
            
        print("\n[Simulasi Transfer Bank]")
        rekening = input("Masukkan Nomor Rekening Tujuan pencairan: ")

        cursor.execute(
            "INSERT INTO withdrawal (user_id, amount, status) VALUES (%s, %s, 'pending')",
            (author_id, jumlah)
        )
        conn.commit()
        print(f"\n[SUCCESS] Permintaan withdrawal sebanyak {jumlah} koin berhasil diajukan.")
        print(f"Dana akan ditransfer ke rekening {rekening} setelah disetujui Admin.")
        
    except ValueError:
        print("[ERROR] Masukkan angka yang valid.")
    except Exception as e:
        print(f"[ERROR] Gagal withdrawal: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def lihat_riwayat_withdrawal(author_id):
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT withdrawal_id, amount, status, requested_at FROM withdrawal WHERE user_id = %s ORDER BY requested_at DESC",
            (author_id,)
        )
        riwayat = cursor.fetchall()

        print(f"\n--- RIWAYAT PENARIKAN ---")
        if not riwayat:
            print("Belum ada riwayat penarikan pendapatan.")
        else:
            for row in riwayat:
                print(f"ID: {row['withdrawal_id']} | Koin Ditarik: {row['amount']} | Status: [{row['status'].upper()}] | Waktu: {row['requested_at']}")
    except Exception as e:
        print(f"[ERROR] Gagal ambil riwayat: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def cek_saldo(user_id):
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT coin_balance, author_balance FROM user WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        print("\n=== INFORMASI SALDO SAAT INI ===")
        print(f"Saldo Koin Pembaca    : {user_data['coin_balance']} Koin")
        print(f"Saldo Koin Penulis    : {user_data['author_balance']} Koin")
        print("================================")
    except Exception as e:
        print(f"[ERROR] Gagal mengecek saldo: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def menu_transaksi(user_id):
    while True:
        print("\n--- KEUANGAN & TRANSAKSI ---")
        print("1. Cek Saldo Koin & Pendapatan")
        print("2. Top-Up Koin Pembaca")
        print("3. Beli Bab Premium")
        print("4. Tarik Saldo Penulis (Withdrawal)")
        print("5. Lihat Riwayat Penarikan")
        print("0. Kembali ke Menu Utama")

        pilihan = input("Pilih menu: ")

        if pilihan == '1':   cek_saldo(user_id)
        elif pilihan == '2': top_up(user_id)
        elif pilihan == '3': beli_bab(user_id)
        elif pilihan == '4': request_withdrawal(user_id)
        elif pilihan == '5': lihat_riwayat_withdrawal(user_id)
        elif pilihan == '0': break
        else: print("Pilihan tidak valid.")