# File: main.py
import user
import story
import character
import transaction

# Mendefinisikan session_user di level global agar bisa diakses semua fungsi
session_user = None

def main_menu():
    global session_user # Memberitahu Python bahwa kita menggunakan variabel global di atas
    
    while True:
        print("\n==========================================")
        print(" STORYFORGE: PLATFORM FIKSI ALL-IN-ONE ")
        print("==========================================")
        
        # TAMPILAN JIKA BELUM LOGIN
        if not session_user:
            print("1. Register")
            print("2. Login")
            print("0. Keluar Aplikasi")
            pilihan = input("Pilih menu: ")
            
            if pilihan == '1': 
                user.register()
            elif pilihan == '2': 
                session_user = user.login()
            elif pilihan == '0': 
                print("Terima kasih telah menggunakan StoryForge!")
                break
                
        # TAMPILAN JIKA SUDAH LOGIN
        else:
            print(f"Halo, {session_user['username']}! Selamat datang di Beranda.")
            print("--- PROFIL & AKUN ---")
            print("1. Lihat Profil & Dompet Koin")
            print("--- MODE PEMBACA ---")
            print("2. Eksplorasi Cerita (Published)")
            print("3. Baca Bab Cerita")
            print("--- MODE PENULIS ---")
            print("4. Buat Cerita Baru")
            print("5. Tambah Bab (Draft/Publish)")
            print("6. Kelola Lore Karakter")
            print("7. Lihat Daftar Karyaku")
            print("--- KEUANGAN & TRANSAKSI ---")
            print("8. Pusat Keuangan (Top-Up, Beli Bab, Pencairan)")
            print("9. Logout")
            
            pilihan = input("Pilih menu: ")
            
            if pilihan == '1':
                user.lihat_profil(session_user)
            elif pilihan == '2':
                story.lihat_semua_published()
            elif pilihan == '3':
                story.baca_chapter(session_user['user_id'])
            elif pilihan == '4':
                story.buat_story(session_user['user_id'])
            elif pilihan == '5':
                story.buat_chapter(session_user['user_id'])
            elif pilihan == '6':
                character.menu_karakter(session_user['user_id'])
            elif pilihan == '7':
                story.lihat_story_ku(session_user['user_id'])
            elif pilihan == '8':
                transaction.menu_transaksi(session_user['user_id'])
            elif pilihan == '9':
                session_user = None
                print("Berhasil keluar akun.")
            else:
                print("Pilihan tidak valid.")


if __name__ == "__main__":
    main_menu()