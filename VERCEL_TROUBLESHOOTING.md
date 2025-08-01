# 🔧 Troubleshooting Vercel Deployment

## ❌ Error: "functions and builds cannot be used together"

### Penyebab
Menggunakan kedua property `functions` dan `builds` dalam `vercel.json` secara bersamaan.

### Solusi

#### Option 1: Gunakan `functions` (Recommended)
```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  }
}
```

#### Option 2: Gunakan `builds` (Legacy)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

#### Option 3: Tanpa vercel.json
Hapus file `vercel.json` dan biarkan Vercel auto-detect Python project.

## 🔄 Langkah-langkah Perbaikan

### 1. Update vercel.json
```bash
# Backup file lama
cp vercel.json vercel.json.backup

# Gunakan konfigurasi yang benar
# (lihat solusi di atas)
```

### 2. Commit dan Push
```bash
git add vercel.json
git commit -m "Fix vercel.json configuration"
git push origin main
```

### 3. Redeploy di Vercel
- Buka Vercel dashboard
- Pilih project
- Klik "Redeploy"

## 🚨 Error Lainnya

### "Module not found"
**Penyebab**: Dependencies tidak terinstall
**Solusi**: 
- Pastikan `requirements.txt` ada dan benar
- Check build logs di Vercel dashboard

### "Import error"
**Penyebab**: Struktur folder tidak benar
**Solusi**:
- Pastikan ada `__init__.py` di setiap folder
- Check import paths di `api/index.py`

### "Function timeout"
**Penyebab**: Request terlalu lama
**Solusi**:
- Optimize OCR processing
- Reduce file size limit
- Use async processing

### "Static files not found"
**Penyebab**: Route static files tidak dikonfigurasi
**Solusi**:
```json
{
  "functions": {
    "api/index.py": {
      "maxDuration": 30
    }
  },
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

## 📋 Checklist Deployment

### Pre-Deployment
- [ ] ✅ `vercel.json` konfigurasi benar
- [ ] ✅ `requirements.txt` lengkap
- [ ] ✅ `api/index.py` ada dan benar
- [ ] ✅ Environment variables set
- [ ] ✅ OCR service configured

### Post-Deployment
- [ ] ✅ Build success
- [ ] ✅ Function accessible
- [ ] ✅ Static files served
- [ ] ✅ Database working
- [ ] ✅ OCR working

## 🔍 Debug Steps

### 1. Check Build Logs
```bash
# Di Vercel dashboard
# Project > Deployments > Latest > Build Logs
```

### 2. Check Function Logs
```bash
# Di Vercel dashboard
# Project > Functions > api/index.py > Logs
```

### 3. Test Locally
```bash
# Test sebelum deploy
python test_local.py
python run.py
```

### 4. Check Environment Variables
```bash
# Di Vercel dashboard
# Project > Settings > Environment Variables
```

## 📞 Support

Jika masih ada masalah:

1. **Vercel Documentation**: https://vercel.com/docs
2. **FastAPI on Vercel**: https://vercel.com/docs/functions/serverless-functions/runtimes/python
3. **Community**: https://github.com/vercel/vercel/discussions
4. **Support**: https://vercel.com/support

## 🎯 Quick Fix

Jika ingin cepat deploy tanpa masalah:

1. **Hapus vercel.json**
2. **Deploy tanpa konfigurasi**
3. **Vercel akan auto-detect Python project**
4. **Set environment variables manual**

```bash
# Hapus vercel.json
rm vercel.json

# Commit dan push
git add .
git commit -m "Remove vercel.json for auto-detection"
git push origin main
``` 