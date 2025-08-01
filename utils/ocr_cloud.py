"""
Cloud-based OCR utility for PDF text extraction
Uses Google Cloud Vision API or similar cloud OCR service
"""

import os
import fitz  # PyMuPDF
import base64
import requests
from typing import Optional
import json

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using cloud OCR service
    Falls back to PyMuPDF text extraction if cloud OCR is not available
    """
    try:
        # First try to extract text directly from PDF (for text-based PDFs)
        text = extract_text_direct(pdf_path)
        if text.strip():
            return text
        
        # If no text found, use cloud OCR
        return extract_text_with_cloud_ocr(pdf_path)
        
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_direct(pdf_path: str) -> str:
    """Extract text directly from PDF using PyMuPDF"""
    try:
        with fitz.open(pdf_path) as doc:
            text = ""
            for page in doc:
                text += page.get_text()
            return text
    except Exception as e:
        print(f"Error in direct text extraction: {e}")
        return ""

def extract_text_with_cloud_ocr(pdf_path: str) -> str:
    """
    Extract text using cloud OCR service
    Currently uses a mock implementation - replace with actual cloud OCR service
    """
    try:
        # Convert PDF to images and extract text
        with fitz.open(pdf_path) as doc:
            text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution
                
                # Convert to base64 for API call
                img_data = pix.tobytes("png")
                img_base64 = base64.b64encode(img_data).decode()
                
                # Call cloud OCR service (mock implementation)
                page_text = call_cloud_ocr(img_base64)
                text += page_text + "\n"
                
        return text
        
    except Exception as e:
        print(f"Error in cloud OCR: {e}")
        return ""

def call_cloud_ocr(img_base64: str) -> str:
    """
    Call cloud OCR service
    This is a mock implementation - replace with actual service like:
    - Google Cloud Vision API
    - Azure Computer Vision
    - AWS Textract
    - OCR.space API
    """
    
    # Option 1: OCR.space API (free tier available)
    api_key = os.getenv("OCR_SPACE_API_KEY")
    if api_key:
        return call_ocrspace_api(img_base64, api_key)
    
    # Option 2: Google Cloud Vision API
    google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if google_credentials:
        return call_google_vision_api(img_base64)
    
    # Fallback: Return empty string (you should implement one of the above)
    print("No OCR service configured. Please set up OCR_SPACE_API_KEY or GOOGLE_APPLICATION_CREDENTIALS")
    return ""

def call_ocrspace_api(img_base64: str, api_key: str) -> str:
    """Call OCR.space API"""
    try:
        url = "https://api.ocr.space/parse/image"
        payload = {
            'apikey': api_key,
            'base64Image': f'data:image/png;base64,{img_base64}',
            'language': 'ind',  # Indonesian
            'isOverlayRequired': False,
            'filetype': 'png',
            'detectOrientation': True,
        }
        
        response = requests.post(url, data=payload)
        result = response.json()
        
        if result.get('IsErroredOnProcessing'):
            print(f"OCR.space error: {result.get('ErrorMessage')}")
            return ""
        
        parsed_results = result.get('ParsedResults', [])
        if parsed_results:
            return parsed_results[0].get('ParsedText', '')
        
        return ""
        
    except Exception as e:
        print(f"Error calling OCR.space API: {e}")
        return ""

def call_google_vision_api(img_base64: str) -> str:
    """Call Google Cloud Vision API"""
    try:
        from google.cloud import vision
        
        client = vision.ImageAnnotatorClient()
        
        image = vision.Image(content=base64.b64decode(img_base64))
        response = client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(f"Google Vision API error: {response.error.message}")
        
        texts = response.text_annotations
        if texts:
            return texts[0].description
        
        return ""
        
    except ImportError:
        print("Google Cloud Vision library not installed. Install with: pip install google-cloud-vision")
        return ""
    except Exception as e:
        print(f"Error calling Google Vision API: {e}")
        return ""

# Alternative: Simple text extraction for development/testing
def extract_text_simple(pdf_path: str) -> str:
    """
    Simple text extraction for development/testing
    This is a fallback that doesn't require external services
    """
    try:
        with fitz.open(pdf_path) as doc:
            text = ""
            for page in doc:
                # Try to get text directly
                page_text = page.get_text()
                if page_text.strip():
                    text += page_text + "\n"
                else:
                    # If no text, try to get text from images (basic OCR simulation)
                    text += f"[Page {page.number + 1} - Image content detected]\n"
            return text
    except Exception as e:
        print(f"Error in simple text extraction: {e}")
        return "" 