import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "libs"))

import uvicorn
from app.main import app

uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
