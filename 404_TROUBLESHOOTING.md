# 🔧 Troubleshooting 404 Error di Vercel

## ❌ Masalah: Halaman 404 Setelah Deploy

### Kemungkinan Penyebab

1. **Konfigurasi vercel.json salah**
2. **Path routing tidak benar**
3. **FastAPI app tidak terdeteksi**
4. **Static files tidak ditemukan**
5. **Environment variables tidak set**

## 🔧 Solusi Step by Step

### 1. Periksa Konfigurasi vercel.json

#### Konfigurasi yang Benar:
```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

#### Atau Konfigurasi Sederhana:
```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ]
}
```

### 2. Periksa Struktur File

```
Permen/
├── api/
│   ├── __init__.py          # ✅ Harus ada
│   └── index.py             # ✅ Main FastAPI app
├── templates/               # ✅ HTML templates
├── static/                  # ✅ Static files
├── utils/                   # ✅ Utility modules
├── requirements.txt         # ✅ Dependencies
└── vercel.json             # ✅ Vercel config
```

### 3. Test Endpoint Sederhana

Buat file `api/test.py` untuk testing:

```python
from http.server import BaseHTTPRequestHandler

def handler(request):
    return {
        "statusCode": 200,
        "body": "Hello from Vercel!",
        "headers": {
            "Content-Type": "text/plain"
        }
    }
```

### 4. Periksa Build Logs

Di Vercel dashboard:
1. Buka project
2. Klik deployment terbaru
3. Lihat "Build Logs"
4. Cari error messages

### 5. Periksa Function Logs

Di Vercel dashboard:
1. Buka project
2. Klik "Functions"
3. Pilih `api/index.py`
4. Lihat "Logs"

## 🚨 Error Umum dan Solusi

### "Module not found"
**Solusi:**
- Pastikan `requirements.txt` ada dan benar
- Check import paths di `api/index.py`
- Pastikan ada `__init__.py` di setiap folder

### "Template not found"
**Solusi:**
```python
# Di api/index.py, pastikan path benar
templates = Jinja2Templates(directory="../templates")
```

### "Static files not found"
**Solusi:**
```python
# Di api/index.py, pastikan path benar
app.mount("/static", StaticFiles(directory="../static"), name="static")
```

### "Database error"
**Solusi:**
```python
# Gunakan path yang benar untuk Vercel
DB_PATH = "/tmp/histori_pemeriksaan.db"
```

## 🔄 Langkah-langkah Debug

### Step 1: Test Lokal
```bash
# Test aplikasi lokal
python test_local.py
python run.py
```

### Step 2: Check Dependencies
```bash
# Pastikan semua dependencies ada
pip install -r requirements.txt
```

### Step 3: Test Import
```bash
# Test import modules
python -c "from api.index import app; print('Import success')"
```

### Step 4: Deploy Test
```bash
# Deploy dengan konfigurasi sederhana
cp vercel-simple.json vercel.json
git add .
git commit -m "Test simple vercel config"
git push origin main
```

## 📋 Checklist Debug

### Pre-Deployment
- [ ] ✅ `api/index.py` ada dan benar
- [ ] ✅ `requirements.txt` lengkap
- [ ] ✅ `vercel.json` konfigurasi benar
- [ ] ✅ `__init__.py` di setiap folder
- [ ] ✅ Templates dan static files ada

### Post-Deployment
- [ ] ✅ Build success
- [ ] ✅ Function accessible
- [ ] ✅ Root endpoint (`/`) berfungsi
- [ ] ✅ Static files served
- [ ] ✅ Templates rendered

## 🎯 Quick Fix

Jika masih 404, coba ini:

### Option 1: Hapus vercel.json
```bash
rm vercel.json
git add .
git commit -m "Remove vercel.json for auto-detection"
git push origin main
```

### Option 2: Gunakan Konfigurasi Minimal
```bash
# Gunakan vercel-simple.json
cp vercel-simple.json vercel.json
git add .
git commit -m "Use minimal vercel config"
git push origin main
```

### Option 3: Test dengan Endpoint Sederhana
```bash
# Ganti api/index.py dengan test sederhana
cp api/test.py api/index.py
git add .
git commit -m "Test simple endpoint"
git push origin main
```

## 📞 Support

Jika masih bermasalah:

1. **Check Vercel Documentation**: https://vercel.com/docs
2. **FastAPI on Vercel**: https://vercel.com/docs/functions/serverless-functions/runtimes/python
3. **Community**: https://github.com/vercel/vercel/discussions
4. **Function Logs**: Di Vercel dashboard > Functions > Logs

## 🔍 Debug Commands

```bash
# Test lokal
python -c "import fastapi; print('FastAPI version:', fastapi.__version__)"

# Test import
python -c "from api.index import app; print('App created successfully')"

# Test templates
python -c "from fastapi.templating import Jinja2Templates; print('Templates OK')"

# Test static files
python -c "from fastapi.staticfiles import StaticFiles; print('Static files OK')"
``` 