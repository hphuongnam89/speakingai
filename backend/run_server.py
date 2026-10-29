import sys
import os
import logging
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))
os.chdir(str(backend_dir))

import uvicorn

if __name__ == "__main__":
    try:
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False, access_log=True)
    except Exception as e:
        logging.exception(f"Fatal error running server: {e}")
        raise
