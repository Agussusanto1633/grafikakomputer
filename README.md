# Modul Pemrograman Grafika Komputer

Implementasi grafika komputer berbasis OpenGL yang komprehensif dengan fitur manipulasi objek 2D dan visualisasi 3D dengan pencahayaan dan transformasi canggih.

## Gambaran Umum

Proyek ini terdiri dari dua modul utama:
- **Modul A**: Penggambaran dan Manipulasi Objek 2D dengan Clipping
- **Modul B**: Visualisasi Objek 3D dengan Pencahayaan Canggih

## Persyaratan Sistem

### Paket Python yang Diperlukan
```bash
pip install pygame PyOpenGL PyOpenGL_accelerate numpy
```

### Kebutuhan Sistem
- Python 3.7+
- Kartu grafis yang kompatibel dengan OpenGL 2.1+
- Resolusi layar minimum 1200x800 (disarankan)

## Modul A: Penggambaran dan Manipulasi Objek 2D

### Fitur-Fitur

#### 🎯 A. Fungsi Penggambaran Objek
- **A.1.a)** Menggambar titik dengan ukuran yang dapat disesuaikan
- **A.1.b)** Menggambar garis dengan kontrol ketebalan
- **A.1.c)** Menggambar persegi panjang
- **A.1.d)** Menggambar ellipse dengan presisi matematis
- **A.2)** Sistem input koordinat berbasis mouse

#### 🎨 B. Kontrol Warna dan Gaya
- **B.3.a)** Pemilihan warna melalui shortcut keyboard
- **B.3.b)** Penyesuaian ketebalan garis
- Feedback visual secara real-time

#### 🔄 C. Transformasi Geometri
- **C.4.a)** Translasi (perubahan posisi)
- **C.4.b)** Rotasi mengelilingi pusat objek
- **C.4.c)** Scaling dari pusat objek
- **C.5)** Kontrol transformasi berbasis keyboard
- Transformasi berkelanjutan yang halus dengan menahan tombol

#### 🪟 D. Windowing dan Clipping Canggih
- **D.6)** Definisi window clipping secara interaktif
- **D.7.a)** Objek di dalam window berubah warna hijau
- **D.7.b)** Algoritma Cohen-Sutherland untuk clipping garis
- **D.8)** Window clipping yang dapat diseret dengan feedback visual

### Kontrol

#### Pemilihan Tool
- `1` - Tool titik (klik sekali)
- `2` - Tool garis (klik dua kali)
- `3` - Tool persegi (klik dua kali)
- `4` - Tool ellipse (klik dua kali)

#### Pemilihan Warna
- `R` - Merah
- `G` - Hijau
- `B` - Biru
- `W` - Putih
- `Y` - Kuning
- `M` - Magenta
- `Shift+C` - Cyan

#### Properti Objek
- `+` / `-` - Tambah/kurangi ketebalan garis
- `.` / `,` - Tambah/kurangi ukuran titik

#### Transformasi Objek
- `S` - Pilih objek berikutnya (ditandai dengan warna kuning)
- **Transformasi Instan:**
  - `T` - Translasi secara instan
  - `Z` - Rotasi secara instan
  - `X` / `V` - Scale up/down secara instan
- **Transformasi Berkelanjutan (tahan tombol):**
  - `Q` / `E` - Putar kiri/kanan
  - `WASD` atau `Tombol Panah` - Gerakkan objek
  - `U` / `J` - Scale up/down

#### Window Clipping
- `O` - Definisikan window clipping baru (klik dua sudut)
- **Seret Window**: Klik dan seret border window merah
- `P` atau `Delete` - Hapus window clipping

#### Utilitas
- `C` - Hapus semua objek
- `Spasi` - Tampilkan instruksi detail
- `ESC` - Keluar program

### Contoh Penggunaan
```python
# Jalankan Modul A
python "Modul A.py"

# Alur kerja:
# 1. Tekan '1' untuk tool titik, 'R' untuk warna merah
# 2. Klik di canvas untuk membuat titik merah
# 3. Tekan 'S' untuk memilih titik (berubah kuning)
# 4. Tahan 'Q' untuk memutar atau 'W' untuk naik
# 5. Tekan 'O' dan klik dua sudut untuk membuat window clipping
# 6. Seret border window merah untuk memindahkan posisi
```

## Modul B: Visualisasi Objek 3D

### Fitur-Fitur

#### 🎯 1. Rendering Objek 3D
- **1.a)** Objek kubus dan piramida berkualitas tinggi
- **1.b)** Definisi vertex dan face secara manual
- Rendering anti-aliased yang halus

