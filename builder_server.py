#!/usr/bin/env python3
"""
Jekyll Local HTML Builders Server for Linux
Provides direct filesystem access to save posts, news, projects, books, and images.
Zero external dependencies (uses standard Python library).
"""

import os
import sys
import json
import base64
import argparse
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

ALLOWED_SAVE_FOLDERS = {"_posts", "_books", "_news", "_projects"}
ALLOWED_UPLOAD_FOLDERS = {"assets/img", "assets/img/book_covers", "assets/img/projects"}


class BuilderRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

    def end_headers(self):
        # Enable CORS for local cross-origin requests (e.g., file:// or localhost:4000)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Requested-With")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # API: Status check
        if self.path == "/api/status" or self.path.startswith("/api/status?"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            status_data = {
                "ok": True,
                "mode": "server",
                "os": "linux" if sys.platform.startswith("linux") else sys.platform,
                "root": str(REPO_ROOT),
                "folders": {
                    folder: (REPO_ROOT / folder).is_dir()
                    for folder in ALLOWED_SAVE_FOLDERS | ALLOWED_UPLOAD_FOLDERS
                },
            }
            self.wfile.write(json.dumps(status_data).encode("utf-8"))
            return

        # Dashboard landing page at root
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jekyll Local Builders Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-gray-100 text-gray-800 min-h-screen p-8 flex flex-col justify-center items-center">
    <div class="max-w-2xl w-full bg-white rounded-xl shadow-md border border-gray-200 p-8">
        <div class="flex items-center space-x-3 mb-6">
            <span class="inline-flex p-3 rounded-lg bg-blue-100 text-blue-600 text-2xl">
                <i class="fa-solid fa-layer-group"></i>
            </span>
            <div>
                <h1 class="text-2xl font-bold text-gray-900">Jekyll Local Builders</h1>
                <p class="text-sm text-green-600 font-medium"><i class="fa-solid fa-circle-check mr-1"></i> Connected to Linux Filesystem ({REPO_ROOT})</p>
            </div>
        </div>

        <p class="text-gray-600 mb-6 text-sm">
            Select a builder to create and edit content. Files and images are saved directly to your local Jekyll repository without manual copy-pasting.
        </p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <a href="/post-builder.html" class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow transition bg-gray-50 group">
                <i class="fa-solid fa-pen-nib text-2xl text-blue-600 mr-4 group-hover:scale-110 transition-transform"></i>
                <div>
                    <h2 class="font-bold text-gray-900">Post Builder</h2>
                    <p class="text-xs text-gray-500">Create blog posts in _posts/</p>
                </div>
            </a>
            <a href="/news-builder.html" class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow transition bg-gray-50 group">
                <i class="fa-solid fa-newspaper text-2xl text-emerald-600 mr-4 group-hover:scale-110 transition-transform"></i>
                <div>
                    <h2 class="font-bold text-gray-900">News Builder</h2>
                    <p class="text-xs text-gray-500">Create announcements in _news/</p>
                </div>
            </a>
            <a href="/project-builder.html" class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow transition bg-gray-50 group">
                <i class="fa-solid fa-flask text-2xl text-purple-600 mr-4 group-hover:scale-110 transition-transform"></i>
                <div>
                    <h2 class="font-bold text-gray-900">Project Builder</h2>
                    <p class="text-xs text-gray-500">Add portfolio items in _projects/</p>
                </div>
            </a>
            <a href="/book-builder.html" class="flex items-center p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow transition bg-gray-50 group">
                <i class="fa-solid fa-book text-2xl text-amber-600 mr-4 group-hover:scale-110 transition-transform"></i>
                <div>
                    <h2 class="font-bold text-gray-900">Book Builder</h2>
                    <p class="text-xs text-gray-500">Add book reviews in _books/</p>
                </div>
            </a>
        </div>

        <div class="mt-8 pt-4 border-t border-gray-200 flex justify-between items-center text-xs text-gray-500">
            <span>Server running at <code>http://127.0.0.1:{self.server.server_port}</code></span>
            <span>Zero dependencies &bull; Linux Native</span>
        </div>
    </div>
</body>
</html>"""
            self.wfile.write(dashboard_html.encode("utf-8"))
            return

        # Default static file handling
        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length)

        try:
            payload = json.loads(post_body.decode("utf-8"))
        except Exception as e:
            self._send_json({"ok": False, "error": f"Invalid JSON payload: {e}"}, status=400)
            return

        # API: Save Markdown File
        if self.path == "/api/save":
            folder = payload.get("folder", "").strip("/\\")
            filename = payload.get("filename", "").strip("/\\")
            content = payload.get("content", "")

            if folder not in ALLOWED_SAVE_FOLDERS:
                self._send_json(
                    {"ok": False, "error": f"Folder '{folder}' is not allowed for saving."},
                    status=403,
                )
                return

            if not filename or ".." in filename or "/" in filename or "\\" in filename:
                self._send_json({"ok": False, "error": "Invalid or unsafe filename."}, status=400)
                return

            target_dir = REPO_ROOT / folder
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / filename

            try:
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"[SAVE] Successfully saved {folder}/{filename} ({len(content)} bytes)")
                self._send_json(
                    {
                        "ok": True,
                        "path": f"{folder}/{filename}",
                        "message": f"Successfully saved to {folder}/{filename}",
                    }
                )
            except Exception as e:
                print(f"[ERROR] Failed to write {target_file}: {e}")
                self._send_json({"ok": False, "error": f"Failed to write file: {e}"}, status=500)
            return

        # API: Upload Image
        if self.path == "/api/upload":
            folder = payload.get("folder", "assets/img").strip("/\\")
            filename = payload.get("filename", "").strip("/\\")
            data = payload.get("data", "")

            if folder not in ALLOWED_UPLOAD_FOLDERS:
                self._send_json(
                    {"ok": False, "error": f"Folder '{folder}' is not allowed for image uploads."},
                    status=403,
                )
                return

            if not filename or ".." in filename or "/" in filename or "\\" in filename:
                self._send_json({"ok": False, "error": "Invalid or unsafe image filename."}, status=400)
                return

            if not data:
                self._send_json({"ok": False, "error": "No image data provided."}, status=400)
                return

            # Extract base64 if data URI
            if "," in data:
                data = data.split(",", 1)[1]

            try:
                binary_data = base64.b64decode(data)
            except Exception as e:
                self._send_json({"ok": False, "error": f"Invalid base64 data: {e}"}, status=400)
                return

            target_dir = REPO_ROOT / folder
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / filename

            try:
                with open(target_file, "wb") as f:
                    f.write(binary_data)
                print(f"[UPLOAD] Successfully saved {folder}/{filename} ({len(binary_data)} bytes)")
                self._send_json(
                    {
                        "ok": True,
                        "path": f"{folder}/{filename}",
                        "message": f"Successfully saved {folder}/{filename}",
                    }
                )
            except Exception as e:
                print(f"[ERROR] Failed to write image {target_file}: {e}")
                self._send_json({"ok": False, "error": f"Failed to write image: {e}"}, status=500)
            return

        self._send_json({"ok": False, "error": "Unknown API endpoint."}, status=404)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format, *args):
        # Filter out noisy standard static file logs, but keep API calls visible
        if len(args) >= 1 and (args[0].startswith("POST /api") or args[0].startswith("GET /api")):
            sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")
        elif len(args) >= 2 and args[1] in ("400", "403", "404", "500"):
            sys.stdout.write(f"[{self.log_date_time_string()}] {format % args}\n")


def find_free_port(start_port=8000, max_attempts=20):
    import socket

    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


def main():
    parser = argparse.ArgumentParser(description="Jekyll HTML Builders Linux Local Server")
    parser.add_argument("port", nargs="?", type=int, default=8000, help="Port to serve on (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
    args = parser.parse_args()

    port = find_free_port(args.port)
    server_address = ("127.0.0.1", port)

    httpd = ThreadingHTTPServer(server_address, BuilderRequestHandler)
    url = f"http://127.0.0.1:{port}"

    print("=" * 60)
    print("  Jekyll Local HTML Builders Server (Linux Filesystem)")
    print("=" * 60)
    print(f"  Root:   {REPO_ROOT}")
    print(f"  Server: {url}")
    print("\n  Available Builders:")
    print(f"  - Post Builder:    {url}/post-builder.html")
    print(f"  - News Builder:    {url}/news-builder.html")
    print(f"  - Project Builder: {url}/project-builder.html")
    print(f"  - Book Builder:    {url}/book-builder.html")
    print("\n  Press Ctrl+C to stop the server.")
    print("=" * 60)

    if not args.no_browser:
        try:
            webbrowser.open(f"{url}/post-builder.html")
        except Exception:
            pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping builder server. Goodbye!")
        httpd.server_close()


if __name__ == "__main__":
    main()
