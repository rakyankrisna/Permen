from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from passlib.hash import bcrypt
from typing import List
from utils.ocr import ocr_pdf_to_text
from time import perf_counter

import os
import re
import pytesseract
import sqlite3
import pandas as pd
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="rahasia-anda")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_PATH = "histori_pemeriksaan.db"
LAST_ST_PATH = "last_st.txt"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Tabel users
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Tabel histori
    c.execute('''
        CREATE TABLE IF NOT EXISTS histori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            nomor_surat_tugas TEXT,
            instansi_terperiksa TEXT,
            nama_file TEXT,
            waktu TEXT
        )
    ''')

    conn.commit()
    conn.close()

# ✅ Panggil saat startup
init_db()

# ====== FUNGSI EKSTRAKSI DETAIL DOKUMEN (copy dari kamu, tidak diubah) ======
# ... (Semua fungsi seperti extract_detail_spm, extract_detail_sp2d, dst.) ...
# (Untuk ringkasnya, aku akan salin ulang fungsi detail kamu nanti)

# ====== LOGIKA UTAMA PEMROSESAN FOLDER ======
def ocr_pdf(pdf_path: str) -> str:
    try:
        images = convert_from_path(pdf_path)
        text = ""
        for img in images:
            gray = img.convert("L")
            text += pytesseract.image_to_string(gray, lang="ind") + "\n"
        return text
    except Exception as e:
        return ""

# ===== Fungsi Ekstraksi Dokumen =====

def extract_detail_spm(text: str) -> dict:
    jenis_dokumen = "Surat Perintah Membayar"
    nomor, tanggal = "", ""
    for line in text.splitlines():
        if "Nomor" in line and "Tanggal" in line:
            nomor_match = re.search(r"Nomor\s+([A-Za-z0-9\-\/]+)", line)
            tanggal_match = re.search(r"Tanggal\s+([0-9]{1,2}[-/ ][A-Za-z]{3,9}[-/ ][0-9]{4})", line)
            if nomor_match:
                nomor = nomor_match.group(1).strip()
            if tanggal_match:
                tanggal = tanggal_match.group(1).strip()
            break
    dipa_match = re.search(r"(DIPA[-\s:]?\d{3}\.\d{2}\.\d{1}\.\d{6}/\d{4})", text)
    dipa = dipa_match.group(1).strip() if dipa_match else ""
    nominal = ""
    for line in text.splitlines():
        if "TOTAL" in line.upper() or "PEMBAYARAN" in line.upper():
            match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})", line)
            if match:
                nominal = match.group(1).strip()
                break
    return {
        "jenis_dokumen": jenis_dokumen,
        "nomor_spm": nomor,
        "tanggal_spm": tanggal,
        "dipa_spm": dipa,
        "nominal_spm": nominal
    }

def extract_detail_daftar_sp2d(text: str) -> dict:
    jenis_dokumen = "DAFTAR SP2D SATKER"
    nomor, tanggal, nominal = "", "", ""
    for line in text.splitlines():
        nomor_match = re.search(r'\b(\d{15,})\b', line)
        if nomor_match:
            nomor = nomor_match.group(1).strip()
            all_dates = re.findall(r'(\d{2}-\d{2}-\d{4})', line)
            if len(all_dates) >= 2:
                tanggal = all_dates[1]
            nominal_match = re.search(r'(\d{1,3}(?:[.,]\d{3})+[.,]\d{2})', line)
            if nominal_match:
                nominal = nominal_match.group(1).strip()
            break
    return {
        "jenis_dokumen": jenis_dokumen,
        "nomor_daftar_sp2d": nomor,
        "tanggal_daftar_sp2d": tanggal,
        "nominal_daftar_sp2d": nominal
    }

def extract_detail_sp2d(text: str) -> dict:
    jenis_dokumen = "Surat Perintah Pencairan Dana"
    nomor = ""
    tanggal = ""
    npwp = ""
    rekening = ""
    bank = ""
    jumlah = ""

    if "SURAT PERINTAH PENCAIRAN DANA" in text.upper():
        nomor_match = re.search(r'\d{5}/SP2D/\d{1,2}\.\d{2}\.\d{2}\.\d{2}/\d{4}', text)
        if nomor_match:
            nomor = nomor_match.group(0)

        tanggal_match = re.search(r'(\d{1,2}\s(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\s\d{4})', text, re.IGNORECASE)
        if tanggal_match:
            tanggal = tanggal_match.group(1)

        npwp_match = re.search(r'\d{2}\.\d{3}\.\d{3}\.\d-\d{3}\.\d{3}', text)
        if npwp_match:
            npwp = npwp_match.group(0)

        rekening_match = re.search(r'\d{3}-\d{2}-\d{7}-\d', text)
        if rekening_match:
            rekening = rekening_match.group(0)
            rekening_pos = rekening_match.end()
            sisa_text = text[rekening_pos:][:100]
            
        bank_match = re.search(r'BANK.*', sisa_text, re.IGNORECASE)
        if bank_match:
            bank = bank_match.group(0).strip()

        jumlah_match = re.search(r'Jumlah yang dibayarkan\s*Rp[.: ]*\s*([\d\.]+,\d{2})', text, re.IGNORECASE)
        if jumlah_match:
            jumlah = jumlah_match.group(1).strip()

    return {
        "jenis_dokumen": jenis_dokumen,
        "nomor_sp2d": nomor,
        "tanggal_sp2d": tanggal,
        "npwp_sp2d": npwp,
        "rekening_sp2d": rekening,
        "bank_sp2d": bank,
        "jumlah_sp2d": jumlah
    }


