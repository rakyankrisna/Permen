# Panduan Deployment Permen di Vercel

## 🚀 Langkah-langkah Deployment

### 1. Persiapan Repository

Pastikan kode sudah di-push ke GitHub/GitLab:

```bash
git add .
git commit -m "Restructure for Vercel deployment"
git push origin main
```

### 2. Setup Vercel Account

1. Daftar di [vercel.com](https://vercel.com)
2. Login dengan GitHub/GitLab account
3. Klik "New Project"

### 3. Connect Repository

1. Pilih repository yang berisi kode Permen
2. Vercel akan otomatis mendeteksi sebagai Python project
3. Klik "Deploy"

### 4. Konfigurasi Build Settings

Di halaman konfigurasi project:

- **Framework Preset**: Other
- **Root Directory**: `./` (default)
- **Build Command**: `pip install -r requirements.txt`
- **Output Directory**: `api`
- **Install Command**: `pip install -r requirements.txt`

### 5. Environment Variables

Tambahkan environment variables di Vercel dashboard:

```bash
# Session secret (generate random string)
SESSION_SECRET=your-super-secret-key-here

# OCR Service (pilih salah satu)
OCR_SPACE_API_KEY=your-ocr-space-api-key

# Atau untuk Google Cloud Vision
GOOGLE_APPLICATION_CREDENTIALS=path-to-credentials.json
```

### 6. Deploy

1. Klik "Deploy"
2. Tunggu proses build selesai
3. Aplikasi akan live di URL yang diberikan

## 🔧 Konfigurasi Vercel

### vercel.json
File `vercel.json` sudah dikonfigurasi dengan benar:

```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

**Catatan Penting**: 
- Jangan menggunakan `builds` dan `functions` bersamaan
- Gunakan hanya `functions` untuk konfigurasi timeout
- Vercel akan otomatis mendeteksi Python project

### Troubleshooting vercel.json

Jika mendapat error:
- **"functions and builds cannot be used together"**: Hapus salah satu property
- **"maxDuration not supported"**: Gunakan format yang benar
- **"route not found"**: Pastikan path ke `api/index.py` benar

## 🔧 Setup OCR Service

### Option 1: OCR.space API (Recommended)

1. Daftar di [ocr.space](https://ocr.space/ocrapi)
2. Dapatkan API key gratis (500 requests/day)
3. Set environment variable:
   ```bash
   OCR_SPACE_API_KEY=your-api-key
   ```

### Option 2: Google Cloud Vision API

1. Setup Google Cloud Project
2. Enable Vision API
3. Create service account
4. Download credentials JSON
5. Set environment variable:
   ```bash
   GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
   ```

## 📁 Struktur File untuk Vercel

```
Permen/
├── api/
│   ├── __init__.py
│   └── index.py          # Main FastAPI app
├── utils/
│   ├── __init__.py
│   ├── ocr_cloud.py      # Cloud OCR utilities
│   └── document_extractor.py
├── templates/            # HTML templates
├── static/              # Static files
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel configuration
└── README.md
```

## 🚨 Limitations Vercel

### File System
- Tidak ada persistent file system
- Semua file temporary
- Gunakan cloud storage untuk file upload

### Database
- SQLite tidak persistent
- Data hilang setelah cold start
- Gunakan external database

### Memory & Timeout
- Maksimal 1024MB RAM
- Maksimal 30 detik per request
- Optimize untuk serverless

## 🔄 Continuous Deployment

Setelah setup awal:

1. Setiap push ke `main` branch akan auto-deploy
2. Preview deployments untuk pull requests
3. Rollback ke versi sebelumnya jika ada masalah

## 🐛 Troubleshooting

### Build Errors

1. **Module not found**: Pastikan semua dependencies di `requirements.txt`
2. **Import errors**: Check struktur folder dan `__init__.py` files
3. **Path issues**: Gunakan relative paths, bukan absolute
4. **vercel.json errors**: Pastikan konfigurasi benar

### Runtime Errors

1. **OCR not working**: Check environment variables
2. **Database errors**: SQLite tidak persistent di Vercel
3. **File upload errors**: Gunakan cloud storage

### Performance Issues

1. **Cold start**: Pertama kali load akan lambat
2. **Memory limits**: Optimize image processing
3. **Timeout**: Batasi ukuran file upload

## 📊 Monitoring

1. **Vercel Analytics**: Lihat performance metrics
2. **Function Logs**: Debug runtime errors
3. **Error Tracking**: Setup error monitoring

## 🔒 Security

1. **Environment Variables**: Jangan commit secrets ke repo
2. **CORS**: Configure untuk domain yang diizinkan
3. **Rate Limiting**: Implement rate limiting untuk API
4. **Input Validation**: Validate semua user input

## 🚀 Production Checklist

- [ ] Environment variables configured
- [ ] OCR service working
- [ ] Database setup (external)
- [ ] File storage configured
- [ ] Error monitoring setup
- [ ] Performance optimized
- [ ] Security measures implemented
- [ ] Backup strategy in place

## 📞 Support

Jika ada masalah:

1. Check Vercel documentation
2. Review function logs
3. Test locally first
4. Contact support jika diperlukan 