#### 🔄 2. Transformasi Canggih
- **2)** Rotasi terinterpolasi halus (LERP)
- Kontrol rotasi dengan drag mouse
- Pergerakan berbasis keyboard (WASD + QE)
- Mode auto-rotation

#### ✨ 3. Sistem Pencahayaan Profesional
- **3.a)** Model shading Phong dan Gouraud
- **3.b)** Setup multi-light (ambient, diffuse, specular)
- Pencahayaan beranimasi dengan sumber cahaya bergerak
- Kontrol properti material

#### 📷 4. Kamera dan Perspektif
- **4.a)** Positioning kamera dengan gluLookAt
- **4.b)** Proyeksi 3D dengan gluPerspective
- Penanganan viewport yang responsif

### Kontrol

#### Kontrol Objek
- `C` - Beralih antara kubus dan piramida
- `Seret Mouse` - Putar objek dengan halus
- `WASD` - Gerakkan objek (sumbu X, Z)
- `Q` / `E` - Gerak naik/turun (sumbu Y)

#### Mode Rendering
- `L` - Toggle pencahayaan hidup/mati
- `1` - Phong shading (halus)
- `2` - Gouraud shading (datar)
- `F` - Toggle mode wireframe
- `R` - Toggle auto-rotation

#### Interface
- `H` - Sembunyikan/tampilkan panel informasi
- `ESC` - Keluar program

### Contoh Penggunaan
```python
# Jalankan Modul B
python "Modul B.py"

# Alur kerja:
# 1. Seret mouse untuk memutar objek 3D
# 2. Tekan 'C' untuk beralih antara kubus dan piramida
# 3. Tekan '1' untuk Phong shading yang halus
# 4. Tekan 'L' untuk toggle efek pencahayaan
# 5. Gunakan WASD untuk memindahkan objek dalam ruang 3D
# 6. Tekan 'R' untuk mode auto-rotation
```

## Detail Implementasi Teknis

### Fitur Teknis Modul A
- **Sistem Koordinat OpenGL 2D**: Proyeksi ortho2D yang dioptimalkan
- **Algoritma Cohen-Sutherland**: Implementasi clipping garis profesional
- **Transformasi Halus**: Operasi matriks real-time
- **Interface yang Dapat Diseret**: Manipulasi window interaktif dengan feedback visual
- **Anti-aliasing**: Rendering garis dan titik berkualitas tinggi

### Fitur Teknis Modul B
- **Model Pencahayaan Canggih**: Pencahayaan multi-source dengan komponen ambient, diffuse, dan specular
- **Animasi LERP**: Interpolasi halus untuk gerakan natural
- **Shading Profesional**: Implementasi model Phong dan Gouraud
- **Matematika 3D**: Kalkulasi normal vector dan transformasi matriks yang tepat
- **Rendering Berkualitas Tinggi**: Anti-aliasing, depth testing, dan alpha blending

## Struktur File
```
.
├── Modul A.py          # Penggambaran dan Manipulasi Objek 2D
├── Modul B.py          # Visualisasi Objek 3D
└── README.md           # Dokumentasi ini
```

## Screenshot dan Fitur Visual

