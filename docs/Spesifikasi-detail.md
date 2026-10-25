# Spesifikasi rinci aplikasi perpustakaan kampus

**Perpus Merah Putih**  
Versi 1.1 | 25 Oktober 2026 | Draf untuk peninjauan

Dokumen ini menjelaskan kebutuhan aplikasi web untuk mengelola buku, pengajuan pinjaman online, antrean reservasi, peminjaman, pengembalian dan denda. Struktur dokumen mengikuti contoh BRD pemesanan kamar hotel yang diberikan pemilik proyek. Isi kebutuhan berasal dari percakapan proyek ini, bukan dari kebijakan resmi kampus.

## Daftar isi

1. Identitas dan riwayat dokumen
2. Pendahuluan
3. Ruang lingkup
4. Perspektif sistem
5. Kebutuhan bisnis
6. Pengakuan dan persetujuan
7. Lampiran desain dan keterlacakan

## 1. Identitas dan riwayat dokumen

| Informasi | Isi |
| --- | --- |
| ID proyek | PMP-01 |
| Nama proyek | Perpus Merah Putih |
| Jenis aplikasi | Aplikasi web perpustakaan kampus |
| Pemohon | Pemilik proyek tugas kuliah |
| Pengguna | Mahasiswa dan pustakawan |
| Status | Draf kebutuhan versi 1.1, belum ditandatangani |
| Penyusun | Asisten penyusun dokumen |
| Peninjau | Pemilik proyek dan perwakilan pustakawan, nama belum ditetapkan |
| Pemberi persetujuan | Pemilik proyek atau dosen pembimbing, nama belum ditetapkan |

| Versi | Tanggal | Ringkasan perubahan |
| --- | --- | --- |
| 1.0 | 24 Oktober 2026 | Kebutuhan awal, aturan yang dikonfirmasi, ERD, dan diagram sequence. |
| 1.1 | 25 Oktober 2026 | Model disederhanakan menjadi satu buku fisik per judul dengan ISBN wajib dan unik. Tabel eksemplar, kode inventaris, dan fitur perpanjangan pinjaman dihapus. |

## 2. Pendahuluan

### 2.1. Latar belakang

Perpustakaan memerlukan satu tempat untuk mencatat koleksi dan peredaran buku. Mahasiswa perlu melihat ketersediaan buku serta mengajukan pinjaman tanpa harus datang terlebih dahulu. Pustakawan perlu memeriksa pengajuan, menyerahkan buku, mencatat pengembalian, dan mengetahui pinjaman yang terlambat.

Satu baris `books` mewakili satu buku fisik per judul dengan ISBN wajib dan unik. Tidak ada pencatatan eksemplar terpisah, kode inventaris, atau jumlah stok. Ketersediaan buku ditentukan dari status aktif, persetujuan pengambilan, dan pinjaman yang belum dikembalikan.

### 2.2. Tujuan dan perbaikan yang diharapkan

| ID | Tujuan | Ukuran penerimaan |
| --- | --- | --- |
| OBJ-01 | Menyediakan katalog dan ketersediaan buku yang dapat ditelusuri. | Setiap buku memiliki ISBN unik dan satu status ketersediaan yang jelas. |
| OBJ-02 | Memudahkan pengajuan online. | Mahasiswa dapat melihat hasil pengajuan dan posisi antrean miliknya. |
| OBJ-03 | Menjaga ketertiban peminjaman. | Sistem menerapkan batas 2 buku dan 5 hari pada pengaturan awal. |
| OBJ-04 | Mencatat pengembalian dan denda secara konsisten. | Setiap pengembalian memiliki waktu pencatatan dan denda yang dapat dihitung ulang. |
| OBJ-05 | Memberi kendali kebijakan kepada pustakawan. | Nilai aturan dapat diubah tanpa mengubah riwayat transaksi lama. |

### 2.3. Gambaran proses bisnis

#### 2.3.1. Proses sebelum aplikasi

Proses saat ini belum dikonfirmasi melalui observasi. Untuk membandingkan proses, dokumen ini memakai gambaran pencatatan manual sebagai konteks saja: mahasiswa menanyakan buku, pustakawan memeriksa rak dan catatan, lalu mencatat pinjaman serta pengembalian. Gambaran ini bukan klaim tentang kondisi perpustakaan tertentu.

#### 2.3.2. Proses yang diusulkan

