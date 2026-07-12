# Laporan Final Project - Simple LMS Extended Backend

## 1. Identitas
- **Nama:** Danendra Farrel Haryo Wibowo 
- **NIM:** A11.2023.15025
- **Kelas:** A11.4618 : Bapak Fahri Firdausillah
- **URL Repository:** https://github.com/DFNexus/UAS_SSVR

## 2. Deskripsi Project
Proyek **Simple LMS API** ini dikembangkan sebagai fondasi *backend* sistem manajemen pembelajaran (Learning Management System) modern. Proyek ini dibangun untuk memenuhi kriteria utama dan difokuskan pada kelengkapan pengalaman belajar pengguna, sehingga saya mengambil secara utuh **Paket 1 - LMS Experience**. Sistem ini menangani autentikasi, hierarki materi pembelajaran, pelacakan progres belajar, hingga sistem analitik agregasi pada dashboard mahasiswa.

## 3. Fitur Dasar yang Sudah Berjalan
- Authentication JWT (Register, Login, Refresh Token, Profile/Me).
- Role-based access control (RBAC): Admin, Instructor, Student.
- Course API (CRUD dengan permission ketat per role).
- Curriculum bertingkat: Course, Section, Lesson.
- Enrollment student ke course.
- Progress belajar dinamis per lesson.

## 4. Fitur Tambahan yang Dipilih: Paket 1 - LMS Experience
| No | Fitur | Kategori | Poin | Status |
|---|---|---|---|---|
| 1 | Search, filter, dan sorting course lanjutan | A | 12 | Selesai |
| 2 | Rating, review, dan wishlist course | A | 12 | Selesai |
| 3 | Curriculum dan progress belajar detail | A | 15 | Selesai |
| 4 | Student dashboard | A | 12 | Selesai |

## 5. Penjelasan Implementasi & Keputusan Desain
Aplikasi ini dibangun menggunakan **Django 5.2**, **Django Ninja**, **PostgreSQL 16**, dan **Redis 7**. Berikut adalah penjelasan implementasi fitur tambahannya:

- **Fitur 1 - Search, Filter, dan Sorting Lanjutan:** Pencarian mendukung teks (judul/deskripsi), penyaringan berdasarkan kategori, instruktur, dan tingkat kesulitan. Pengurutan `popular` dihitung menggunakan `annotate(Count)` ke database sehingga efisien dan terhindar dari *N+1 query*.
- **Fitur 2 - Rating, Review, dan Wishlist:** Sistem validasi memastikan hanya pengguna terdaftar (*enrolled*) yang dapat memberikan ulasan pada suatu kursus. Rata-rata rating dihitung menggunakan `Avg` dari Django ORM dan disuntikkan langsung saat memanggil detail Course.
- **Fitur 3 - Curriculum dan Progress Tracking:** Menerapkan struktur hierarki `Course -> Section -> Lesson`. Sistem dirancang untuk mampu menghitung persentase progres kelulusan tiap bagian (*section*) maupun total keseluruhan kursus secara dinamis dan presisi (0.0% hingga 100.0%).
- **Fitur 4 - Student Dashboard:** Menyajikan data agregasi kompleks seperti status kursus aktif, kursus yang sudah selesai, metrik total pembelajaran, serta algoritma untuk merekomendasikan kursus populer yang belum didaftar siswa.

## 6. Cara Menjalankan Project
Proyek ini didesain sepenuhnya menggunakan arsitektur *containerized*.
1. Clone repository: `git clone https://github.com/DFNexus/UAS_SSVR.git`
2. Masuk ke direktori: `cd UAS-SSVR`
3. Salin konfigurasi environment: `cp .env.example .env`
4. Jalankan aplikasi: `docker compose up -d`
5. Tunggu sekitar 30 detik hingga seluruh *service* (Web, DB, Redis, Frontend) berstatus *healthy*.
6. Akses dokumentasi API di: `http://localhost:8000/api/docs`

## 7. Akun Demo
Setelah Anda menjalankan seeding (`docker compose exec web python manage.py seed_demo_data`), Anda bisa login menggunakan akun berikut:
| Role | Username | Password |
|---|---|---|
| Admin | admin | admin123 |
| Instructor | instructor1 | instructor123 |
| Instructor | instructor2 | instructor123 |
| Student | student1 | student123 |
| Student | student2 | student123 |
| Student | student3 | student123 |

## 8. Endpoint Penting
- `POST /api/auth/login` - Login dan mendapatkan Token JWT
- `GET /api/courses/` - Mencari, memfilter, dan mengurutkan kursus
- `GET /api/courses/{id}` - Menampilkan detail kursus beserta kurikulum dan rata-rata rating
- `POST /api/enrollments/` - Melakukan pendaftaran kursus (Student)
- `POST /api/lessons/{id}/complete` - Menandai materi selesai dibaca
- `GET /api/courses/{id}/progress` - Mengecek persentase kelulusan
- `POST /api/courses/{id}/reviews` - Memberikan rating dan ulasan
- `GET /api/dashboard/student` - Menampilkan dasbor agregasi siswa

## 9. Screenshot / Bukti Pengujian
- GET /api/dashboard/student
(image.png)

- GET /api/courses 
(image-1.png)

- Postman 
pada beberapa pengujian ada kode 400 itu bukan error in the bad way, tetapi itu adalah error handling karna sebelumnya saya suidah melakukan review dan enroll course yang sama jadi saya balikkan ke kode 400. untuk penjelasannya dapat saya jelaskan pada video presentasi
(image-2.png)
(image-3.png)

- get /api/course
(image-4.png)

- GET /api/courses/{id}/progress.
(image-5.png)

## 10. Cara Menjalankan Test Automatis (Reliabilitas)
Aplikasi dilindungi oleh *Automated Unit Testing* yang berjalan di atas *database in-memory* (sqlite3) sehingga sangat cepat:
```bash
docker compose exec web pytest --cov=apps --cov-report=term-missing
```

## 11. Kendala dan Solusi
**Kendala Utama:** Menangani ancaman *N+1 Query* pada database, terutama di fitur penghitungan progres dan *dashboard* karena banyaknya relasi antar tabel (Course, Section, Lesson, Enrollment).
**Solusi:** Saya secara agresif menggunakan teknik *fetching* cerdas dari Django ORM, yaitu `.select_related()` (untuk relasi ForeignKey) dan `.prefetch_related()` (untuk relasi Reverse/Many-to-Many). Beban komputasi agregasi dialihkan ke mesin database menggunakan `.annotate()`, sehingga konsumsi memori aplikasi tetap rendah dan performa sangat cepat.

## 12. Kesimpulan
Mengerjakan proyek ini membuktikan bahwa sebuah *backend* RESTful API dapat dibangun secara terstruktur dan berperforma tinggi jika menerapkan *Clean Architecture* (Separation of Concerns). Dengan memisahkan logika bisnis (di `services.py`) dari antarmuka rute (di `api.py`), serta diisolasi menggunakan Docker, kode menjadi sangat mudah dipelihara (*maintainable*), di-test, dan siap diskalakan.