### Modul A - Grafika 2D dengan Clipping
![Modul A - Objek 2D Tanpa Window](https://i.imgur.com/demo1.png)
*Tampilan awal dengan berbagai objek 2D: titik putih, garis, persegi, dan ellipse*

![Modul A - Clipping Window Aktif](https://i.imgur.com/demo2.png)
*Fitur clipping window dengan objek di dalam window berubah hijau. Window merah dapat diseret.*

#### Highlight Modul A
- 🎨 **Preview Warna Real-time**: Indikator warna aktif di UI (kotak putih di kiri atas)
- 🎯 **Feedback Pemilihan**: Objek yang dipilih ditandai dengan warna kuning
- 🪟 **Clipping Interaktif**: Window merah yang dapat diseret dengan corner markers
- 🔄 **Transformasi Halus**: Kontrol berkelanjutan dengan menahan tombol
- ✨ **Visual Feedback**: Objek dalam window berubah hijau, luar window tetap warna asli
- 📐 **Cohen-Sutherland**: Algoritma clipping garis profesional terimplementasi

### Modul B - Visualisasi 3D Premium
![Modul B - Kubus 3D](https://i.imgur.com/demo3.png)
*Kubus 3D dengan Phong shading, setiap face memiliki warna berbeda dengan pencahayaan realistis*

![Modul B - Piramida 3D](https://i.imgur.com/demo4.png)
*Piramida 3D dengan material properties dan lighting yang sama. Panel informasi menampilkan status real-time*

#### Highlight Modul B
- 💡 **Pencahayaan Dinamis**: Sistem multi-light dengan ambient, diffuse, specular
- 🎭 **Properti Material**: Refleksi permukaan dan kilau yang realistis
- 📱 **Panel Informasi**: Status real-time di kiri atas (Object, Shading, Lighting, dll)
- 🔄 **Animasi Halus**: Rotasi terinterpolasi untuk gerakan natural
- 🎨 **Multiple Mode Render**: Beralih antara solid dan wireframe
- ✨ **Phong Shading**: Model pencahayaan smooth untuk hasil visual premium
- 🎮 **Kontrol Intuitif**: Mouse drag untuk rotasi, WASD untuk movement

## Nilai Edukasi

### Tujuan Pembelajaran yang Dicakup
1. **Fundamental Grafika Komputer**: Pipeline rendering 2D dan 3D
2. **Transformasi Geometri**: Matriks translasi, rotasi, scaling
3. **Model Pencahayaan**: Implementasi shading Phong dan Gouraud
4. **Algoritma Clipping**: Cohen-Sutherland line clipping
5. **Desain User Interface**: Pemrograman grafika interaktif
6. **Matematika 3D**: Operasi vektor, kalkulasi normal
7. **Optimisasi Performa**: Teknik rendering yang efisien

### Konsep Lanjutan yang Didemonstrasikan
- **Grafika Real-time**: Animasi halus 60 FPS
- **Sistem Interaktif**: Penanganan input mouse dan keyboard
- **Manajemen State**: Pemilihan objek dan pergantian tool
- **Feedback Visual**: Pertimbangan user experience
- **Struktur Kode Profesional**: Implementasi modular dan terdokumentasi

## Pemecahan Masalah

### Masalah Umum
1. **Error Import**: Pastikan semua paket yang diperlukan terinstal
2. **Masalah Performa**: Update driver grafis
3. **Ukuran Window**: Program menyesuaikan dengan resolusi layar
4. **Kompatibilitas OpenGL**: Memerlukan dukungan OpenGL 2.1+

### Tips Performa
- Gunakan kartu grafis dedicated jika tersedia
- Tutup aplikasi lain yang intensif grafis
- Pastikan RAM sistem cukup (4GB+ disarankan)

## Kredit dan Pengakuan

Implementasi ini mendemonstrasikan teknik pemrograman grafika komputer profesional yang cocok untuk aplikasi edukatif dan praktis. Kode menekankan arsitektur yang bersih, dokumentasi komprehensif, dan interface yang user-friendly.

**Fitur yang Diimplementasikan:**
- Grafika 2D interaktif dengan clipping canggih
- Visualisasi 3D profesional dengan pencahayaan
- Sistem animasi halus
- Kontrol pengguna yang komprehensif
- Struktur kode edukatif dengan komentar detail

## Fitur Unggulan

### Modul A - Grafika 2D Canggih
- 🖱️ **Window Draggable**: Fitur unik untuk menyeret window clipping
- 🎯 **Visual Feedback**: Window berubah warna saat hover dan drag
- 🔄 **Transformasi Real-time**: Kontrol berkelanjutan yang smooth
- 📐 **Algoritma Profesional**: Cohen-Sutherland clipping implementation
- 🎨 **UI Intuitif**: Indikator visual untuk semua status

### Modul B - Visualisasi 3D Premium
- ✨ **LERP Animation**: Rotasi terinterpolasi untuk gerakan natural
- 💡 **Multi-Light System**: Ambient, diffuse, specular lighting
- 🎭 **Dual Shading**: Phong (smooth) dan Gouraud (flat) models
- 📱 **Info Panel**: Real-time status display dengan font rendering
- 🔄 **Auto-Rotation**: Mode animasi otomatis dengan timing control

## Panduan Cepat

### Memulai dengan Modul A
1. **Setup Awal**: `python "Modul A.py"`
2. **Buat Objek**: `1` (titik) → `R` (merah) → klik canvas
3. **Transform**: `S` (pilih) → `Q` (putar) atau `WASD` (gerak)
4. **Clipping**: `O` → klik 2 sudut → seret window merah

### Memulai dengan Modul B
1. **Setup Awal**: `python "Modul B.py"`
2. **Rotasi**: Seret mouse untuk putar objek
3. **Ganti Objek**: `C` untuk toggle kubus/piramida
4. **Shading**: `1` (Phong) atau `2` (Gouraud)
5. **Movement**: `WASD` + `QE` untuk navigasi 3D

---

*Untuk pertanyaan atau masalah, silakan rujuk dokumentasi inline yang detail dalam setiap modul.*
