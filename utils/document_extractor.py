"""
Document extraction utilities for analyzing PDF content
"""

import re
from typing import Dict, Any

def extract_document_details(text: str) -> Dict[str, Any]:
    """
    Extract document details from text
    Returns a dictionary with all detected document types and their details
    """
    upper_text = text.upper()
    
    # Check document types
    status = {
        "SPM": "Ada" if "SURAT PERINTAH MEMBAYAR" in upper_text else "Tidak Ada",
        "DAFTAR_SP2D": "Ada" if "DAFTAR SP2D SATKER" in upper_text else "Tidak Ada",
        "SP2D": "Ada" if "SURAT PERINTAH PENCAIRAN DANA" in upper_text else "Tidak Ada",
        "SPP": "Ada" if "SURAT PERMINTAAN PEMBAYARAN" in upper_text else "Tidak Ada",
        "SK": "Ada" if "KEPUTUSAN" in upper_text and all(k in text for k in ["Menimbang", "Mengingat", "Menetapkan"]) else "Tidak Ada",
        "SURAT_TUGAS": "Ada" if "SURAT TUGAS" in upper_text and any(k in upper_text for k in ["MENUGASKAN", "MEMBERI TUGAS"]) else "Tidak Ada",
        "BAPP": "Ada" if "BERITA ACARA" in upper_text and "PENYELESAIAN PEKERJAAN" in upper_text else "Tidak Ada",
        "BAST": "Ada" if "BERITA ACARA" in upper_text and "SERAH TERIMA" in upper_text else "Tidak Ada",
        "BA_PEMBAYARAN": "Ada" if "BERITA ACARA" in upper_text and "PEMBAYARAN" in upper_text else "Tidak Ada",
        "SURAT_PERJANJIAN": "Ada" if "SURAT PERJANJIAN" in upper_text else "Tidak Ada",
        "KONTRAK": "Ada" if "KONTRAK" in upper_text else "Tidak Ada",
        "SPK": "Ada" if "SURAT PERINTAH KERJA" in upper_text else "Tidak Ada",
        "SPMK": "Ada" if "SURAT PERINTAH MULAI KERJA" in upper_text else "Tidak Ada",
        "KWITANSI": "Ada" if "KWITANSI" in upper_text or "KUITANSI" in upper_text else "Tidak Ada",
        "INVOICE": "Ada" if "INVOICE" in upper_text else "Tidak Ada",
    }
    
    # Extract details for each document type
    result = {**status}
    
    if status["SPM"] == "Ada":
        result.update(extract_detail_spm(text))
    
    if status["DAFTAR_SP2D"] == "Ada":
        result.update(extract_detail_daftar_sp2d(text))
    
    if status["SP2D"] == "Ada":
        result.update(extract_detail_sp2d(text))
    
    if status["SPP"] == "Ada":
        result.update(extract_detail_spp(text))
    
    return result

def extract_detail_spm(text: str) -> Dict[str, str]:
    """Extract SPM (Surat Perintah Membayar) details"""
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

def extract_detail_daftar_sp2d(text: str) -> Dict[str, str]:
    """Extract Daftar SP2D details"""
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

def extract_detail_sp2d(text: str) -> Dict[str, str]:
    """Extract SP2D (Surat Perintah Pencairan Dana) details"""
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

def extract_detail_spp(text: str) -> Dict[str, str]:
    """Extract SPP (Surat Permintaan Pembayaran) details"""
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