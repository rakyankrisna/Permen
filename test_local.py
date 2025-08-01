#!/usr/bin/env python3
"""
Local testing script for Permen application
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_test_environment():
    """Setup test environment variables"""
    os.environ.setdefault('SESSION_SECRET', 'test-secret-key-for-local-development')
    os.environ.setdefault('DEBUG', 'True')
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    os.environ.setdefault('DB_PATH', temp_db.name)
    temp_db.close()
    
    print(f"✅ Test environment setup complete")
    print(f"📁 Temporary database: {temp_db.name}")
    return temp_db.name

def cleanup_test_environment(db_path):
    """Cleanup test environment"""
    try:
        os.unlink(db_path)
        print(f"✅ Cleaned up temporary database: {db_path}")
    except Exception as e:
        print(f"⚠️  Warning: Could not cleanup {db_path}: {e}")

def test_imports():
    """Test if all modules can be imported"""
    try:
        from api.index import app
        from utils.ocr_cloud import extract_text_from_pdf
        from utils.document_extractor import extract_document_details
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_initialization():
    """Test database initialization"""
    try:
        from api.index import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation"""
    try:
        from api.index import app
        print(f"✅ FastAPI app created: {app.title}")
        return True
    except Exception as e:
        print(f"❌ FastAPI app error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Starting local tests for Permen application...")
    print("=" * 50)
    
    # Setup test environment
    db_path = setup_test_environment()
    
    try:
        # Run tests
        tests = [
            ("Module Imports", test_imports),
            ("Database Initialization", test_database_initialization),
            ("FastAPI App", test_fastapi_app),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Application is ready for deployment.")
            print("\n🚀 To run the application locally:")
            print("   python run.py")
            print("\n🌐 Or with uvicorn:")
            print("   uvicorn api.index:app --reload --host 0.0.0.0 --port 8000")
        else:
            print("⚠️  Some tests failed. Please check the errors above.")
            return 1
            
    finally:
        # Cleanup
        cleanup_test_environment(db_path)
    
    return 0

if __name__ == "__main__":
    exit(main()) 