def extract_detail_spp(text: str) -> dict:
    jenis_dokumen = "Surat Permintaan Pembayaran"
    nomor, tanggal = "", ""
    for line in text.splitlines():
        if "Nomor" in line and "Tanggal" in line:
            nomor_match = re.search(r"Nomor\s+([A-Za-z0-9\-\/]+)", line)
            tanggal_match = re.search(r"Tanggal\s+([0-9]{1,2}[-/ ][A-Za-z]{3,9}[-/ ][0-9]{4})", line)
            if nomor_match:
                nomor = nomor_match.group(1).strip()
            if tanggal_match:
                tanggal = tanggal_match.group(1).strip()
            break
    dipa_match = re.search(r"(DIPA[-\s:]?\d{3}\.\d{2}\.\d{1}\.\d{6}/\d{4})", text)
    dipa = dipa_match.group(1).strip() if dipa_match else ""
    nominal = ""
    for line in text.splitlines():
        if "TOTAL" in line.upper() or "PEMBAYARAN" in line.upper():
            match = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})", line)
            if match:
                nominal = match.group(1).strip()
                break
    return {
        "jenis_dokumen": jenis_dokumen,
        "nomor_spp": nomor,
        "tanggal_spp": tanggal,
        "dipa_spp": dipa,
        "nominal_spp": nominal
    }

def periksa_pdf(file_path: str) -> dict:
    # Simpan hasil OCR ke dalam subfolder
    output_dir = os.path.join("hasil_teks", os.path.basename(os.path.dirname(file_path)))
    os.makedirs(output_dir, exist_ok=True)
    
    # Jalankan OCR dan simpan ke file .txt di subfolder
    text = ocr_pdf_to_text(pdf_path=file_path, output_dir=output_dir)
    upper = text.upper()

    status = {
        "SPM": "Ada" if "SURAT PERINTAH MEMBAYAR" in upper else "Tidak Ada",
        "DAFTAR_SP2D": "Ada" if "DAFTAR SP2D SATKER" in upper else "Tidak Ada",
        "SP2D": "Ada" if "SURAT PERINTAH PENCAIRAN DANA" in upper else "Tidak Ada",
        "SPP": "Ada" if "SURAT PERMINTAAN PEMBAYARAN" in upper else "Tidak Ada",
        "SK": "Ada" if "KEPUTUSAN" in upper and all(k in text for k in ["Menimbang", "Mengingat", "Menetapkan"]) else "Tidak Ada",
        "SURAT_TUGAS": "Ada" if "SURAT TUGAS" in upper and any(k in upper for k in ["MENUGASKAN", "MEMBERI TUGAS"]) else "Tidak Ada",
        "BAPP": "Ada" if "BERITA ACARA" in upper and "PENYELESAIAN PEKERJAAN" in upper else "Tidak Ada",
        "BAST": "Ada" if "BERITA ACARA" in upper and "SERAH TERIMA" in upper else "Tidak Ada",
        "BA_PEMBAYARAN": "Ada" if "BERITA ACARA" in upper and "PEMBAYARAN" in upper else "Tidak Ada",
        "SURAT_PERJANJIAN": "Ada" if "SURAT PERJANJIAN" in upper else "Tidak Ada",
        "KONTRAK": "Ada" if "KONTRAK" in upper else "Tidak Ada",
        "SPK": "Ada" if "SURAT PERINTAH KERJA" in upper else "Tidak Ada",
        "SPMK": "Ada" if "SURAT PERINTAH MULAI KERJA" in upper else "Tidak Ada",
        "KWITANSI": "Ada" if "KWITANSI" in upper or "KUITANSI" in upper else "Tidak Ada",
        "INVOICE": "Ada" if "INVOICE" in upper else "Tidak Ada",
    }

    detail_spm = extract_detail_spm(text) if status["SPM"] == "Ada" else {}
    detail_daftar_sp2d = extract_detail_daftar_sp2d(text) if status["DAFTAR_SP2D"] == "Ada" else {}
    detail_sp2d = extract_detail_sp2d(text) if status["SP2D"] == "Ada" else {}
    detail_spp = extract_detail_spp(text) if status["SPP"] == "Ada" else {}

    return {
        "nama_file": os.path.basename(file_path),
        **status,
        **detail_spm,
        **detail_daftar_sp2d,
        **detail_sp2d,
        **detail_spp
    }


