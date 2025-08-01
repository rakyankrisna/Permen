#!/usr/bin/env python3
"""
Local development server for Permen application
"""

import uvicorn
from api.index import app

if __name__ == "__main__":
    uvicorn.run(
        "api.index:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 