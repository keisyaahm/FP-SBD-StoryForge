# StoryForge - Platform Fiksi All-in-One (Final Project SBD)

StoryForge adalah platform penulisan dan pembacaan fiksi berbasis CLI (*Command Line Interface*). Proyek ini mengimplementasikan **Arsitektur Hybrid Database**, mengintegrasikan **MySQL** untuk integritas data transaksional yang ketat dan **MongoDB** untuk fleksibilitas skema konten naskah serta metadata karakter yang dinamis.

## Daftar Isi

1. [Deskripsi Proyek](https://www.google.com/search?q=%231-deskripsi-proyek)
2. [Arsitektur Sistem (Hybrid Database)](https://www.google.com/search?q=%232-arsitektur-sistem)
3. [Struktur Direktori & Penjelasan Modul](https://www.google.com/search?q=%233-struktur-direktori--penjelasan-modul)
4. [Alur Kerja Sistem (Flow)](https://www.google.com/search?q=%234-alur-kerja-sistem-flow)
5. [Penanganan Kasus Ekstrem (Edge Cases)](https://www.google.com/search?q=%235-penanganan-kasus-ekstrem-edge-cases)
6. [Panduan Instalasi & Setup](https://www.google.com/search?q=%236-panduan-instalasi--setup)

---

## 1. Deskripsi Proyek

StoryForge memfasilitasi dua peran utama pengguna: **Penulis** dan **Pembaca**. Penulis dapat merancang cerita, mengelola draf bab, menetapkan harga premium (*monetisasi*), serta membangun ensiklopedia karakter (*Lore*). Pembaca dapat membeli koin, membaca bab premium, mencari informasi karakter secara interaktif (*pop-up*), dan memberikan komentar langsung pada setiap paragraf.

## 2. Arsitektur Sistem

* **MySQL (Relational DB):** Menangani data esensial yang membutuhkan prinsip ACID (*Atomicity, Consistency, Isolation, Durability*). Ini mencakup Autentikasi Pengguna, Hak Cipta Karya (Story & Chapter Metadata), dan Sistem Transaksi Keuangan. MySQL dioptimalkan menggunakan *Trigger* dan *Stored Procedure* untuk otomasi di sisi *back-end*.
* **MongoDB (NoSQL DB):** Menangani data yang bentuknya bervariasi (*schema-less*) dan berlapis (*nested*). Ini mencakup penyimpanan naskah cerita (*array of paragraphs*), fitur komentar per-paragraf (*embedded documents*), serta detail atribut karakter yang dinamis.

---

## 3. Struktur Direktori & Penjelasan Modul

Aplikasi ini dibagi menjadi beberapa modul berbasis fungsi (*separation of concerns*):

### `main.py` (Sistem Inti & Routing)

*File* utama yang menyatukan seluruh modul. Berfungsi sebagai *controller* antarmuka CLI.

* **Fungsi Utama:** Mengatur *session* pengguna saat *login* dan menampilkan hierarki menu berdasarkan peran (Akun, Pembaca, Penulis, Transaksi).

### `db.py` (Konfigurasi Jaringan)

Modul independen untuk membangun jembatan koneksi ke pangkalan data.

* **Fungsi Utama:** Menyediakan `get_mysql_connection()` (port 3308) dan `get_mongo_database()` (URI 27017) agar tidak terjadi redundansi kode koneksi di *file* lain.

### `user.py` (Modul Autentikasi & Keamanan)

Menangani pintu masuk aplikasi dan keamanan identitas.

* **Fungsi `hash_password`:** Memastikan kata sandi dienkripsi menggunakan SHA-256 sebelum masuk ke MySQL.
* **Fungsi `register` & `login`:** Memvalidasi input kosong, memblokir simbol ilegal (*Alphanumeric Check*), dan menolak duplikasi email.
* **Fungsi `lihat_profil`:** Menarik data saldo koin (*coin_balance*) dan pendapatan (*author_balance*) secara *real-time*.

### `story.py` (Modul Manajemen Naskah Hibrida)

Mesin utama untuk pengelolaan cerita, bab, dan mesin pembaca.

* **Fungsi `buat_story` & `publish_story`:** Mengelola metadata karya (Judul, Sinopsis, Genre) di MySQL dengan sistem status (*Draft* / *Published*).
* **Fungsi `buat_chapter`:** Modul hibrida kompleks. Menyimpan metadata harga ke MySQL, mengambil `lastrowid`, lalu meminta penulis mengetik paragraf cerita secara *looping* untuk dibungkus ke dalam JSON Array dan dikirim ke MongoDB.
* **Fungsi `baca_chapter`:** Memverifikasi status kepemilikan bab Premium di MySQL. Jika lolos, ia menarik isi paragraf dari MongoDB. Di sinilah **Mesin Pop-Up Lore** (pencarian teks karakter *case-insensitive*) dan **Mesin Komentar** berada.
* **Fungsi `tambah_komentar` & `lihat_komentar`:** Memanfaatkan perintah `$push` MongoDB untuk menyisipkan komentar secara spesifik ke indeks paragraf tertentu.

### `character.py` (Modul Manajemen Lore Dinamis)

Pengelolaan ensiklopedia karakter yang aman dan fleksibel.

* **Fungsi `is_story_owner`:** Perisai keamanan (*helper*) untuk memastikan pengguna hanya bisa mengelola karakter pada karya miliknya sendiri.
* **Fungsi CRUD Karakter:** Menyimpan ID dan nama dasar di MySQL sebagai relasi/jangkar, sementara atribut pelengkap (Senjata, Ras, Kelemahan) disimpan sebagai *Key-Value pairs* bebas di MongoDB.
* Fitur **Hybrid Sync**: Jika nama karakter diubah di MongoDB, sistem akan otomatis mengirim kueri `UPDATE` untuk mengubah nama di MySQL juga.

### `transaction.py` (Modul Ekonomi Digital)

Mengelola perputaran koin dalam ekosistem.

* **Fungsi `top_up`:** Mengonversi Rupiah menjadi koin pembaca dengan validasi kelipatan minimal dan maksimal.
* **Fungsi `beli_bab`:** Mengeksekusi transaksi dengan verifikasi "Apakah bab sudah pernah dibeli?" untuk mencegah *double-charge*.
* **Fungsi `request_withdrawal`:** Mencatat pengajuan pencairan saldo penulis ke tabel MySQL.

### `sinkron_dummy.py` & `query.sql` (Inisialisasi Database)

* `query.sql`: Membangun kerangka MySQL dari nol. Memuat tabel *user, story, chapter, transaction*, lengkap dengan **Triggers** (otomasi pemotongan koin pembelian) dan **Stored Procedures** (logika pencairan dana manual oleh Admin).
* `sinkron_dummy.py`: *Script* untuk memasukkan teks narasi dan struktur JSON data awal ke MongoDB agar selaras dengan ID di MySQL.

---

## 4. Alur Kerja Sistem (Flow)

1. **Flow Autentikasi:** Pengguna baru mendaftar (Sandi di-hash) -> Login -> Sistem menyimpan identitas di global `session_user`.
2. **Flow Penulis:** Membuat Cerita (Draft) -> Menambah Bab (Metadata di SQL, Konten paragraf-berulang di Mongo) -> Membuat Lore Karakter -> Memublikasikan (Publish) Cerita ke publik.
3. **Flow Pembaca:** Top-Up Koin -> Beli Bab Premium (Trigger SQL memotong saldo pembaca dan mentransfer ke penulis, mencatat di *history*) -> Baca Bab -> Mengetik nama karakter untuk *Pop-up Lore* -> Menambahkan Komentar Inline pada paragraf pilihan.
4. **Flow Pencairan (Withdrawal):** Penulis mengajukan *withdrawal* -> Status masuk sebagai 'pending' -> Admin database menjalankan `CALL approve_withdrawal(ID)` di MySQL -> Saldo dipotong dan dicatat secara aman dalam 1 transaksi SQL.

---

## 5. Penanganan Kasus Ekstrem (Edge Cases)

Platform ini telah dilindungi dari berbagai celah logika (*bug*):

1. **Sabotase Lintas-Akun Terblokir:** Pengguna tidak bisa lagi menebak `story_id` untuk menambahkan bab atau mengubah *lore* karakter milik penulis lain. Fungsi `is_story_owner` mengunci hak akses mutlak berdasarkan `user_id`.
2. **Pencegahan Defisit (Overdraft):** Fungsi Top-Up dan Withdrawal dijaga dengan validasi batas bawah dan atas yang ketat di level Python, dan dipertebal dengan pengecekan saldo (`IF balance < amount`) di dalam MySQL *Stored Procedure*.
3. **Bebas Penulisan Tanpa Batas:** Bug penulis yang hanya bisa menulis satu paragraf telah ditangani dengan *while loop*, memungkinkan penulis mengetik paragraf sebanyak mungkin hingga mereka mengetik *command* 'selesai'.
4. **Penanganan Sinkronisasi Anomali:** MongoDB Compass membedakan huruf besar/kecil. Untuk pencarian karakter agar tidak *error*, Python men-*downcast* (*lower*) nama saat diinput dan saat dicari, memastikan akurasi data 100%.

---

## 6. Panduan Instalasi & Setup

1. Buka XAMPP, nyalakan **Apache** dan **MySQL**.
2. Masuk ke `http://localhost/phpmyadmin/`, eksekusi/Import seluruh baris dari `query.sql`.
3. Buka **MongoDB Compass**, sambungkan ke koneksi lokal (`mongodb://localhost:27017/`).
4. Buka terminal IDE Anda, instal modul yang dibutuhkan: `pip install mysql-connector-python pymongo`.
5. Sinkronkan data awal ke MongoDB dengan perintah: `python sinkron_dummy.py`
6. Mulai jalankan aplikasi utama: `python main.py`