1. Pustakawan memasukkan judul, kategori, dan ISBN unik untuk satu buku fisik.
2. Mahasiswa masuk, mencari buku, lalu mengajukan satu judul per pengajuan.
3. Sistem memeriksa akun, kuota, pinjaman terlambat, denda belum lunas, dan pengajuan ganda.
4. Jika ada buku bebas, pengajuan berstatus MENUNGGU. Jika tidak ada, pengajuan berstatus ANTRE.
5. Pustakawan memproses pengajuan sesuai urutan masuk dan menyetujui pengajuan yang memenuhi syarat. Persetujuan menahan satu buku selama 2 hari.
6. Mahasiswa datang mengambil buku. Pustakawan mengonfirmasi penyerahan. Pinjaman dan masa 5 hari baru dimulai saat penyerahan ini.
7. Pustakawan menerima buku kembali. Sistem menutup pinjaman dan membuat tagihan denda jika terlambat.
8. Buku kembali tersedia. Pengajuan tertua yang layak masuk daftar pemrosesan berikutnya.
9. Pustakawan mencatat pelunasan denda yang diterima di luar aplikasi.
## 3. Ruang lingkup

### 3.1. Termasuk dalam cakupan

- Masuk dan keluar akun dengan dua peran, mahasiswa dan pustakawan.
- Pengelolaan akun mahasiswa oleh pustakawan, termasuk status aktif.
- Pengelolaan kategori dan buku dengan ISBN unik.
- Pencarian katalog berdasarkan judul, penulis, ISBN, dan kategori.
- Pengajuan pinjaman online serta antrean reservasi per judul.
- Persetujuan atau penolakan pengajuan oleh pustakawan.
- Pembatalan pengajuan oleh mahasiswa sebelum buku diserahkan.
- Batas waktu pengambilan dan pelepasan buku jika pengajuan kedaluwarsa.
- Pencatatan penyerahan, pengembalian, dan riwayat pinjaman.
- Perhitungan denda keterlambatan dan pencatatan pelunasan penuh.
- Pengaturan aturan pinjam oleh pustakawan dan penyimpanan versi aturan.
- Ringkasan koleksi, pinjaman aktif, keterlambatan, antrean, dan denda belum lunas.

### 3.2. Di luar cakupan

- Aplikasi seluler native, buku elektronik, pembelian buku, dan katalog lintas kampus.
- Integrasi SSO kampus, sistem akademik, RFID, pemindai khusus, dan payment gateway.
- Pembayaran online, cicilan denda, pengembalian uang, atau penghapusan denda.
- Denda kerusakan atau kehilangan serta proses penggantian buku. Buku dapat ditandai tidak layak untuk menghentikan peminjaman baru.
- Email, SMS, dan WhatsApp otomatis. Status dan batas waktu ditampilkan dalam aplikasi.
- Rekomendasi buku, ulasan, dan laporan analitik lanjutan.
- Pengajuan banyak buku dalam satu transaksi. Dua buku diproses sebagai dua pengajuan dan dua pinjaman.

- Fitur perpanjangan pinjaman.

## 4. Perspektif sistem

### 4.1. Asumsi dan ketergantungan

- Aplikasi melayani satu perpustakaan kampus dan koleksi fisik.
- Pustakawan memverifikasi identitas mahasiswa saat membuat akun dan saat menyerahkan buku.
- Akun pustakawan pertama disiapkan pengelola teknis. Mahasiswa tidak dapat memilih peran pustakawan.
- Pengguna memiliki perangkat dengan browser dan koneksi ke server aplikasi.
- Hari pinjam, pengambilan, dan keterlambatan memakai hari kalender dalam zona waktu Asia/Jakarta.
- Target kinerja pada bagian 5.4 merupakan target rancangan untuk proyek kuliah, belum hasil pengukuran.

### 4.2. Pengecualian dan batas tanggung jawab

Sistem mencatat aktivitas perpustakaan. Pustakawan tetap bertanggung jawab atas pemeriksaan fisik, kecocokan ISBN, dan penerimaan pembayaran. Status SIAP_DIAMBIL bukan bukti penyerahan buku. Bukti pinjaman baru ada setelah pustakawan mengonfirmasi pengambilan.

### 4.3. Batasan

