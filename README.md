# Sistem Manajemen Kompetisi PDC 2025

Platform web untuk mengelola pendaftaran, verifikasi, dan administrasi kompetisi siswa (akademik, kreatif, performa) secara online.

## Teknologi yang Digunakan

- **Backend:** Flask (Python)
- **Database:** SQLAlchemy ORM (SQLite untuk pengembangan, PostgreSQL untuk produksi)
- **Autentikasi:** Flask-Login
- **Formulir:** Flask-WTF & WTForms
- **Frontend:** Bootstrap 5 + Jinja2
- **Bahasa:** UI sepenuhnya dalam Bahasa Indonesia

## Cara Instalasi & Menjalankan (Development)

1. **Clone repository & masuk ke folder proyek:**
   ```bash
   git clone <repo-url>
   cd pdc
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Copy file environment:**
   ```bash
   cp .env.example .env
   # Atur variabel di .env jika perlu
   ```
4. **Jalankan aplikasi:**
   ```bash
   python run.py
   ```
5. **Akses aplikasi di browser:**
   [http://localhost:5000](http://localhost:5000)

## Struktur Proyek

```
app/
├── __init__.py           # Inisialisasi Flask app
├── config.py             # Konfigurasi aplikasi
├── blueprints/           # Modularisasi route (main, auth, admin, dll)
├── models/               # Model database
├── forms/                # Formulir WTForms
├── templates/            # Template HTML (Jinja2 + Bootstrap)
├── static/               # File statis (CSS, JS, gambar)
└── utils/                # Fungsi utilitas
```

## Fitur Utama

- Registrasi & login pengguna
- Manajemen profil peserta
- Pendaftaran kompetisi individu & tim
- Upload dokumen & bukti pembayaran
- Verifikasi & approval admin
- Dashboard peserta & admin
- Harga early bird & reguler
- Export data peserta & pembayaran

## Daftar Route Penting

- `/` — Beranda
- `/auth/masuk` — Login
- `/auth/daftar` — Daftar akun
- `/dashboard` — Dashboard peserta
- `/kompetisi` — Daftar kompetisi
- `/kompetisi/<id>` — Detail kompetisi
- `/admin/dashboard` — Dashboard admin
- `/admin/kompetisi` — Kelola kompetisi (admin)

## Catatan Pengembangan

- Pastikan Python 3.8+ sudah terinstall.
- Untuk development gunakan SQLite, untuk produksi disarankan PostgreSQL.
- Semua fitur utama sudah tersedia, silakan laporkan bug atau request fitur baru via issues.

---

Dikembangkan untuk PDC 2025. Kontribusi & feedback sangat dihargai!