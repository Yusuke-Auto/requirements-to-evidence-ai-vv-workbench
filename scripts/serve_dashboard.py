#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

url = "http://127.0.0.1:8000/docs/dashboard.html"
print(f"Serving repository at http://127.0.0.1:8000")
print(f"Dashboard: {url}")
try:
    webbrowser.open(url)
except Exception:
    pass

ThreadingHTTPServer(("127.0.0.1", 8000), SimpleHTTPRequestHandler).serve_forever()
