# File: main.py
import user
import story
import character
import transaction
from story import *

session_user = None

def main_menu():
    global session_user
    
    while True:
        print("\n==========================================")
        print(" STORYFORGE: PLATFORM FIKSI ALL-IN-ONE ")
        print("==========================================")
        
        if not session_user:
            print("1. Register Akun Baru")
            print("2. Login Aplikasi")
            print("0. Keluar Aplikasi")
            pilihan = input("Pilih menu: ")
            
            if pilihan == '1': 
                user.register()
            elif pilihan == '2': 
                session_user = user.login()
            elif pilihan == '0': 
                print("Terima kasih telah menggunakan StoryForge!")
                break
        else:
            print(f"Halo, {session_user['username']}! Selamat datang di Beranda.")
            print("\n--- PROFIL & AKUN ---")
            print("1. Lihat Profil & Informasi Saldo Dompet")
            print("\n--- MODE PEMBACA ---")
            print("2. Eksplorasi Judul Cerita (Published)")
            print("3. Baca Bab Cerita & Akses Lore")
            print("\n--- MODE PENULIS ---")
            print("4. Buat Cerita Baru (Draft)")
            print("5. Tambah Bab Baru (Set Harga Konten Per Bab)")
            print("6. Kelola Dokumentasi Lore Karakter")
            print("7. Lihat Daftar Karyaku")
            print("8. Publish Cerita ke Publik")            # ← baru, pindah ke sini
            print("\n--- KEUANGAN & EKONOMI PLATFORM ---")
            print("9. Menu Transaksi Keuangan (Top-Up / Beli Bab / Tarik Saldo)")   # geser jadi 9
            print("10. Logout Akun")                        # logout jadi 10
            
            pilihan = input("\nPilih menu: ")
            
            if pilihan == '1':
                user.lihat_profil(session_user)
            elif pilihan == '2':
                story.lihat_semua_published()
            elif pilihan == '3':
                story.baca_chapter(session_user)
            elif pilihan == '4':
                story.buat_story(session_user['user_id'])
            elif pilihan == '5':
                story.buat_chapter(session_user['user_id'])
            elif pilihan == '6':
                character.menu_karakter(session_user['user_id'])
            elif pilihan == '7':
                story.lihat_story_ku(session_user['user_id'])
            elif pilihan == '8':
                story.publish_story(session_user['user_id'])
            elif pilihan == '9':
                transaction.menu_transaksi(session_user['user_id'])
            elif pilihan == '10':
                session_user = None
                

if __name__ == "__main__":
    main_menu()