| Aspek | Batasan |
| --- | --- |
| Skala awal | Satu perpustakaan, dua peran pengguna. |
| Anggaran dan jadwal | Belum ditetapkan. Dokumen ini tidak menjanjikan biaya atau tanggal peluncuran. |
| Teknologi | Framework dan basis data belum dipilih. Model data dapat diterapkan pada basis data relasional. |
| Migrasi | Tidak ada migrasi data lama yang termasuk dalam versi awal. |
| Keandalan | Ketersediaan bergantung pada server dan jaringan kampus. Tidak ada janji layanan 24/7. |

## 5. Kebutuhan bisnis

### 5.1. Peran dan hak akses

| Aktivitas | Mahasiswa | Pustakawan |
| --- | --- | --- |
| Melihat dan mencari katalog | Ya | Ya |
| Melihat data pribadi dan transaksi sendiri | Ya | Ya |
| Mengajukan, membatalkan, dan melihat antrean sendiri | Ya | Tidak mengajukan atas nama mahasiswa pada versi awal |
| Mengelola mahasiswa dan koleksi | Tidak | Ya |
| Memproses pengajuan dan penyerahan | Tidak | Ya |
| Mencatat pengembalian dan pelunasan denda | Tidak | Ya |
| Mengubah aturan dan melihat seluruh transaksi | Tidak | Ya |

Mahasiswa hanya dapat mengakses transaksi miliknya. Pustakawan tidak dapat mengubah identitas peminjam pada transaksi yang sudah dibuat.

### 5.2. Aturan bisnis

Angka awal berikut telah dikonfirmasi pemilik proyek. Seluruh angka dalam tabel disimpan pada versi kebijakan dan dapat diubah pustakawan.

| ID | Aturan | Nilai awal dan ketentuan |
| --- | --- | --- |
| BR-01 | Batas buku | Maksimal 2 buku per mahasiswa. Kuota terpakai adalah pinjaman aktif ditambah pengajuan SIAP_DIAMBIL. |
| BR-02 | Masa pinjam | 5 hari kalender sejak tanggal penyerahan, jatuh tempo pukul 23.59.59 WIB. |
| BR-03 | Denda | Rp1.000 per buku per hari kalender terlambat. Hari terlambat dihitung dari selisih tanggal lokal, minimal 0. |
| BR-04 | Waktu pengambilan | 2 hari kalender sejak persetujuan, hingga pukul 23.59.59 WIB pada tanggal batas. |
| BR-05 | Urutan reservasi | Berdasarkan waktu pengajuan paling awal, lalu ID pengajuan jika waktunya sama. Berlaku per judul. |

Ketentuan pelaksanaan berikut menghindari perbedaan arti antarfitur.

| ID | Ketentuan |
| --- | --- |
| BR-06 | Pengajuan baru ditolak jika akun tidak aktif, kuota penuh, ada pinjaman terlambat, atau ada denda belum lunas. Maksimal pengajuan MENUNGGU dan ANTRE yang terbuka per mahasiswa mengikuti nilai batas buku. Satu mahasiswa hanya boleh memiliki satu pengajuan terbuka atau pinjaman aktif untuk judul yang sama. |
| BR-07 | Pengajuan ANTRE dan MENUNGGU belum mengalokasikan buku atau kuota. Pustakawan wajib memeriksa ulang syarat saat persetujuan dan penyerahan. Jika pengajuan tertua tidak lagi layak, pustakawan menolaknya dengan alasan sebelum memproses yang berikutnya. |
| BR-08 | Persetujuan mengikat satu buku bebas dan menaikkan kuota terpakai. Sistem menolak persetujuan ganda, buku disiapkan ganda, dan tindakan yang melampaui kuota, termasuk saat dua petugas bekerja bersamaan. |
| BR-09 | Mahasiswa dapat membatalkan ANTRE, MENUNGGU, atau SIAP_DIAMBIL. Pengajuan SIAP_DIAMBIL yang melewati batas menjadi KEDALUWARSA. Keduanya melepaskan alokasi buku dan kuota secara atomik. |
| BR-10 | Reservasi ditujukan pada judul. Buku ditetapkan saat persetujuan. Sistem tidak menjanjikan tanggal tersedia bagi pengajuan ANTRE. Status dan posisi antrean dapat dilihat mahasiswa. |
| BR-11 | Pengembalian menutup satu pinjaman dan mencatat kondisi buku. Buku yang baik kembali tersedia. Jika tidak layak dipinjam, pustakawan menonaktifkan buku sebelum pengembalian diselesaikan. Pengembalian tetap dapat dicatat saat mahasiswa memiliki denda. |
| BR-12 | Denda berjalan ditampilkan sebagai perkiraan. Tagihan final dibuat satu kali saat pengembalian jika ada keterlambatan. Pelunasan penuh dicatat pustakawan dengan waktu, petugas, dan referensi bukti pembayaran. |
| BR-13 | Setiap perubahan pengaturan menghasilkan versi kebijakan baru yang tidak dapat diubah. Persetujuan menyimpan versi untuk waktu pengambilan. Penyerahan menyimpan versi yang berlaku saat itu untuk masa pinjam dan tarif denda. Riwayat lama tidak dihitung ulang akibat perubahan aturan. Batas kuota terkini berlaku untuk persetujuan dan penyerahan baru. |
| BR-14 | Penurunan batas kuota tidak membatalkan pinjaman atau persetujuan lama. Jika penyerahan akan melampaui batas terkini, sistem menolak penyerahan dan pustakawan membatalkan persetujuan agar buku kembali tersedia. |
| BR-15 | Akun, buku, dan kategori yang sudah direferensikan transaksi tidak dihapus permanen. Gunakan status nonaktif. Penonaktifan buku membatalkan persetujuan terkait dengan alasan; pinjaman aktif tetap dapat dikembalikan. |
| BR-16 | Perubahan status, penyiapan buku, penyerahan, pengembalian dan pelunasan harus atomik. Pengulangan tindakan yang sama tidak membuat pinjaman atau tagihan baru. |

