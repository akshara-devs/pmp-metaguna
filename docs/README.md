# Perpus Merah Putih

Rancangan aplikasi perpustakaan kampus. Aplikasi web belum diimplementasikan; folder `code/` disiapkan untuk pengembangan berikutnya.

Model terbaru memakai satu buku fisik per judul dengan ISBN wajib dan unik. Tidak ada pencatatan eksemplar, kode inventaris, jumlah stok, atau fitur perpanjangan pinjaman. Buku tersedia jika aktif, tidak sedang disiapkan untuk pengambilan, dan tidak sedang dipinjam.

Aturan awal adalah maksimal 2 buku per mahasiswa, masa pinjam 5 hari kalender, denda Rp1.000 per buku per hari kalender, dan batas pengambilan 2 hari. Pustakawan dapat mengubah keempat aturan tersebut melalui versi kebijakan baru.

## Dokumen dan desain

| Berkas | Kegunaan |
| --- | --- |
| [BRD PDF](BRD-perpus-merah-putih.pdf) | BRD ringkas versi 1.3, enam bab sesuai referensi. |
| [BRD Word](BRD-perpus-merah-putih.docx) | Dokumen editable dengan daftar isi otomatis dan border pada seluruh sel tabel. |
| [BRD Markdown](BRD-perpus-merah-putih.md) | Sumber isi BRD. |
| [Spesifikasi detail](Spesifikasi-detail.md) | Aturan, hak akses, kebutuhan, dan skenario penerimaan. |
| [Kamus data](Kamus-data.md) | Atribut, relasi, dan batasan tujuh entitas. |
| [Diagram PDF](Diagram-Perpus-Merah-Putih.pdf) | Tiga ERD Crow's Foot dan lima sequence diagram. |
| [Diagram HTML](diagram-perpustakaan.html) | Galeri diagram yang dapat diperbesar. |
| [FigCraft diagram](<Perpus Merah Putih — BRD dan diagram.figcraft>) | Sumber diagram dengan teks dan bentuk yang dapat diedit. |
| [FigCraft aplikasi](<Perpus Merah Putih.figcraft>) | Design system serta layar aplikasi. |
| [Design system](design-system/README.md) | shadcn/ui New York/Radix dan Shark Theme Light/Dark. |
| [Kelola buku](librarian-books/README.md) | Delapan layar pustakawan dengan ISBN unik serta preview responsive. |

Sumber model berada di `source/model.json`. Model memiliki **7 entitas dan 12 relasi**. Nama tabel, atribut, dan technical terms memakai English; narasi bisnis serta sequence memakai bahasa Indonesia. Gambar dan sumber Mermaid berada di `diagrams/`.

SVG dapat diimpor ke Figma Design untuk mengedit teks dan bentuk. PNG dapat digunakan di FigJam untuk diskusi. File `.fig` merupakan ekspor eksperimental; pembukaannya di Figma belum diuji. File `.figcraft` tetap menjadi sumber utama editable.

Referensi BRD awal dan acuan warna diagram berada di `reference/`. Warna antarmuka aplikasi memakai Shark Theme persis dari sumber; warna pada dokumen dan diagram mempertahankan acuan sebelumnya.

## Membuat ulang ekspor

Prasyarat: Python, uv, pandoc, FigCraft CLI, serta Microsoft Word di macOS untuk memperbarui nomor halaman daftar isi dan PDF BRD.

```sh
uv run --with markdown --with beautifulsoup4 --with reportlab --with lxml python -B tools/build_documents.py
osascript tools/refresh_word_toc.applescript "$PWD/docs/BRD-perpus-merah-putih.docx" "$PWD/docs/BRD-perpus-merah-putih.pdf"
python3 -B tools/export_model_documents.py
uv run --with pypdf python -B tools/export_book_ui.py
uv run --with pypdf python -B tools/export_design_system.py
uv run --with pypdf python -B tools/package_deliverables.py
```

Jika model atau pesan sequence berubah, impor SVG yang diperbarui ke dokumen FigCraft diagram sebelum mengekspor PNG/PDF. Desain antarmuka diedit langsung pada file FigCraft aplikasi; ekspor mengambil isi file tersebut. Generator migrasi serta snapshot lama tidak termasuk repository ini.

Paket ZIP dibuat lokal di `docs/Perpus-Merah-Putih-dokumen.zip` dan tidak disimpan di Git karena isinya menduplikasi dokumen yang sudah tersedia.

## Verifikasi

```sh
uv run --with pypdf --with pillow python -B tools/verify_documents.py
uv run --with pypdf --with pillow python -B tools/verify_design_system.py
uv run --with pypdf --with pillow python -B tools/verify_librarian_books.py
uv run --with pillow python -B tools/verify_sidebar_component.py
python3 -B tools/verify_sidebar_icons.py
python3 -B tools/verify_navbar_component.py
python3 -B tools/verify_all_sidebar_screens.py
python3 -B tools/verify_responsive_pages.py
python3 -B tools/verify_sidebar_initial_states.py
```

Pemeriksaan memvalidasi artefak rancangan, termasuk relasi data, daftar isi Word, border tabel, isi PDF, komponen native, posisi teks tombol, dan respons layout saat Sidebar berubah. Pemeriksaan ini bukan pengujian aplikasi web yang sudah berjalan.
