# Kamus data Perpus Merah Putih

Versi 1.1, 25 Oktober 2026. Dokumen ini melengkapi BRD versi 1.3 dan tiga lembar ERD. Daftar atribut lengkap dihasilkan dari `source/model.json`.

## Cara membaca ERD

PK adalah primary key, FK adalah foreign key, dan UK adalah nilai unik. Tanda `?` berarti boleh kosong.

Notasi Crow's Foot memakai dua garis untuk tepat satu, lingkaran dan garis untuk nol atau satu, serta lingkaran dan tiga cabang untuk nol atau banyak. Simbol di dekat sebuah entitas menunjukkan jumlah baris entitas tersebut yang dapat terhubung dengan satu baris pada sisi seberangnya.

Tiga lembar ERD membahas koleksi dan pengajuan, sirkulasi, serta kebijakan dan petugas. Entitas yang muncul kembali merupakan tabel yang sama. Model lengkap terdiri dari tujuh entitas dan 12 relasi. Setiap foreign key ditampilkan sekali pada salah satu lembar.

## Arti entitas dan batasannya

### Akun

Peran bernilai STUDENT atau LIBRARIAN. Mahasiswa wajib memiliki NIM. NIM pustakawan boleh kosong. Email unik setelah spasi dibuang dan huruf dinormalisasi. Kata sandi disimpan sebagai hash. `student_id` harus menunjuk mahasiswa, sedangkan foreign key petugas dan `created_by` harus menunjuk pustakawan. Validasi peran dilakukan pada layanan aplikasi.

### Kategori dan buku

Satu baris `books` mewakili satu buku fisik per judul. ISBN wajib diisi dan unik setelah dinormalisasi, misalnya dengan membuang spasi dan tanda hubung. ISBN menjadi identitas buku yang digunakan pustakawan. `id` tetap menjadi primary key internal untuk relasi antartabel.

Satu buku berada dalam satu kategori. Kategori boleh belum memiliki buku. Penulis disimpan sebagai teks, sedangkan tahun terbit boleh kosong. `is_active` menentukan apakah buku ditawarkan untuk pengajuan baru. Tidak ada tabel eksemplar, kode inventaris, atribut kondisi per eksemplar, atau jumlah stok.

Ketersediaan merupakan hasil pembacaan transaksi, bukan kolom jumlah:

| Kondisi | Status ketersediaan |
| --- | --- |
| Buku tidak aktif | Nonaktif |
| Buku aktif dan memiliki pinjaman yang belum dikembalikan | Dipinjam |
| Buku aktif dan memiliki pengajuan READY_FOR_PICKUP | Siap diambil |
| Buku aktif tanpa pinjaman aktif maupun pengajuan READY_FOR_PICKUP | Tersedia |

Pengajuan WAITING dan QUEUED belum menahan buku. Satu buku tidak boleh memiliki dua persetujuan pengambilan, dua pinjaman aktif, atau satu persetujuan pengambilan bersamaan dengan pinjaman aktif.

### Pengajuan

Satu pengajuan dimiliki satu mahasiswa dan merujuk langsung ke satu buku melalui `book_id`. Pengajuan yang belum disetujui belum memiliki versi kebijakan pengambilan. Persetujuan mengisi `reviewed_by`, `policy_id`, `reviewed_at`, dan `pickup_deadline`, lalu mengubah status menjadi READY_FOR_PICKUP. Status tersebut menahan buku sampai diambil, dibatalkan, atau kedaluwarsa.

Status yang berlaku adalah QUEUED, WAITING, READY_FOR_PICKUP, REJECTED, CANCELLED, EXPIRED, dan COMPLETED. Tiga status pertama terbuka. Status akhir harus memiliki `closed_at`. Penolakan memerlukan petugas dan alasan.

Urutan antrean dihitung dari `(requested_at, id)` per `book_id`. Satu mahasiswa tidak boleh memiliki dua pengajuan terbuka untuk buku yang sama. Pinjaman aktif atas buku tersebut juga menghalangi pengajuan baru oleh mahasiswa yang sama.

### Peminjaman

Satu pengajuan menghasilkan nol atau satu pinjaman. Penyerahan hanya boleh dilakukan untuk READY_FOR_PICKUP yang masih valid. Dalam satu transaksi, sistem membuat pinjaman dan mengubah pengajuan menjadi COMPLETED. Identitas mahasiswa dan buku ditelusuri melalui pengajuan, sehingga tidak perlu disalin lagi ke `loans`. Hubungan mahasiswa dan buku pada pengajuan yang sudah menghasilkan pinjaman tidak boleh diubah.

`policy_id` pada pinjaman memakai versi saat penyerahan. `issued_by` wajib diisi. `returned_to`, `returned_at`, dan `return_condition` diisi ketika buku kembali. Pinjaman aktif berarti `returned_at` kosong. `due_date` berlaku sampai akhir hari WIB dan tidak diperpanjang. Fitur perpanjangan tidak termasuk rancangan ini.

Jika kondisi buku tidak layak dipinjam setelah kembali, pustakawan menonaktifkan buku dalam transaksi pengembalian yang sama. Buku nonaktif tidak diberikan kepada antrean berikutnya. Tidak ada pencatatan kerusakan per eksemplar secara terpisah.

### Denda

Satu pinjaman memiliki nol atau satu denda final. Denda dibuat jika hari terlambat dan total denda lebih dari nol. Nilai rupiah memakai bilangan bulat. Total denda adalah `overdue_days × daily_rate`. Tarif disalin dari kebijakan pinjaman saat tagihan dibuat.

