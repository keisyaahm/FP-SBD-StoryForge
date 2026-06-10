# File: main.py
import user
import story

def main_menu():
    session_user = None
    
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
            print("6. Lihat Daftar Karyaku (Draft & Published)")
            print("7. Publish Bab Draft")
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
                story.lihat_story_ku(session_user['user_id'])
            elif pilihan == '7':
                story.publish_chapter_draft()
            elif pilihan == '9':
                session_user = None
                print("Berhasil keluar akun.")

if __name__ == "__main__":
    main_menu()