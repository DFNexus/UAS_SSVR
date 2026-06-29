# Laporan Arsitektur Teknis: Simple LMS API

## 1. Latar Belakang dan Ruang Lingkup
Proyek **Simple LMS API** dikembangkan sebagai fondasi sistem manajemen pembelajaran (Learning Management System) modern yang difokuskan pada kelengkapan pengalaman belajar pengguna (*student*) dan kapabilitas pengelolaan kursus oleh instruktur.

**Fitur Utama Sistem:**
1. **Search, Filter, dan Sorting Lanjutan**: Mendukung pencarian teks (judul/deskripsi), penyaringan berdasarkan kategori, instruktur, dan tingkat kesulitan, serta pengurutan dinamis (berdasarkan popularitas, waktu dibuat, dll).
2. **Rating, Review, dan Wishlist**: Sistem validasi memastikan hanya pengguna terdaftar (*enrolled*) yang dapat memberikan ulasan pada suatu kursus. Terdapat pula fitur Wishlist untuk menyimpan kursus favorit.
3. **Curriculum dan Progress Tracking**: Menerapkan struktur hierarki `Course -> Section -> Lesson`. Sistem dirancang untuk mampu menghitung persentase progres penyelesaian tiap bagian (*section*) maupun total keseluruhan kursus secara dinamis dan efisien.
4. **Student Dashboard**: Menyajikan data agregasi kompleks seperti status kursus aktif, kursus yang sudah selesai, metrik total pembelajaran, serta algoritma sederhana untuk rekomendasi kursus (kursus populer yang belum terdaftar).

---

## 2. Tumpukan Teknologi (Tech Stack)

Aplikasi ini dibangun di atas tumpukan teknologi modern yang kuat dan mudah diperluas (*scalable*):
- **Web Framework**: **Django 5.2** bertindak sebagai fondasi utama sistem ORM (*Object-Relational Mapping*) dan penyedia struktur *backend*.
- **API Layer**: **Django Ninja** diadopsi karena memiliki arsitektur berbasis *Pydantic* yang menjamin proses validasi tipe-data yang ketat (*type-safe*), eksekusi yang jauh lebih cepat, dan secara otomatis menghasilkan dokumentasi *OpenAPI/Swagger*.
- **Database Utama**: **PostgreSQL 16**. Dipilih karena dukungannya yang matang terhadap relasi data yang kompleks serta kecepatan eksekusi kueri agregasi (seperti perhitungan *Count* dan *Avg*).
- **Cache & Message Broker**: **Redis 7**. Saat ini disiapkan sebagai fondasi *caching*, yang di masa depan sangat ideal untuk diperluas sebagai antrean tugas latar belakang (*background tasks*) dengan Celery.
- **Infrastruktur**: Seluruh layanan diisolasi dan diorkestrasi menggunakan **Docker Compose**, menjamin sistem memiliki reliabilitas tinggi dan dapat berjalan identik di berbagai mesin (mengatasi masalah klasik *"It works on my machine"*).

---

## 3. Keputusan Desain dan Praktik Terbaik (Best Practices)

Untuk memastikan skalabilitas, keamanan, dan kemudahan pemeliharaan kode (*maintainability*), proyek ini menerapkan berbagai pola desain perangkat lunak (*design patterns*) tingkat lanjut:

1. **Pemisahan Konsep (Separation of Concerns)**
   Struktur proyek dipecah menjadi **8 modul aplikasi mandiri** (seperti `users`, `categories`, `courses`, `enrollments`, dsb). Logika bisnis yang kompleks tidak diletakkan di *View/API layer*, melainkan diisolasi ke dalam modul `services.py` (sebagai contoh, fungsi kalkulasi progres `calculate_progress()` dipisahkan murni sebagai fungsi *service*).

2. **Keamanan Konfigurasi (Fail-Fast Environment Variables)**
   Aplikasi menerapkan sistem yang sangat ketat terhadap pembacaan variabel lingkungan yang sensitif (`SECRET_KEY`, `DB_USER`, `DB_PASSWORD`). Tidak ada nilai bawaan (*default fallback*) di dalam kode utama. Jika file `.env` hilang atau tidak dikonfigurasi dengan benar di server *production*, Django akan langsung menolak untuk menyala (*Fail-Fast*) melalui eksepsi `ImproperlyConfigured`. Pendekatan ini secara drastis mengurangi risiko sistem berjalan dalam kondisi rentan diretas.

3. **Efisiensi Kueri Database (Query Optimization)**
   Mengingat sistem LMS sangat rentan dengan hambatan performa akibat *N+1 Query* (karena banyaknya relasi antar tabel), sistem ini menggunakan teknik *fetching* cerdas:
   - Penggunaan `.select_related()` saat melakukan *join* pada *Course* dan *Category*.
   - Penggunaan `.prefetch_related('lessons')` saat memuat dan menghitung progres hierarki kurikulum.
   - Penggunaan `.annotate()` untuk mendelegasikan beban kalkulasi agregat (seperti menghitung rata-rata *rating* atau total jumlah murid) langsung ke mesin *database* PostgreSQL. Ini menjaga beban memori di level aplikasi tetap rendah.
   - Pemanfaatan struktur data `set()` bawaan Python untuk mempercepat algoritma pencarian kecocokan (kompleksitas waktu *O(1)*) pada modul pelacakan status *Lesson* mahasiswa.

4. **Keamanan Autentikasi (JWT + RBAC)**
   Sistem meninggalkan pengelolaan *Session* konvensional berbasis *cookies* dan beralih menggunakan arsitektur **JSON Web Tokens (JWT)** yang *stateless*. Manajemen otorisasi dikontrol secara ketat oleh dekorator kelas khusus (`AdminAuth`, `InstructorAuth`, `StudentAuth`) yang akan secara otomatis memblokir permintaan (HTTP 403) yang melanggar batas wewenang (*Role-Based Access Control*).

---

## 4. Evaluasi Reliabilitas (Testing)

Aplikasi dilindungi oleh serangkaian **Automated Unit Testing** menggunakan `pytest`. Skenario pengujian yang tercakup meliputi:
- Validasi keamanan kontrol akses antar peran pengguna (*RBAC*).
- Skenario penggabungan multivariat dari parameter pencarian (*Search*) dan penyaringan (*Filter*).
- Penanganan dan perlindungan terhadap pendaftaran (*enrollment*) duplikat.
- Validasi algoritma persentase kalkulasi parsial (memastikan akurasi progres 0%, 50%, hingga 100%).

Semua *automated tests* berjalan di atas subsistem *database in-memory* (menggunakan *sqlite3* mode memori) selama proses pengujian. Hal ini memastikan eksekusi tes berjalan sangat cepat tanpa menyentuh atau merusak integritas basis data utama.

## 5. Kesimpulan
Proyek ini membuktikan bahwa sebuah *backend* RESTful API untuk platform pembelajaran daring dapat dibangun secara terstruktur, aman, dan berkinerja tinggi. Kombinasi Django Ninja dan arsitektur *Service Layer* menjadikannya sebuah produk perangkat lunak yang tangguh dan siap untuk diskalakan.
