# StoryForge - Platform Fiksi All-in-One

StoryForge adalah platform penulisan dan pembacaan fiksi berbasis CLI (*Command Line Interface*). Proyek ini mengimplementasikan **Arsitektur Hybrid Database**, mengintegrasikan **MySQL** untuk integritas data transaksional yang ketat dan **MongoDB** untuk fleksibilitas skema konten naskah serta metadata karakter yang dinamis.

## Struktur Proyek

```text
StoryForge/
├── db.py               # Konfigurasi koneksi ganda ke MySQL dan MongoDB
├── main.py             # Entry point dan sistem routing menu utama
├── user.py             # Modul autentikasi (Hashing SHA-256) dan profil user
├── story.py            # Manajemen karya, bab (hybrid), dan mesin pembacaan
├── character.py        # CRUD lore karakter (MongoDB) dan statistik
├── transaction.py      # Modul keuangan (Top-up, Pembelian, Withdrawal)
├── sinkron_dummy.py    # Skrip sinkronisasi data teks cerita & karakter
└── query.sql           # DDL MySQL, Triggers, Views, dan data dummy

```

## Fitur Utama

* **Autentikasi Aman:** Perlindungan kata sandi menggunakan hashing SHA-256.
* **Hybrid Storage Engine:** Metadata terstruktur di MySQL; konten bab dan lore karakter di MongoDB.
* **Sistem Ekonomi Token:** Top-up koin (Rp 5rb-1jt), pembelian bab premium, dan penarikan dana penulis.
* **Trigger & View (Database Level):** Otomasi pemotongan koin & perhitungan pendapatan penulis secara *real-time* di sisi server.
* **Dinamis Lore:** *Pop-up* informasi karakter berbasis pencarian *schema-less* di MongoDB.

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
4. Klik menu **Import**, pilih file `query.sql`, dan eksekusi.


* **MongoDB:**
1. Jalankan MongoDB Compass dan hubungkan ke `mongodb://localhost:27017/`.
2. Jalankan skrip sinkronisasi di terminal untuk memetakan konten ke database:
```bash
python sinkron_dummy.py

```





### 3. Konfigurasi Koneksi

Pastikan konfigurasi `port` pada file `db.py` sesuai dengan pengaturan XAMPP Anda (umumnya 3306 atau 3308):

```python
def get_mysql_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3308, 
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

## Panduan Operasional

1. **Registrasi & Login:** Gunakan menu 1 dan 2. Kata sandi akan di-*hash* otomatis untuk keamanan.
2. **Menjadi Penulis:** Gunakan menu 4 hingga 7 untuk membuat cerita, menambah bab (otomatis tersinkron ke MongoDB), dan mengelola lore karakter.
3. **Menjadi Pembaca:** Gunakan menu 2 dan 3 untuk membaca karya. Jika bab berstatus *Premium*, pastikan saldo koin mencukupi.
4. **Menu Transaksi (Menu 8):**
* **Top-Up:** Lakukan top-up (min Rp 5.000, maks Rp 1.000.000).
* **Beli Bab:** Memotong saldo secara otomatis menggunakan MySQL Trigger.
* **Penarikan (Withdrawal):** Penulis dapat mengajukan penarikan saldo. Admin (via phpMyAdmin) dapat menyetujui dengan mengubah status menjadi `approved`, yang akan otomatis memotong saldo penulis.


5. **Pop-up Lore:** Saat membaca bab, masukkan nama karakter yang terdaftar (case-insensitive) untuk memunculkan detail atribut karakter secara instan.
