# Kelola buku untuk pustakawan

Model koleksi memakai satu buku fisik per judul dengan ISBN wajib dan unik. Tidak ada tabel eksemplar, kode inventaris, jumlah stok, atau form tambah/edit eksemplar. Ketersediaan dihitung dari status aktif, pengajuan READY_FOR_PICKUP, dan pinjaman yang belum kembali. Acuannya adalah `docs/Kamus-data.md` dan BRD versi 1.3.

Delapan layar pada page **Librarian / Book management** di `Perpus Merah Putih.figcraft` mencakup:

| Layar | Isi |
| --- | --- |
| Daftar buku | Judul, kategori, status ketersediaan, dan tindakan. |
| Tambah buku | Judul, penulis, kategori, ISBN wajib dan unik, penerbit, serta tahun terbit opsional. |
| Detail buku | Informasi buku dan satu status ketersediaan. |
| Edit buku | Perubahan informasi tanpa mengubah riwayat peminjaman. |
| ISBN sudah digunakan | Validasi ISBN yang sudah tercatat pada buku lain. |
| Nonaktifkan buku | Konfirmasi beralasan, pembatalan persetujuan terkait, dan pelestarian riwayat. |
| Pencarian kosong | Pesan tidak ada hasil dan tindakan untuk mencari kembali. |
| Daftar collapsed | Contoh daftar dengan sidebar diciutkan. |

ISBN menjadi identitas buku yang digunakan pustakawan. Buku berstatus Tersedia hanya jika aktif, tidak sedang disiapkan untuk pengambilan, dan tidak sedang dipinjam. Tidak ada pengisian jumlah buku. Pengembalian tetap dapat dicatat setelah buku dinonaktifkan.

Desain memakai token Shark Theme persis dari sumber, font Inter Tight, serta komponen shadcn/ui. UI copy memakai bahasa Indonesia. Semua data dan status merupakan contoh rancangan, bukan transaksi sebenarnya.

Sidebar tetap memakai component set Expanded 232 px dan Collapsed 72 px. Ikon memakai property instance swap. Navbar tetap memakai property Breadcrumb dan Date. Shell, SidebarInset, PageContent, form, tabel, dan dialog mempertahankan auto layout yang sudah dibuat, sehingga konten mengikuti perubahan lebar sidebar.

Form dan tombol merupakan rancangan visual. Form tidak menerima input atau menyimpan data aplikasi. Prototype menyediakan navigasi antara layar yang masih relevan; perubahan state Sidebar tetap dapat dicoba.

## Ekspor dan preview

Setiap layar memiliki PNG, SVG yang dapat diedit, dan PDF dalam Light serta Dark. PDF gabungan `Librarian-books-light.pdf` dan `Librarian-books-dark.pdf` masing-masing berisi delapan halaman. `preview.html` dan `responsive-preview.html` menyediakan pilihan layar, mode, dan state Sidebar. Gambar dengan awalan `responsive-` menunjukkan kedua state sidebar.

## Ekspor ulang

Desain utama berada di `docs/Perpus Merah Putih.figcraft`. Edit file tersebut langsung untuk mengubah layout atau isi layar. Alat ekspor membaca file native saat ini.

```sh
uv run --with pypdf python -B tools/export_book_ui.py
uv run --with pypdf python -B tools/export_design_system.py
uv run --with pillow --with pypdf python -B tools/verify_librarian_books.py
python3 -B tools/verify_all_sidebar_screens.py
python3 -B tools/verify_responsive_pages.py
```

Snapshot lama, log, serta generator migrasi tidak disimpan di repository. Sumber komponen shadcn/ui yang dipakai tersedia di `docs/design-system/shadcn-source/` beserta lisensinya.

Perpanjangan pinjaman tidak termasuk fitur aplikasi. Pengaturan hanya memuat batas buku, masa pinjam, tarif denda, dan waktu pengambilan.
