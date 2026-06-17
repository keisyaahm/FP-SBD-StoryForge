# File: sinkron_dummy.py
from db import get_mongo_database

def eksekusi_sinkronisasi():
    print("Membuka koneksi ke MongoDB...")
    db = get_mongo_database()
    
    # 1. Mengisi Teks Naskah untuk Bab 1, 2, dan 3
    chapters_collection = db["chapters_content"]
    chapters_collection.delete_many({"chapter_id": {"$in": [1, 2, 3]}}) 
    
    dummy_chapters = [
        {
            "chapter_id": 1,
            "paragraf": [
                {"urutan_paragraf": 1, "teks": "Dalam novel Laut Bercerita karya Leila S. Chudori, tokoh utama yang menceritakan kisah adalah Biru Laut Wibisono (mahasiswa Sastra Inggris UGM yang idealis) dan adiknya, Asmara Jati (mahasiswa sains yang rasional).", "komentar_inline": []},
                {"urutan_paragraf": 2, "teks": "Kisah ini berfokus pada sekelompok aktivis mahasiswa yang memperjuangkan kebebasan dan demokrasi di masa Orde Baru (tahun 1991–1998). Melalui sudut pandang Laut dan Asmara, pembaca diajak menelusuri kisah persahabatan, pengkhianatan dari dalam kelompok, penyiksaan, hingga kepedihan keluarga yang kehilangan anggota keluarga mereka akibat penculikan paksa.", "komentar_inline": []},
                {"urutan_paragraf": 3, "teks": "Novel ini terinspirasi dari kisah nyata para korban penculikan aktivis 1998 dan menjadi salah satu karya sastra yang sangat populer.", "komentar_inline": []}
            ]
        },
        {
            "chapter_id": 2,
            "paragraf": [
                {"urutan_paragraf": 1, "teks": "Malam pengkhianatan itu akhirnya tiba. Tidak ada yang menduga bahwa salah satu dari mereka sendiri yang menjadi informan.", "komentar_inline": []},
                {"urutan_paragraf": 2, "teks": "Gusti menatap kosong ke arah pintu yang baru saja didobrak. Semuanya hancur berkeping-keping.", "komentar_inline": []}
            ]
        },
        {
            "chapter_id": 3,
            "paragraf": [
                {"urutan_paragraf": 1, "teks": "Sinyal Penjaga Kota Digital mulai berkedip merah. Ada penyusup di sektor 7.", "komentar_inline": []}
            ]
        }
    ]
    chapters_collection.insert_many(dummy_chapters)
    print("Berhasil: Teks Bab 1, 2, dan 3 telah ditambahkan ke MongoDB!")
    
    # 2. Mengisi Lore Karakter
    character_collection = db["character_lores"]
    character_collection.delete_many({"story_id": 1})
    
    dummy_lores = [
        {
            "character_id": 1, 
            "story_id": 1, 
            "character_name": "biru laut", 
            "Peran": "Tokoh sentral / Aktivis", 
            "Latar Belakang": "Mahasiswa Sastra Inggris UGM yang idealis",
            "Kisah": "Mendirikan kelompok diskusi di Seyegan, bergerak melawan rezim, hingga disekap dan disiksa."
        },
        {
            "character_id": 2, 
            "story_id": 1, 
            "character_name": "asmara jati", 
            "Peran": "Adik Laut", 
            "Latar Belakang": "Mahasiswa sains yang rasional",
            "Kisah": "Narator yang menceritakan penderitaan keluarga korban dan terus mencari keadilan."
        },
        {
            "character_id": 3, 
            "story_id": 1, 
            "character_name": "kinan", 
            "Peran": "Anggota Organisasi", 
            "Latar Belakang": "Anggota Winatra dan Wirasena",
            "Kisah": "Memiliki andil besar dalam menceritakan dinamika pergerakan mahasiswa."
        },
        {
            "character_id": 4, 
            "story_id": 1, 
            "character_name": "alex", 
            "Peran": "Anggota Organisasi", 
            "Latar Belakang": "Anggota Winatra dan Wirasena",
            "Kisah": "Rekan seperjuangan dalam dinamika pergerakan mahasiswa."
        },
        {
            "character_id": 5, 
            "story_id": 1, 
            "character_name": "gusti", 
            "Peran": "Karakter Pendukung", 
            "Latar Belakang": "Rekan dalam kelompok perjuangan",
            "Kisah": "Kisahnya berujung pada pengkhianatan di dalam kelompok."
        },
        {
            "character_id": 6, 
            "story_id": 1, 
            "character_name": "anjani", 
            "Peran": "Kekasih Biru Laut", 
            "Latar Belakang": "Seorang pelukis",
            "Kisah": "Menceritakan sisi lain tentang kehilangan dan kesetiaan."
        }
    ]
    character_collection.insert_many(dummy_lores)
    print("Berhasil: Lore Karakter (Biru Laut, Asmara, Kinan, dll) telah ditambahkan ke MongoDB!")
    print("\nProses sinkronisasi selesai! Sekarang jalankan 'python main.py'.")

if __name__ == "__main__":
    eksekusi_sinkronisasi()