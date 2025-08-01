from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from passlib.hash import bcrypt
from typing import List, Optional
import os
import re
import json
import sqlite3
import pandas as pd
from datetime import datetime
import tempfile
import shutil
from pathlib import Path

# Import OCR utilities
from utils.ocr_cloud import extract_text_from_pdf
from utils.document_extractor import extract_document_details

app = FastAPI(title="Permen - Document Analysis System")

# Middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "rahasia-anda"))

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
DB_PATH = "/tmp/histori_pemeriksaan.db"

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # History table
    c.execute('''
        CREATE TABLE IF NOT EXISTS histori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            nomor_surat_tugas TEXT,
            instansi_terperiksa TEXT,
            nama_file TEXT,
            hasil_analisis TEXT,
            waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Authentication dependency
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

@app.get("/")
async def root(request: Request):
    """Root endpoint - redirect to login or dashboard"""
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login"""
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
        return RedirectResponse(url="/dashboard", status_code=302)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": "Login gagal! Email atau password salah."
    })

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """Register page"""
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Handle user registration"""
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

@app.get("/logout")
async def logout(request: Request):
    """Logout user"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard"""
    user = get_current_user(request)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user
    })

@app.get("/upload", response_class=HTMLResponse)
async def upload_form(request: Request):
    """Upload documents page"""
    user = get_current_user(request)
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "user": user
    })

@app.post("/analyze-document")
async def analyze_document(
    request: Request,
    file: UploadFile = File(...),
    nomor_surat_tugas: str = Form(...),
    instansi_terperiksa: str = Form(...)
):
    """Analyze uploaded PDF document"""
    user = get_current_user(request)
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(tmp_path)
        
        # Analyze document
        analysis_result = extract_document_details(text)
        analysis_result['nama_file'] = file.filename
        analysis_result['user'] = user
        analysis_result['nomor_surat_tugas'] = nomor_surat_tugas
        analysis_result['instansi_terperiksa'] = instansi_terperiksa
        analysis_result['waktu'] = datetime.now().isoformat()
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO histori (user, nomor_surat_tugas, instansi_terperiksa, nama_file, hasil_analisis, waktu)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user, nomor_surat_tugas, instansi_terperiksa, file.filename, json.dumps(analysis_result), analysis_result['waktu']))
        conn.commit()
        conn.close()
        
        return templates.TemplateResponse("hasil.html", {
            "request": request,
            "hasil": analysis_result,
            "user": user
        })
        
    finally:
        # Clean up temporary file
        os.unlink(tmp_path)

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    """View analysis history"""
    user = get_current_user(request)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM histori WHERE user = ? ORDER BY waktu DESC LIMIT 50", (user,))
    history_data = c.fetchall()
    conn.close()
    
    return templates.TemplateResponse("history.html", {
        "request": request,
        "user": user,
        "history": history_data
    })

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    """User profile page"""
    user = get_current_user(request)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM histori WHERE user = ?", (user,))
    total_analyses = c.fetchone()[0]
    conn.close()
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "total_analyses": total_analyses
    })

# API endpoints for AJAX calls
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/user-info")
async def get_user_info(request: Request):
    """Get current user info"""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {"user": user}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 