def scan_folder(folder_path: str, nomor_st: str, instansi_terperiksa: str, user: str) -> list:
    results = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(root, file)
                hasil = periksa_pdf(file_path)
                hasil["user"] = user
                hasil["nomor_surat_tugas"] = nomor_st
                hasil["instansi_terperiksa"] = instansi_terperiksa
                hasil["waktu"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # simpan histori
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""
                    INSERT INTO histori (user, nomor_surat_tugas, instansi_terperiksa, nama_file, waktu)
                    VALUES (?, ?, ?, ?, ?)
                """, (user, nomor_st, instansi_terperiksa, hasil["nama_file"], hasil["waktu"]))
                conn.commit()
                conn.close()

                results.append(hasil)
    return results

def simpan_ke_excel(data: list, output_name: str):
    df = pd.DataFrame(data)

    # Urutan kolom jika ingin rapi
    kolom_utama = [
        "user", "instansi_terperiksa", "nomor_surat_tugas", "nama_file",
        "SPM", "nomor_spm", "tanggal_spm", "dipa_spm", "nominal_spm",
        "DAFTAR_SP2D", "nomor_daftar_sp2d", "tanggal_daftar_sp2d", "nominal_daftar_sp2d",
        "SP2D", "nomor_sp2d", "tanggal_sp2d", "npwp_sp2d", "rekening_sp2d", "bank_sp2d", "jumlah_sp2d",
        "SPP", "nomor_spp", "tanggal_spp", "dipa_spp", "nominal_spp",
        "SK", "SURAT_TUGAS", "BAPP", "BAST", "BA_PEMBAYARAN",
        "SURAT_PERJANJIAN", "KONTRAK", "SPK", "SPMK", "KWITANSI", "INVOICE",
        "waktu"
    ]

    kolom_tersedia = [col for col in kolom_utama if col in df.columns]
    df = df[kolom_tersedia]

    df.to_excel(output_name, index=False)


# ====== ROUTES ======
@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    if not username.lower().endswith("@bpk.go.id"):
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email harus menggunakan domain @bpk.go.id"
        })
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        hashed_password = bcrypt.hash(password)
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username.lower(), hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email sudah terdaftar!"
        })
    conn.close()
    return RedirectResponse(url="/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if not username.lower().endswith("@bpk.go.id"):
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Email harus menggunakan domain @bpk.go.id"
        })

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username.lower(),))
    row = c.fetchone()
    conn.close()

    if row and bcrypt.verify(password, row[0]):
        request.session['user'] = username.lower()
        return RedirectResponse(url="/", status_code=302)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Login gagal! Email atau password salah."
    })

@app.get("/profil", response_class=HTMLResponse)
async def profil(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    conn = sqlite3.connect("histori_pemeriksaan.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM histori WHERE user = ? ORDER BY waktu DESC", (user,))
    histori_user = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("profil.html", {
        "request": request,
        "user": user,
        "histori": histori_user,
    })

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

@app.get("/", response_class=HTMLResponse)
async def input_st(request: Request):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("input_nomor.html", {"request": request})

@app.post("/masuk")
async def masuk(nomor_surat_tugas: str = Form(...)):
    # Simpan nomor surat tugas ke session atau query param
    # Redirect ke halaman input folder
    return RedirectResponse(url=f"/input-folder?nomor_surat_tugas={nomor_surat_tugas}", status_code=302)

@app.get("/input-folder", response_class=HTMLResponse)
async def input_folder(request: Request, nomor_surat_tugas: str):
    return templates.TemplateResponse("input_folder.html", {
        "request": request,
        "nomor_surat_tugas": nomor_surat_tugas
    })


@app.post("/proses-folder", response_class=HTMLResponse)
async def proses_folder(
    request: Request,
    folder_path: str = Form(...),
    nomor_surat_tugas: str = Form(...),
    instansi_terperiksa: str = Form(...)
):
    with open(LAST_ST_PATH, "w", encoding="utf-8") as f:
        f.write(nomor_surat_tugas)

    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Hitung jumlah file PDF
    jumlah_file = sum(
        len([f for f in files if f.lower().endswith('.pdf')])
        for _, _, files in os.walk(folder_path)
    )

    # Mulai stopwatch
    start_time = perf_counter()

    # Pemeriksaan dimulai
    hasil = scan_folder(folder_path, nomor_surat_tugas, instansi_terperiksa, user)

    # Simpan hasil ke Excel
    output_file = f"hasil_pemeriksaan_{nomor_surat_tugas.replace('/', '_')}.xlsx"
    if os.path.exists(output_file):
        os.remove(output_file)
    simpan_ke_excel(hasil, output_file)

    # Selesai stopwatch
    durasi = round(perf_counter() - start_time, 2)

    return templates.TemplateResponse("pemeriksaan.html", {
        "request": request,
        "hasil": hasil,
        "file_excel": output_file,
        "nomor_surat_tugas": nomor_surat_tugas,
        "instansi_terperiksa": instansi_terperiksa,
        "user": user,
        "durasi": durasi,
        "jumlah_file": jumlah_file
    })




@app.get("/download")
async def download_excel(file: str):
    return FileResponse(file, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file)