Contoh tanggal: buku diserahkan pada 24 Oktober 2026, jatuh tempo 29 Oktober 2026 pukul 23.59.59 WIB. Jika dikembalikan 31 Oktober, keterlambatan adalah 2 hari dan dendanya Rp2.000. Jatuh tempo tidak diperpanjang. Pengajuan yang disetujui 24 Oktober memiliki batas pengambilan 26 Oktober pukul 23.59.59 WIB.

### 5.3. Kebutuhan fungsional

Seluruh kebutuhan berikut termasuk versi awal.

| ID | Kebutuhan | Kriteria penerimaan |
| --- | --- | --- |
| FR-01 | Autentikasi dan pembatasan peran. | Akun nonaktif ditolak. Mahasiswa tidak dapat membuka fungsi pustakawan atau transaksi mahasiswa lain. |
| FR-02 | Kelola mahasiswa. | Pustakawan dapat menambah, memperbarui profil, mereset akses, dan menonaktifkan akun. NIM dan email tidak boleh ganda. |
| FR-03 | Kelola kategori dan judul. | Buku memuat judul, penulis, ISBN wajib dan unik, penerbit, tahun opsional, kategori, dan status aktif. |
| FR-04 | Kelola ketersediaan buku. | Satu buku fisik per judul/ISBN. Buku tersedia jika aktif, tanpa persetujuan pengambilan dan tanpa pinjaman aktif. Tidak ada jumlah stok. |
| FR-05 | Cari katalog dan lihat ketersediaan. | Katalog menampilkan status tersedia, siap diambil, dipinjam, atau nonaktif untuk setiap buku. |
| FR-06 | Ajukan pinjaman online. | Pengajuan valid menjadi MENUNGGU atau ANTRE, mendapat ID, waktu masuk, dan alasan jika gagal. |
| FR-07 | Kelola antrean. | Pengajuan diurutkan per judul. Pengajuan setelah pengembalian atau pembatalan persetujuan diproses sesuai BR-05 dan BR-07. |
| FR-08 | Setujui atau tolak pengajuan. | Persetujuan mengikat tepat satu buku dan batas pengambilan. Penolakan menyimpan alasan dan petugas. |
| FR-09 | Batalkan dan kedaluwarsakan pengajuan. | Stok dan kuota dilepas. Pengajuan yang kedaluwarsa tidak dapat diserahkan. |
| FR-10 | Catat penyerahan buku. | Hanya SIAP_DIAMBIL yang valid dapat menghasilkan satu pinjaman. Tanggal jatuh tempo muncul setelah penyerahan. |
| FR-11 | Catat pengembalian. | Pinjaman hanya ditutup satu kali. Sistem mencatat petugas, waktu kembali, kondisi, dan denda final jika ada. |
| FR-12 | Kelola denda. | Perkiraan dihitung dari tanggal lokal. Tagihan final hanya satu per pinjaman. Pelunasan penuh tidak dapat dicatat dua kali. |
| FR-13 | Atur kebijakan. | Pustakawan dapat mengubah batas buku, hari pinjam, tarif denda dan hari pengambilan. |
| FR-14 | Lihat ringkasan dan riwayat. | Pustakawan melihat seluruh transaksi dengan filter tanggal dan status. Mahasiswa hanya melihat data miliknya. |