`paid_at`, `payment_recorded_by`, dan `payment_reference` diisi bersama saat lunas, atau semuanya kosong saat belum lunas. Aplikasi mencatat pelunasan penuh yang dilakukan di luar sistem. Pembayaran sebagian dan penghapusan denda tidak termasuk versi awal.

### Kebijakan

Setiap baris merupakan versi yang tidak dapat diubah. Versi berjalan memiliki `effective_at` terbesar yang tidak melewati waktu sekarang. Perubahan pustakawan membuat versi baru. Satu versi awal harus tersedia sebelum pengajuan diproses.

`max_books`, `loan_days`, dan `pickup_days` berupa bilangan bulat positif. `daily_fine` berupa bilangan bulat nol atau lebih. Nilai nol menonaktifkan denda. Ketentuan yang sudah dipakai transaksi tidak dihapus.

## Integritas, transaksi, dan indeks

- Gunakan foreign key dengan penghapusan dibatasi untuk data riwayat.
- Terapkan ISBN wajib dan unik pada `books`.
- Pengajuan mahasiswa memakai indeks `(student_id, status)`, sedangkan antrean memakai `(book_id, status, requested_at, id)`.
- Terapkan indeks unik kondisional untuk satu pengajuan terbuka per mahasiswa dan buku, serta satu pengajuan READY_FOR_PICKUP per buku bila didukung basis data.
- Pinjaman aktif memerlukan indeks pada `returned_at` dan `due_date`. Buku ditelusuri melalui `loan_request_id`.
- Persetujuan, penyerahan, pembatalan, kedaluwarsa, dan pengembalian mengunci akun, buku, pengajuan, lalu pinjaman dalam urutan yang konsisten sesuai data yang diperlukan.
- Validasi ketersediaan harus membaca persetujuan pengambilan dan pinjaman aktif dalam transaksi yang sama sambil mengunci baris `books`. Satu indeks pada salah satu tabel tidak cukup untuk mencegah benturan antartabel.
- Penyerahan mengubah pengajuan menjadi COMPLETED dan membuat pinjaman secara atomik, sehingga buku tidak sempat dianggap tersedia di antara kedua operasi.
- Pelunasan mengunci tagihan dan memeriksa statusnya sebelum menulis.
- Pengiriman ulang tindakan tidak membuat pinjaman atau tagihan tambahan. Log teknis tidak menyimpan kata sandi.

## Batas rancangan

Tipe `bigint`, `varchar`, `date`, dan `timestamptz` merupakan tipe logis yang diusulkan. Sintaks enum, indeks kondisional, dan mekanisme transaksi ditentukan saat implementasi. Aplikasi dan skema SQL belum dibuat.

## Bahasa pada diagram

Nama tabel, atribut, relasi, serta enum pada ERD memakai English. Diagram sequence memakai Web UI, Library Service, dan Database untuk komponen teknis. Narasi alur, Mahasiswa, dan Pustakawan tetap memakai bahasa Indonesia.

<!-- GENERATED FIELDS -->

## Daftar atribut lengkap

### Category · `categories`

| Atribut | Kunci | Tipe logis |
| --- | --- | --- |
| id | PK | bigint |
| name | UK | varchar(100) |
| is_active | - | boolean |

### Book · `books`

| Atribut | Kunci | Tipe logis |
| --- | --- | --- |
| id | PK | bigint |
| category_id | FK | bigint |
| title | - | varchar(255) |
| author | - | varchar(255) |
| isbn | UK | varchar(20) |
| publisher | - | varchar(150) |
| publication_year | - | smallint? |
| is_active | - | boolean |

### User · `users`

| Atribut | Kunci | Tipe logis |
| --- | --- | --- |
| id | PK | bigint |
| name | - | varchar(150) |
| email | UK | varchar(255) |
| student_number | UK? | varchar(30)? |
| password_hash | - | text |
| role | - | enum |
| is_active | - | boolean |

### Loan request · `loan_requests`

| Atribut | Kunci | Tipe logis |
| --- | --- | --- |
| id | PK | bigint |
| student_id | FK | bigint |
| book_id | FK | bigint |
| reviewed_by | FK? | bigint? |
| policy_id | FK? | bigint? |
| status | - | enum |
| requested_at | - | timestamptz |
| reviewed_at | - | timestamptz? |
| pickup_deadline | - | timestamptz? |
| closed_at | - | timestamptz? |
| reason | - | text? |

### Loan · `loans`

| Atribut | Kunci | Tipe logis |
| --- | --- | --- |
| id | PK | bigint |
| loan_request_id | FK, UK | bigint |
| policy_id | FK | bigint |
| issued_by | FK | bigint |
| returned_to | FK? | bigint? |
| borrowed_at | - | timestamptz |
| due_date | - | date |
| returned_at | - | timestamptz? |
| return_condition | - | text? |

### Fine · `fines`

| Atribut | Kunci | Tipe logis |
| --- | --- | --- |
| id | PK | bigint |
| loan_id | FK, UK | bigint |
| overdue_days | - | integer |
| daily_rate | - | integer |
| total_amount | - | bigint |
| created_at | - | timestamptz |
| paid_at | - | timestamptz? |
| payment_recorded_by | FK? | bigint? |
| payment_reference | - | varchar(100)? |

### Lending policy · `lending_policies`

| Atribut | Kunci | Tipe logis |
| --- | --- | --- |
| id | PK | bigint |
| effective_at | UK | timestamptz |
| created_by | FK | bigint |
| max_books | - | integer = 2 |
| loan_days | - | integer = 5 |
| daily_fine | - | integer = 1000 |
| pickup_days | - | integer = 2 |
