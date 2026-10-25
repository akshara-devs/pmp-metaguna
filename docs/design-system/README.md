# Perpus Merah Putih dengan shadcn/ui

Library di `Perpus Merah Putih.figcraft` kini memakai komponen visual shadcn/ui **New York v4 / Radix**, mengikuti komponen yang digunakan pada [halaman Shark Theme](https://tweakcn.com/themes/cmqfccy22000504l8fld0fkop). Semua 44 token tema Light dan Dark dipertahankan persis dari sumber.

File FigCraft berisi komponen native yang dapat diedit, variants, instances, text styles, variables, slot Card, dan tautan komponen React untuk handoff. File ini bukan aplikasi React yang berjalan. Snapshot kode komponen React resmi tersedia di `shadcn-source/*.json`; asal dan hash sumber tercatat di `shadcn-components.json`.

## Komponen dan aturan

| Komponen sebelumnya | Komponen saat ini |
| --- | --- |
| Primary, secondary, danger, text button | Button dengan Variant default, secondary, destructive, outline, ghost, link; Size xs, sm, default, lg, icon; states hover, focus, disabled, loading. |
| Navigation item | SidebarMenuButton dengan selected state memakai sidebar-accent. |
| Text field | Field, FieldLabel, Input, FieldDescription, FieldError. |
| Checkbox dan switch besar | Checkbox 16 px dan Switch 32 × 18,4 px, di dalam baris Field dengan label. |
| Solid callout | Alert, AlertTitle, AlertDescription; varian default dan destructive standar. |
| Custom toast | Sonner dengan title, description, dan ikon. |
| Dialog pembatalan | AlertDialog dengan Title, Description, cancel Button outline, dan action Button destructive. |
| Badge warna khusus | Badge standar default, secondary, destructive, outline, ghost, link. |
| Loan table row | TableRow dan TableCell dengan padding 8 px; metadata dua baris memakai tinggi row 72 px. |
| Empty state | Empty dengan ikon, judul, deskripsi, dan Button. |
| Book card | Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter, dan Button. |
| Ikon gambar manual | Vektor Lucide dari sumber resmi, dengan stroke 2 px. |
| Search dan policy controls | Input dan SelectTrigger. |

Button dan Input memiliki tinggi visual default 36 px. Button xs 24 px, sm 32 px, lg 40 px. Badge memiliki tinggi 22 px dan lebar mengikuti isi. Ukuran visual ini mengikuti komponen sumber; area sentuh dapat diperluas pada implementasi mobile.

Button memakai tinggi tetap dan alignment center. Auto layout dihitung ulang sesudah resolusi variable dan font agar label tidak menyimpan koordinat dari kontrol lama 44 px. Posisi label diperiksa pada semua ukuran dan instance, serta pada piksel ekspor.

Focus menggunakan border ring dan ring 3 px dengan opacity 50%. Disabled memakai opacity 50%. Loading merupakan komposisi Spinner dan disabled. Radius, warna, spacing, dan shadow tetap mengambil Shark Theme.

`shadcn/*` variables menyimpan ukuran komponen serta modifier opacity yang berasal dari kelas komponen resmi, termasuk dark input/30 dan destructive/60. Modifier tersebut tidak mengganti nilai token tema asli.

## Pemetaan status

| Label | Variant Badge |
| --- | --- |
| Tersedia, Siap diambil | default |
| Menunggu, Mengantre, Dipinjam | secondary |
| Terlambat, Ditolak, Belum lunas | destructive |
| Selesai, Dibatalkan, Kedaluwarsa, Lunas | outline |

Varian warna solid khusus sebelumnya sudah diganti sesuai pilihan pengguna. Pesan warning menggunakan Alert default dengan judul dan deskripsi yang menjelaskan kondisi. Status tetap memiliki label Indonesia, sehingga maknanya tidak hanya bergantung pada warna.

Warna sumber tidak disesuaikan untuk kontras. Beberapa pasangan sumber berada di bawah 4.5:1; laporan pengukuran tersedia di `verification.json`. Tidak ada klaim bahwa seluruh pasangan memenuhi WCAG AA.

## Memakai file

1. Tarik komponen dari Assets dan pilih Variant, Size, atau State yang tersedia.
2. Ubah Label pada Button. Book card menyediakan Title, Cover title, Category, dan Availability.
3. Pilih page atau frame, lalu ganti variable mode pada collection **Shark Theme** menjadi Light atau Dark. File disimpan dalam Light.
4. Pertahankan instance agar pembaruan main component tetap diteruskan.

UI copy memakai bahasa Indonesia. Nama komponen, token, dan technical terms memakai English. Kebijakan peminjaman tetap 2 buku, 5 hari, denda Rp1.000 per buku per hari kalender, pengambilan reservasi 2 hari. Angkanya dapat diubah pustakawan.

## Ekspor dan reproduksi

Lima page memuat Foundations, Components, Forms and feedback, Library patterns, dan Reference screens. Tujuh board/layar masing-masing memiliki ekspor PNG, PDF, serta SVG dalam Light dan Dark. Sufiks `-dark` menandai mode Dark. PDF gabungan tersedia sebagai `Design-system.pdf` dan `Design-system-dark.pdf`.

`shark-theme.css` memuat seluruh token sumber dalam `:root` dan `.dark`. `variables.json` dan `variables.css` merupakan ekspor native FigCraft. `Perpus-Merah-Putih-design-system.fig` adalah ekspor Figma eksperimental; `.figcraft` tetap sumber utama yang dapat diedit.

Untuk mengekspor ulang isi file native saat ini:

```sh
uv run --with pypdf python -B tools/export_design_system.py
uv run --with pypdf --with pillow python -B tools/verify_design_system.py
```

Edit komponen langsung di `docs/Perpus Merah Putih.figcraft`. Snapshot registry resmi dan lisensi shadcn/ui serta Lucide berada di `shadcn-source/`. Generator migrasi dan snapshot lama tidak disimpan di repository.

Model koleksi saat ini memakai satu buku fisik per judul dengan ISBN wajib dan unik. Fitur perpanjangan pinjaman sudah dikeluarkan dari ruang lingkup; formulir kebijakan menampilkan empat aturan.