### 5.4. Kebutuhan nonfungsional

| ID | Aspek | Target penerimaan |
| --- | --- | --- |
| NFR-01 | Keamanan akses | Semua operasi memeriksa sesi, peran, dan kepemilikan pada server. Kata sandi disimpan dengan hash adaptif dan koneksi produksi memakai HTTPS. |
| NFR-02 | Integritas data | Foreign key dan batasan unik diterapkan. Simulasi persetujuan bersamaan tidak mengalokasikan satu buku ke dua pengajuan atau melampaui kuota. |
| NFR-03 | Kinerja | Dengan 5.000 buku ber-ISBN berbeda dan 20 pengguna bersamaan pada lingkungan uji yang dicatat, 95% pencarian dan pembukaan riwayat selesai dalam 2 detik. |
| NFR-04 | Kemudahan penggunaan | Tampilan bekerja pada lebar 360 hingga 1440 piksel. Formulir memiliki label, pesan kesalahan, dan navigasi keyboard. |
| NFR-05 | Pencadangan | Basis data dicadangkan setiap hari. Uji pemulihan dapat mengembalikan data dari cadangan terakhir, dengan potensi kehilangan data maksimal 24 jam. |
| NFR-06 | Ketepatan waktu | Simpan waktu kejadian secara konsisten dan hitung tanggal bisnis dalam Asia/Jakarta. Pengajuan kedaluwarsa diperiksa sebelum setiap alokasi atau penyerahan, meskipun proses terjadwal terlambat. |
| NFR-07 | Penelusuran | Pengajuan, persetujuan, penyerahan, pengembalian, pelunasan, dan versi kebijakan menyimpan pelaku serta waktunya. Pesan kesalahan tidak menampilkan kata sandi atau data sesi. |

### 5.5. Status dan perpindahan

| Objek | Status atau perpindahan yang diperbolehkan |
| --- | --- |
| Pengajuan awal | MENUNGGU jika buku tersedia, ANTRE jika buku tidak tersedia. Keduanya belum menjamin alokasi. |
| Penilaian ketersediaan | ANTRE dapat menjadi MENUNGGU ketika buku tersedia kembali. MENUNGGU dapat kembali ANTRE bila buku sudah disiapkan untuk mahasiswa lain sebelum disetujui. Urutan tetap memakai waktu awal. |
| Keputusan pustakawan | ANTRE atau MENUNGGU menjadi SIAP_DIAMBIL saat disetujui, atau DITOLAK dengan alasan. Persetujuan mensyaratkan buku tersedia. |
| Akhir pengajuan | SIAP_DIAMBIL menjadi SELESAI setelah penyerahan atau KEDALUWARSA setelah batas waktu. ANTRE, MENUNGGU, dan SIAP_DIAMBIL dapat menjadi DIBATALKAN. Status akhir tidak dapat dibuka ulang. |
| Pinjaman | Aktif jika dikembalikan_pada kosong. Selesai jika terisi. Terlambat merupakan kondisi turunan dari tanggal jatuh tempo, bukan status terpisah yang dapat tertinggal. |
| Buku | Layak atau tidak layak sebagai kondisi fisik. Status bebas, disiapkan, atau dipinjam dihitung dari pengajuan aktif dan pinjaman aktif. |
| Denda | Belum lunas jika dibayar_pada kosong. Lunas setelah pustakawan mencatat pembayaran penuh. |

## 6. Pengakuan dan persetujuan

### 6.1. Pengakuan peninjauan

| Nama | Peran | Tanggal | Tanda tangan |
| --- | --- | --- | --- |
| Belum diisi | Perwakilan pustakawan | Belum diisi | Belum diisi |
| Belum diisi | Perwakilan mahasiswa | Belum diisi | Belum diisi |

### 6.2. Persetujuan dokumen

| Nama | Peran | Keputusan | Tanggal dan tanda tangan |
| --- | --- | --- | --- |
| Belum diisi | Pemilik proyek | Belum ditetapkan | Belum diisi |
| Belum diisi | Dosen pembimbing | Belum ditetapkan | Belum diisi |

