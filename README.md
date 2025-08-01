# Permen - Sistem Analisis Dokumen Pemeriksaan BPK

Aplikasi web untuk analisis dan ekstraksi informasi dari dokumen PDF pemeriksaan BPK (Badan Pemeriksa Keuangan). Aplikasi ini dapat mendeteksi dan mengekstrak berbagai jenis dokumen seperti SPM, SP2D, SPP, dan dokumen pemeriksaan lainnya.

## 🚀 Fitur Utama

- **Upload Dokumen PDF**: Upload file PDF untuk dianalisis
- **OCR & Text Extraction**: Ekstraksi teks dari PDF menggunakan cloud OCR
- **Document Detection**: Deteksi otomatis jenis dokumen (SPM, SP2D, SPP, SK, dll)
- **Information Extraction**: Ekstraksi informasi detail dari dokumen
- **User Authentication**: Sistem login dengan domain @bpk.go.id
- **History Tracking**: Riwayat analisis dokumen
- **Modern UI**: Interface yang modern dan responsif

## 🛠️ Teknologi yang Digunakan

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS (Tailwind CSS), JavaScript
- **Database**: SQLite (untuk development)
- **OCR**: Cloud-based OCR (Google Cloud Vision API / OCR.space)
- **Deployment**: Vercel (Serverless)

## 📋 Jenis Dokumen yang Didukung

- **SPM** (Surat Perintah Membayar)
- **SP2D** (Surat Perintah Pencairan Dana)
- **SPP** (Surat Permintaan Pembayaran)
- **SK** (Surat Keputusan)
- **Surat Tugas**
- **BAPP** (Berita Acara Penyelesaian Pekerjaan)
- **BAST** (Berita Acara Serah Terima)
- **BA Pembayaran**
- **Surat Perjanjian**
- **Kontrak**
- **SPK** (Surat Perintah Kerja)
- **SPMK** (Surat Perintah Mulai Kerja)
- **Kwitansi**
- **Invoice**

## 🚀 Deployment di Vercel

### Prerequisites

1. **Vercel Account**: Daftar di [vercel.com](https://vercel.com)
2. **Git Repository**: Push kode ke GitHub/GitLab
3. **OCR Service**: Setup salah satu OCR service:
   - [OCR.space API](https://ocr.space/ocrapi) (Free tier available)
   - [Google Cloud Vision API](https://cloud.google.com/vision)

### Setup Environment Variables

Di Vercel dashboard, tambahkan environment variables:

```bash
# Session secret untuk FastAPI
SESSION_SECRET=your-super-secret-key-here

# OCR Service (pilih salah satu)
OCR_SPACE_API_KEY=your-ocr-space-api-key

# Atau untuk Google Cloud Vision
GOOGLE_APPLICATION_CREDENTIALS=path-to-credentials.json
```

### Deploy Steps

1. **Connect Repository**:
   ```bash
   # Di Vercel dashboard, connect ke repository GitHub/GitLab
   ```

2. **Configure Build Settings**:
   - Framework Preset: Other
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `api`
   - Install Command: `pip install -r requirements.txt`

3. **Deploy**:
   ```bash
   # Vercel akan otomatis deploy saat ada push ke main branch
   git push origin main
   ```

## 🏃‍♂️ Local Development

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd Permen
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Environment Variables**:
   ```bash
   # Buat file .env
   echo "SESSION_SECRET=your-secret-key" > .env
   echo "OCR_SPACE_API_KEY=your-api-key" >> .env
   ```

4. **Run Application**:
   ```bash
   # Development server
   uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
   
   # Atau untuk production
   uvicorn api.index:app --host 0.0.0.0 --port 8000
   ```

5. **Access Application**:
   ```
   http://localhost:8000
   ```

## 📁 Struktur Project

```
Permen/
├── api/
│   └── index.py              # Main FastAPI application
├── utils/
│   ├── ocr_cloud.py          # Cloud OCR utilities
│   └── document_extractor.py # Document extraction logic
├── templates/
│   ├── base.html             # Base template
│   ├── dashboard.html        # Dashboard page
│   ├── upload.html           # Upload page
│   ├── hasil.html            # Results page
│   ├── history.html          # History page
│   ├── profile.html          # Profile page
│   ├── login.html            # Login page
│   └── register.html         # Register page
├── static/
│   └── logo_bpk.png          # Static assets
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration
└── README.md                # This file
```

## 🔧 Konfigurasi OCR

### OCR.space API (Recommended untuk development)

1. Daftar di [ocr.space](https://ocr.space/ocrapi)
2. Dapatkan API key gratis
3. Set environment variable:
   ```bash
   OCR_SPACE_API_KEY=your-api-key
   ```

### Google Cloud Vision API

1. Setup Google Cloud Project
2. Enable Vision API
3. Create service account dan download credentials
4. Set environment variable:
   ```bash
   GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
   ```

## 🔐 Authentication

- Sistem login menggunakan email dengan domain `@bpk.go.id`
- Password di-hash menggunakan bcrypt
- Session management dengan FastAPI SessionMiddleware

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### History Table
```sql
CREATE TABLE histori (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    nomor_surat_tugas TEXT,
    instansi_terperiksa TEXT,
    nama_file TEXT,
    hasil_analisis TEXT,
    waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚨 Limitations & Considerations

### Vercel Limitations
- **File System**: Tidak ada persistent file system, semua file temporary
- **Database**: SQLite tidak persistent di Vercel, data akan hilang setelah cold start
- **Memory**: Maksimal 1024MB RAM per function
- **Timeout**: Maksimal 30 detik per request

### Recommendations untuk Production
1. **Database**: Gunakan PostgreSQL/MySQL dengan Vercel Postgres atau external provider
2. **File Storage**: Gunakan AWS S3, Google Cloud Storage, atau Vercel Blob
3. **OCR Service**: Setup dedicated OCR service untuk performa yang lebih baik

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

Untuk bantuan dan pertanyaan:
- Email: support@bpk.go.id
- Documentation: [Link ke dokumentasi]
- Issues: [GitHub Issues](https://github.com/your-repo/issues)

## 🔄 Changelog

### v2.0.0 (Current)
- ✅ Restructured untuk Vercel deployment
- ✅ Cloud-based OCR implementation
- ✅ Modern UI dengan Tailwind CSS
- ✅ Improved document extraction
- ✅ Better error handling
- ✅ Responsive design

### v1.0.0 (Original)
- ✅ Basic PDF analysis
- ✅ Local OCR dengan pytesseract
- ✅ Simple web interface
- ✅ Local file processing 
