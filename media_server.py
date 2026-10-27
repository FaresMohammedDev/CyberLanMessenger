# -*- coding: utf-8 -*-
"""
CYBER-LAN MEDIA & FILE TRANSFER SERVER (HTTP Micro-Service)
Runs locally on Port 54322 to:
1. Transfer files, photos, videos, and office documents (.docx, .pdf, .pptx)
2. Host the Cyber Watch-Party Cinema with synchronized video and side-by-side chat
"""

import os
import sys
import json
import time
import urllib.parse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket

MEDIA_PORT = 54322
MEDIA_DIR = os.path.join(os.path.dirname(__file__), "shared_files")
DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "downloads")

os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Shared State for Watch Party
WATCH_PARTY_STATE = {
    "active_movie": None,       # filename
    "movie_title": "Awaiting Cinema Stream...",
    "is_playing": False,
    "current_time": 0.0,
    "last_sync_timestamp": time.time(),
    "host_nick": "Host",
    "chat_messages": []
}


class CyberMediaHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence default terminal request spam
        return

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Watch Party HTML5 Theater
        if path == "/" or path == "/watch":
            self._serve_watch_theater()
            return

        # 2. Watch Party State API
        elif path == "/api/party_state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(WATCH_PARTY_STATE, ensure_ascii=False).encode("utf-8"))
            return

        # 3. Stream / Download File
        elif path.startswith("/files/"):
            filename = urllib.parse.unquote(path[7:])
            filepath = os.path.join(MEDIA_DIR, filename)
            if os.path.exists(filepath) and os.path.isfile(filepath):
                self._serve_file_stream(filepath)
            else:
                self.send_error(404, "File Not Found")
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Update Watch Party Sync (Play / Pause / Seek)
        if path == "/api/party_sync":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            if "is_playing" in data:
                WATCH_PARTY_STATE["is_playing"] = bool(data["is_playing"])
            if "current_time" in data:
                WATCH_PARTY_STATE["current_time"] = float(data["current_time"])
            WATCH_PARTY_STATE["last_sync_timestamp"] = time.time()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return

        # 2. Post Watch Party Chat Message
        elif path == "/api/party_chat":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            msg_data = json.loads(body)
            msg_data["time"] = time.strftime("%H:%M:%S")
            WATCH_PARTY_STATE["chat_messages"].append(msg_data)
            if len(WATCH_PARTY_STATE["chat_messages"]) > 80:
                WATCH_PARTY_STATE["chat_messages"].pop(0)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return

        self.send_error(404, "Not Found")

    def _serve_file_stream(self, filepath):
        """Serves video or documents with HTTP Range support for video seeking."""
        file_size = os.path.getsize(filepath)
        mime_type = "application/octet-stream"

        ext = os.path.splitext(filepath)[1].lower()
        if ext in [".mp4", ".m4v"]:
            mime_type = "video/mp4"
        elif ext in [".webm"]:
            mime_type = "video/webm"
        elif ext in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif ext == ".png":
            mime_type = "image/png"
        elif ext == ".gif":
            mime_type = "image/gif"
        elif ext == ".pdf":
            mime_type = "application/pdf"
        elif ext == ".docx":
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ext == ".pptx":
            mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(file_size))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                self.wfile.write(chunk)

    def _serve_watch_theater(self):
        """Renders the Cyber Cinema Web Player with live synchronized controls & side chat."""
        movie_url = f"/files/{urllib.parse.quote(WATCH_PARTY_STATE['active_movie'])}" if WATCH_PARTY_STATE['active_movie'] else ""

        html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>🎬 CYBER CINEMA // LAN WATCH PARTY</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background:#070b12; color:#e2e8f0; font-family:'Segoe UI', Consolas, sans-serif; display:flex; height:100vh; overflow:hidden; }}
        
        /* Video Left Area */
        .theater-main {{ flex:1; display:flex; flex-direction:column; background:#000; border-left:2px solid #1f2f4d; }}
        .theater-header {{ background:#0d1424; padding:12px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #1f2f4d; }}
        .movie-title {{ font-size:16px; font-weight:bold; color:#00f0ff; }}
        .badge-live {{ background:#ff0055; color:#fff; font-size:11px; padding:3px 8px; border-radius:4px; font-weight:bold; }}
        
        .video-wrapper {{ flex:1; display:flex; align-items:center; justify-content:center; background:#05070a; position:relative; }}
        video {{ width:100%; height:100%; max-height:85vh; }}
        
        /* Chat Right Area */
        .chat-sidebar {{ width:380px; display:flex; flex-direction:column; background:#0a0f18; }}
        .chat-header {{ background:#0f172a; padding:15px; border-bottom:1px solid #1e293b; color:#00ff66; font-weight:bold; display:flex; justify-content:space-between; }}
        .chat-stream {{ flex:1; overflow-y:auto; padding:15px; display:flex; flex-direction:column; gap:8px; }}
        .chat-msg {{ background:#111b2b; padding:8px 12px; border-radius:6px; font-size:13px; line-height:1.4; border-right:3px solid #00ff66; }}
        .chat-msg.me {{ border-right-color:#00f0ff; background:#102238; }}
        .chat-author {{ font-size:11px; font-weight:bold; color:#00f0ff; margin-bottom:2px; }}
        .chat-time {{ font-size:10px; color:#64748b; margin-right:8px; }}
        
        .chat-input-bar {{ padding:12px; background:#0d1424; border-top:1px solid #1e293b; display:flex; gap:8px; }}
        .chat-input {{ flex:1; background:#04070d; border:1px solid #1f2f4d; color:#fff; padding:8px 12px; border-radius:4px; outline:none; }}
        .chat-btn {{ background:#00ff66; color:#000; font-weight:bold; border:none; padding:8px 16px; border-radius:4px; cursor:pointer; }}
        .chat-btn:hover {{ background:#00cc52; }}
    </style>
</head>
<body>
    <div class="theater-main">
        <div class="theater-header">
            <span class="movie-title">🎬 {WATCH_PARTY_STATE['movie_title']}</span>
            <span class="badge-live">● LAN SYNC ACTIVE</span>
        </div>
        <div class="video-wrapper">
            {'<video id="vplayer" controls src="' + movie_url + '"></video>' if movie_url else '<div style="color:#64748b; font-size:18px;">⚠️ في انتظار اختيار المضيف لفيلم لبدء البث...</div>'}
        </div>
    </div>
    
    <div class="chat-sidebar">
        <div class="chat-header">
            <span>💬 شات صالة السينما</span>
            <span style="font-size:11px; color:#ffd000;">Host: {WATCH_PARTY_STATE['host_nick']}</span>
        </div>
        <div class="chat-stream" id="chatStream"></div>
        <div class="chat-input-bar">
            <input type="text" id="msgInput" class="chat-input" placeholder="اكتب تعليقك على الفيلم...">
            <button class="chat-btn" onclick="sendPartyMsg()">إرسال</button>
        </div>
    </div>

    <script>
        const vplayer = document.getElementById("vplayer");
        const chatStream = document.getElementById("chatStream");
        const msgInput = document.getElementById("msgInput");
        let isSyncing = false;
        let lastMsgCount = 0;

        // Poll Party State every 1.5s
        async function fetchState() {{
            try {{
                const res = await fetch("/api/party_state");
                const state = await res.json();
                
                // Update Video Playback Sync
                if (vplayer && !isSyncing) {{
                    const diff = Math.abs(vplayer.currentTime - state.current_time);
                    if (diff > 2.5) {{
                        vplayer.currentTime = state.current_time;
                    }}
                    if (state.is_playing && vplayer.paused) {{
                        vplayer.play().catch(() => {{}});
                    }} else if (!state.is_playing && !vplayer.paused) {{
                        vplayer.pause();
                    }}
                }}

                // Update Chat
                if (state.chat_messages && state.chat_messages.length !== lastMsgCount) {{
                    lastMsgCount = state.chat_messages.length;
                    chatStream.innerHTML = state.chat_messages.map(m => `
                        <div class="chat-msg">
                            <div class="chat-author">${{m.nick}} <span class="chat-time">${{m.time}}</span></div>
                            <div>${{m.text}}</div>
                        </div>
                    `).join("");
                    chatStream.scrollTop = chatStream.scrollHeight;
                }}
            }} catch(e) {{}}
        }}

        setInterval(fetchState, 1500);

        if (vplayer) {{
            vplayer.onplay = () => syncState(true, vplayer.currentTime);
            vplayer.onpause = () => syncState(false, vplayer.currentTime);
            vplayer.onseeked = () => syncState(!vplayer.paused, vplayer.currentTime);
        }}

        async function syncState(isPlaying, currentTime) {{
            isSyncing = true;
            try {{
                await fetch("/api/party_sync", {{
                    method: "POST",
                    headers: {{"Content-Type": "application/json"}},
                    body: JSON.stringify({{ is_playing: isPlaying, current_time: currentTime }})
                }});
            }} catch(e) {{}}
            setTimeout(() => {{ isSyncing = false; }}, 800);
        }}

        async function sendPartyMsg() {{
            const val = msgInput.value.trim();
            if (!val) return;
            msgInput.value = "";
            try {{
                await fetch("/api/party_chat", {{
                    method: "POST",
                    headers: {{"Content-Type": "application/json"}},
                    body: JSON.stringify({{ nick: "Viewer", text: val }})
                }});
                fetchState();
            }} catch(e) {{}}
        }}

        msgInput.addEventListener("keypress", (e) => {{
            if (e.key === "Enter") sendPartyMsg();
        }});
    </script>
</body>
</html>"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))


class MediaServer:
    def __init__(self, port=MEDIA_PORT):
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        try:
            self.server = HTTPServer(("0.0.0.0", self.port), CyberMediaHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            return True, self.port
        except Exception as e:
            # Fallback port
            try:
                self.port += 1
                self.server = HTTPServer(("0.0.0.0", self.port), CyberMediaHandler)
                self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
                self.thread.start()
                return True, self.port
            except Exception as e2:
                return False, str(e2)

    def set_active_movie(self, filepath, movie_title="Movie"):
        filename = os.path.basename(filepath)
        dest = os.path.join(MEDIA_DIR, filename)
        if filepath != dest and not os.path.exists(dest):
            import shutil
            shutil.copy2(filepath, dest)

        WATCH_PARTY_STATE["active_movie"] = filename
        WATCH_PARTY_STATE["movie_title"] = movie_title
        WATCH_PARTY_STATE["is_playing"] = False
        WATCH_PARTY_STATE["current_time"] = 0.0
        WATCH_PARTY_STATE["last_sync_timestamp"] = time.time()
        return filename


# Global server instance
media_server_instance = MediaServer()

if __name__ == "__main__":
    ok, p = media_server_instance.start()
    print(f"Media & Watch Party server running at http://localhost:{p}")
    time.sleep(2)