Pemilik proyek telah mengonfirmasi fitur dan angka kebijakan melalui percakapan. Tabel ini tetap kosong karena persetujuan formal dokumen belum diberikan. Jadwal, anggaran, identitas penandatangan, dan teknologi implementasi tetap belum ditetapkan.

## 7. Lampiran desain dan keterlacakan

### 7.1. Daftar artefak

| Artefak | Isi |
| --- | --- |
| 01a-erd-koleksi-pengajuan.svg | ERD koleksi dan pengajuan dengan notasi crow's foot. |
| 01b-erd-sirkulasi.svg | ERD pinjaman, dan denda. |
| 01c-erd-kebijakan-petugas.svg | ERD kebijakan dan pelaku transaksi. |
| 01-erd-lengkap.mmd | Sumber Mermaid lengkap, tujuh entitas dan seluruh 12 relasi. |
| 02-pengajuan.svg dan 02-pengajuan.mmd | Pengajuan online serta penentuan status antrean. |
| 03-persetujuan.svg dan 03-persetujuan.mmd | Persetujuan, penyiapan buku, dan batas pengambilan. |
| 04-pengambilan.svg dan 04-pengambilan.mmd | Validasi ulang, penyerahan, dan pembuatan pinjaman. |
| 05-pengembalian.svg dan 05-pengembalian.mmd | Pengembalian, denda final, dan pelepasan alokasi buku. |
| 06-pelunasan.svg dan 06-pelunasan.mmd | Pencatatan pelunasan penuh oleh pustakawan. |
| Kamus-data.md | Atribut, relasi, batasan, dan arti data. |

### 7.2. Keterlacakan kebutuhan

| Kebutuhan | Entitas utama | Diagram atau cara pembuktian |
| --- | --- | --- |
| FR-01, FR-02 | akun | Pemeriksaan peran dan kepemilikan pada seluruh alur; uji akses saat implementasi. |
| FR-03, FR-04, FR-05 | kategori, buku | ERD dan uji katalog saat implementasi. |
| FR-06, FR-07 | pengajuan, buku, akun | Sequence 02 dan 05. |
| FR-08, FR-09 | pengajuan, buku, kebijakan | Sequence 03, 04, dan aturan kedaluwarsa BR-09. |
| FR-10 | peminjaman, pengajuan, kebijakan | Sequence 04. |
| FR-11 | peminjaman, buku, denda | Sequence 05. |
| FR-12 | denda, peminjaman, akun | Sequence 05 dan 07. |
| FR-13 | kebijakan | ERD, versi kebijakan, dan uji perubahan aturan saat implementasi. |
| FR-14 | Seluruh data transaksi | Filter daftar dan pemisahan data per mahasiswa saat implementasi. |

### 7.3. Skenario penerimaan prioritas

1. Mahasiswa dengan dua pinjaman aktif tidak dapat memperoleh persetujuan ketiga.
2. Dua pustakawan menyetujui buku terakhir secara bersamaan. Tepat satu persetujuan berhasil.
3. Mahasiswa terlambat atau memiliki denda belum lunas tidak dapat mengajukan atau mengambil buku baru.
4. Dua pengajuan untuk satu judul diproses menurut waktu masuk. Pengajuan yang ditolak menyimpan alasannya.
5. Buku yang tidak diambil setelah batas 2 hari dilepas dan pengajuan menjadi KEDALUWARSA.
6. Buku yang diserahkan 24 Oktober dan kembali 31 Oktober menghasilkan denda Rp2.000 dengan aturan awal.
7. Perubahan tarif tidak mengubah tarif yang berlaku pada pinjaman lama.
8. Pengembalian dan pelunasan yang dikirim ulang tidak menggandakan alokasi buku atau tagihan.

Skenario ini adalah kriteria pengujian untuk aplikasi yang akan dibangun. Dokumen ini belum menyatakan aplikasi atau skenario tersebut sudah dijalankan.

### 7.4. Sumber

- Struktur BRD: EXAMPLE_BRD-PROYEK_WEB_PEMESANAN_KAMAR_HOTEL.pdf, 9 halaman, disediakan pemilik proyek.
- Cakupan dan angka aturan: konfirmasi pemilik proyek pada percakapan 24 Oktober 2026.
- Acuan warna: https://www.metaguna.ac.id/, CSS terhitung diperiksa 24 Oktober 2026. Situs hanya menjadi acuan visual, bukan sumber kebijakan perpustakaan.
