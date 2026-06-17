# StoryForge - Platform Fiksi All-in-One

StoryForge adalah platform penulisan dan pembacaan fiksi berbasis CLI (Command Line Interface). Aplikasi ini menggunakan arsitektur Hybrid Database yang mengintegrasikan MySQL untuk integritas data transaksi dan MongoDB untuk fleksibilitas penyimpanan konten teks serta data lore karakter yang dinamis.

## Struktur Proyek

```text
StoryForge/
├── db.py               # Konfigurasi koneksi MySQL dan MongoDB
├── main.py             # Entry point dan routing menu aplikasi
├── user.py             # Autentikasi (Register/Login) dan profil user
├── story.py            # Manajemen karya, bab (hybrid), dan mesin baca
├── karakter.py         # CRUD lore karakter (MongoDB) dan statistik
├── transaktion.py      # Modul keuangan (Top-up, Pembelian, Withdrawal)
├── query_sql.txt       # DDL MySQL, Trigger, View, dan data awal
└── README.md           # Dokumentasi ini

```

## Fitur Utama

* **Autentikasi Aman:** Password disimpan menggunakan algoritma Hashing SHA-256.
* **Hybrid Storage:** Metadata cerita di MySQL, konten naskah bab di MongoDB.
* **Sistem Ekonomi:** Top-up koin, pembelian bab premium, dan penarikan saldo penulis.
* **Dinamis Lore:** Pop-up informasi karakter berbasis data dokumen fleksibel di MongoDB.
* **Workflow Penulis:** Manajemen draf cerita dan sistem publish bab yang terintegrasi.

## Persyaratan Sistem

1. Python 3.x
2. XAMPP (Apache & MySQL)
3. MongoDB Compass / Server MongoDB lokal

## Setup dan Instalasi

### 1. Instalasi Dependensi

Buka terminal pada direktori proyek, jalankan:

```bash
pip install mysql-connector-python pymongo

```

### 2. Persiapan Database

* **MySQL:**
1. Jalankan Apache dan MySQL di XAMPP.
2. Akses `http://localhost/phpmyadmin/`.
3. Buat database baru bernama `fiction_platform`.
4. Klik menu **Import**, pilih file `query_sql.txt`, dan eksekusi.


* **MongoDB:**
1. Jalankan MongoDB Compass.
2. Hubungkan ke URI `mongodb://localhost:27017/`. Database akan terbuat otomatis saat aplikasi dijalankan.



### 3. Konfigurasi Koneksi

Pastikan port pada file `db.py` sesuai dengan pengaturan XAMPP Anda:

```python
def get_mysql_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3308, # Sesuaikan dengan port MySQL di XAMPP Anda
        user="root",
        password="",
        database="fiction_platform"
    )

```

## Menjalankan Aplikasi

Jalankan aplikasi dengan perintah:

```bash
python main.py

```

## Panduan Penggunaan untuk Pengguna

1. **Registrasi & Login:** Gunakan menu 1 dan 2. Kata sandi Anda akan dienkripsi secara otomatis.
2. **Menjadi Penulis:** Gunakan menu 4, 5, dan 6 untuk membuat cerita, menambah bab (Hybrid), dan mendata karakter.
3. **Menjadi Pembaca:** Gunakan menu 2 dan 3 untuk membaca karya. Jika bab berstatus Premium, pastikan Anda memiliki koin yang cukup.
4. **Transaksi:** Gunakan menu 8 untuk melakukan Top-Up koin atau menarik pendapatan (Withdrawal) sebagai penulis.
5. **Pop-up Lore:** Saat membaca bab, Anda dapat mengetik nama karakter yang terdaftar untuk melihat detail atribut karakter tersebut secara instan.

```
tes