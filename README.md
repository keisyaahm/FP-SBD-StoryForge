# StoryForge - Platform Fiksi All-in-One

Aplikasi antarmuka baris perintah (CLI) berbasis Python untuk platform penulisan dan pembacaan fiksi. Proyek ini menerapkan Hybrid Database yang menggabungkan MySQL (untuk keamanan transaksi dan relasi data) dan MongoDB (untuk fleksibilitas skema teks naskah dan lore karakter).

## Struktur Proyek

```text
StoryForge/
├── db.py               # Konfigurasi koneksi ganda ke MySQL dan MongoDB
├── main.py             # Entry point aplikasi dan sistem routing menu utama
├── user.py             # Modul autentikasi (Register/Login) dan manajemen profil
├── story.py            # Modul manajemen karya (draft/publish) dan mesin pembacaan
├── karakter.py         # Modul interaksi lore karakter dengan skema dinamis
├── query_sql.txt       # DDL Skema relasional, Trigger, View, dan data awal
└── README.md           # Dokumentasi cara penggunaan

```

## Syarat

1. Python versi 3.x
2. XAMPP (untuk menjalankan server Apache dan MySQL)
3. MongoDB Compass / MongoDB lokal aktif

## Setup

### 1. Instalasi Dependensi

Buka terminal pada folder project, lalu instal penghubung database:

```bash
pip install mysql-connector-python pymongo

```

### 2. Persiapan Database (MySQL & MongoDB)

Aplikasi ini membutuhkan wadah database agar tidak terjadi error koneksi

* **MySQL:**
1. Buka aplikasi XAMPP Control Panel, lalu klik **Start** pada Apache dan MySQL.
2. Buka browser dan akses `http://localhost/phpmyadmin/`.
3. Buat database baru bernama `fiction_platform`.
4. Masuk ke tab SQL, salin seluruh isi dari file `query_sql.txt`, lalu klik tombol eksekusi/Go.

* **MongoDB:**
1. Buka aplikasi MongoDB Compass.
2. Biarkan URI default (`mongodb://localhost:27017/`) dan klik **Connect**.
3. Anda tidak perlu membuat tabel manual di sini. MongoDB akan otomatis membuat koleksi ketika Python mengirimkan data teks atau lore karakter.


### 3. Konfigurasi Port Lokal

Secara bawaan, MySQL berjalan di port 3306. Jika laptop yang digunakan menjalankan MySQL di port yang berbeda (misalnya 3307/8), buka file `db.py` dan sesuaikan nilainya:

```python
def get_mysql_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306, # Ubah angka ini sesuai port MySQL di XAMPP masing-masing
        user="root",
        password="",
        database="fiction_platform"
    )

```

### 4. Menjalankan Aplikasi

Setelah database menyala dan dependensi terinstal, jalankan file utama lewat terminal:

```bash
python main.py

```

Apk CLI StoryForge akan langsung berjalan dan siap digunakan.
