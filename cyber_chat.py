# -*- coding: utf-8 -*-
"""
CYBER-CHAT // SECRET P2P LAN NODE (ADMIN, STEALTH & MULTI-THREADED PRIVATE CHATS)
Serverless, encrypted peer-to-peer real-time chat with:
- Dedicated Isolated Private Chat Windows (no mixing with public stream)
- Public Quoted Reply System (seen by everyone)
- Admin privileges & Boss-Key Stealth Mode
- Access clearance gate
"""

import os
import sys
import time
import json
import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import winsound
    HAS_SOUND = True
except Exception:
    HAS_SOUND = False

# ----------------- CONFIGURATION -----------------
UDP_PORT = 54321
BUFFER_SIZE = 4096
XOR_KEY = 0x5A               # Lightweight cyber obfuscation byte
ADMIN_IP = "192.168.20.54"   # Authorized Root Admin IP
REQUIRED_PASSWORD = "Sd2027" # Access Clearance Key

# ----------------- HACKER PALETTE -----------------
COLOR_BG = "#06090e"         # Void Black
COLOR_PANEL = "#0b121e"      # Deep Cyber Navy
COLOR_PANEL_ALT = "#101b2d"  # Highlighted frames
COLOR_ENTRY_BG = "#03060a"   # Deep Input Box
COLOR_GREEN = "#00ff66"      # Neon Matrix Green
COLOR_CYAN = "#00f0ff"       # Cyberpunk Cyan
COLOR_YELLOW = "#ffd000"     # Alert Yellow / Admin Gold
COLOR_RED = "#ff2a55"        # Hazard Red
COLOR_PURPLE = "#c084fc"     # Whisper Purple
COLOR_TEXT = "#e2e8f0"       # High-contrast text
COLOR_DIM = "#64748b"        # Dim text
COLOR_BORDER = "#1b2a47"     # Border tone

FONT_TITLE = ("Consolas", 11, "bold")
FONT_MAIN = ("Consolas", 10)
FONT_BOLD = ("Consolas", 10, "bold")
FONT_MSG = ("Segoe UI", 10)
FONT_MSG_BOLD = ("Segoe UI", 10, "bold")
FONT_TIME = ("Consolas", 9)


def get_local_ip_and_hostname():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "NODE-" + local_ip.split(".")[-1]

    return local_ip, hostname


def xor_cipher(data_bytes):
    """Simple XOR stream cipher for lightweight network obfuscation."""
    return bytes([b ^ XOR_KEY for b in data_bytes])


# ----------------- LOGIN / AUTHENTICATION GATE -----------------
class AuthGateModal:
    """Hacker-styled password authentication modal."""
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("SECURITY CLEARANCE // GATEWAY")
        self.top.geometry("450x300")
        self.top.resizable(False, False)
        self.top.configure(bg=COLOR_BG)
        self.top.attributes("-topmost", True)
        self.authenticated = False
        self.attempts_left = 3

        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() - 450) // 2
        y = (self.top.winfo_screenheight() - 300) // 2
        self.top.geometry(f"+{x}+{y}")

        self._build_ui()
        self.top.protocol("WM_DELETE_WINDOW", self._on_close)
        self.entry_pass.focus_set()

    def _build_ui(self):
        frame = tk.Frame(self.top, bg=COLOR_PANEL, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        lbl_header = tk.Label(
            frame,
            text="[ # ] ACCESS CONTROL // CLEARANCE GATE",
            fg=COLOR_GREEN, bg=COLOR_PANEL, font=FONT_TITLE
        )
        lbl_header.pack(pady=(16, 4))

        lbl_desc = tk.Label(
            frame,
            text="ENTER NETWORK ACCESS PASSPHRASE TO PROCEED:",
            fg=COLOR_CYAN, bg=COLOR_PANEL, font=("Consolas", 9)
        )
        lbl_desc.pack(pady=(0, 15))

        self.entry_pass = tk.Entry(
            frame, bg=COLOR_ENTRY_BG, fg=COLOR_GREEN, insertbackground=COLOR_GREEN,
            font=("Consolas", 14, "bold"), show="*", justify="center", bd=1, relief="solid", width=22
        )
        self.entry_pass.pack(pady=5, ipady=4)
        self.entry_pass.bind("<Return>", lambda e: self.check_password())

        self.lbl_status = tk.Label(
            frame, text="STATUS: STANDBY // AUTHORIZATION REQUIRED",
            fg=COLOR_DIM, bg=COLOR_PANEL, font=("Consolas", 8)
        )
        self.lbl_status.pack(pady=(10, 15))

        btn = tk.Button(
            frame, text="🔓 AUTHENTICATE [ENTER]",
            bg="#02381b", fg=COLOR_GREEN, activebackground="#056b34", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", padx=20, pady=5, cursor="hand2",
            command=self.check_password
        )
        btn.pack()

    def check_password(self):
        entered = self.entry_pass.get()
        if entered == REQUIRED_PASSWORD:
            self.authenticated = True
            if HAS_SOUND:
                try:
                    winsound.Beep(1200, 100)
                except Exception:
                    pass
            self.top.destroy()
        else:
            self.attempts_left -= 1
            if HAS_SOUND:
                try:
                    winsound.Beep(400, 200)
                except Exception:
                    pass
            if self.attempts_left > 0:
                self.lbl_status.config(
                    text=f"[!] ACCESS DENIED. {self.attempts_left} ATTEMPTS REMAINING.",
                    fg=COLOR_RED
                )
                self.entry_pass.delete(0, "end")
            else:
                messagebox.showerror("LOCKOUT", "Clearance failed. Terminating process.")
                self.top.destroy()

    def _on_close(self):
        self.top.destroy()


# ----------------- DEDICATED PRIVATE CHAT WINDOW -----------------
class PrivateChatWindow:
    """Dedicated isolated window for direct peer-to-peer private messages."""
    def __init__(self, main_app, peer_ip, peer_nick):
        self.main_app = main_app
        self.peer_ip = peer_ip
        self.peer_nick = peer_nick

        self.top = tk.Toplevel(self.main_app.root)
        self.top.title(f"PRIVATE ENCRYPTED CHANNEL // @{peer_nick} [{peer_ip}]")
        self.top.geometry("640x500")
        self.top.minsize(520, 400)
        self.top.configure(bg=COLOR_BG)

        self._build_ui()
        self.top.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.top, bg="#1a102f", bd=1, relief="solid", highlightbackground=COLOR_PURPLE)
        hdr.pack(fill="x", padx=8, pady=(8, 4))

        tk.Label(
            hdr, text=f"🔒 SECURE DIRECT CHANNEL // @{self.peer_nick}",
            fg=COLOR_PURPLE, bg="#1a102f", font=FONT_TITLE
        ).pack(side="left", padx=10, pady=6)

        tk.Label(
            hdr, text=f"IP: {self.peer_ip} | E2E OBFUSCATED",
            fg=COLOR_DIM, bg="#1a102f", font=("Consolas", 8)
        ).pack(side="right", padx=10)

        # Chat Text Box
        txt_frame = tk.Frame(self.top, bg=COLOR_ENTRY_BG, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        txt_frame.pack(fill="both", expand=True, padx=8, pady=4)

        self.txt_history = tk.Text(
            txt_frame, bg=COLOR_ENTRY_BG, fg=COLOR_TEXT, insertbackground=COLOR_PURPLE,
            font=FONT_MSG, bd=0, wrap="word", padx=8, pady=8
        )
        scroll = ttk.Scrollbar(txt_frame, orient="vertical", command=self.txt_history.yview)
        self.txt_history.configure(yscrollcommand=scroll.set)

        self.txt_history.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.txt_history.tag_configure("TIME", foreground=COLOR_DIM, font=FONT_TIME)
        self.txt_history.tag_configure("ME_TAG", foreground=COLOR_CYAN, font=FONT_BOLD)
        self.txt_history.tag_configure("ME_MSG", foreground="#ffffff", font=FONT_MSG)
        self.txt_history.tag_configure("PEER_TAG", foreground=COLOR_PURPLE, font=FONT_BOLD)
        self.txt_history.tag_configure("PEER_MSG", foreground="#f5f3ff", font=FONT_MSG)
        self.txt_history.tag_configure("SYS", foreground=COLOR_YELLOW, font=FONT_TIME)

        # Input Box
        in_frame = tk.Frame(self.top, bg=COLOR_PANEL, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        in_frame.pack(fill="x", padx=8, pady=(0, 8))

        self.entry_msg = tk.Entry(
            in_frame, bg=COLOR_ENTRY_BG, fg="#ffffff", insertbackground=COLOR_PURPLE,
            font=("Segoe UI", 11), bd=1, relief="solid"
        )
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=8, pady=8, ipady=4)
        self.entry_msg.bind("<Return>", lambda e: self.send_private_message())

        btn_send = tk.Button(
            in_frame, text="🔒 SEND WHISPER",
            bg="#3b0764", fg="#e9d5ff", activebackground="#581c87", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", padx=12, cursor="hand2",
            command=self.send_private_message
        )
        btn_send.pack(side="right", padx=(0, 8), pady=8)

        self.append_system(f"Private encrypted link established with @{self.peer_nick} [{self.peer_ip}].")

    def append_system(self, text):
        ts = time.strftime("[%H:%M:%S] ")
        self.txt_history.insert("end", ts, "TIME")
        self.txt_history.insert("end", f"[SYSTEM] {text}\n", "SYS")
        self.txt_history.see("end")

    def append_incoming(self, text, ts):
        self.txt_history.insert("end", f"[{ts}] ", "TIME")
        self.txt_history.insert("end", f"@{self.peer_nick}: ", "PEER_TAG")
        self.txt_history.insert("end", f"{text}\n", "PEER_MSG")
        self.txt_history.see("end")

    def send_private_message(self):
        text = self.entry_msg.get().strip()
        if not text:
            return

        ts = time.strftime("%H:%M:%S")
        packet = {
            "type": "PRIVATE_MSG",
            "nick": self.main_app.my_nick,
            "ip": self.main_app.local_ip,
            "target": self.peer_ip,
            "text": text,
            "time": ts
        }
        self.main_app.send_packet(packet, self.peer_ip)

        self.txt_history.insert("end", f"[{ts}] ", "TIME")
        self.txt_history.insert("end", f"<{self.main_app.my_nick}>: ", "ME_TAG")
        self.txt_history.insert("end", f"{text}\n", "ME_MSG")
        self.txt_history.see("end")
        self.entry_msg.delete(0, "end")

    def on_close(self):
        if self.peer_ip in self.main_app.private_windows:
            del self.main_app.private_windows[self.peer_ip]
        self.top.destroy()


# ----------------- INNOCENT DISGUISE WINDOW (STEALTH MODE) -----------------
class StealthDisguiseWindow:
    """Innocent educational window for Boss-Key disguise mode."""
    def __init__(self, on_restore_callback):
        self.on_restore_callback = on_restore_callback
        self.top = tk.Toplevel()
        self.top.title("Physics Unit 1 - Scientific Reference & Model Revision Notes")
        self.top.geometry("900x600")
        self.top.configure(bg="#f8fafc")

        tb = tk.Frame(self.top, bg="#e2e8f0", bd=1, relief="solid")
        tb.pack(fill="x", side="top")

        tk.Label(tb, text="📘 Ministry of Education - Science & Physics Digital Library", bg="#e2e8f0", fg="#1e293b", font=("Segoe UI", 9, "bold")).pack(side="left", padx=10, pady=6)
        
        btn_stealth = tk.Button(
            tb, text="🔍 Refresh Notes (F12)", bg="#cbd5e1", fg="#475569",
            font=("Segoe UI", 8), bd=0, relief="flat", cursor="hand2",
            command=self.restore_hacker_chat
        )
        btn_stealth.pack(side="right", padx=10, pady=4)

        text_area = tk.Text(self.top, bg="#ffffff", fg="#0f172a", font=("Segoe UI", 11), wrap="word", padx=25, pady=20, bd=0)
        text_area.pack(fill="both", expand=True)

        sample_notes = (
            "UNIT 1: MOTION IN ONE DIRECTION & PHYSICAL QUANTITIES\n"
            "====================================================\n\n"
            "1. Definitions and Fundamental Concepts:\n"
            "   - Speed (v): The distance covered by an object per unit time (v = d / t).\n"
            "   - Uniform Velocity: When an object covers equal distances in equal periods of time.\n"
            "   - Non-uniform Velocity: When an object covers unequal distances in equal periods of time.\n"
            "   - Acceleration (a): The change in velocity per unit time (a = Δv / Δt).\n\n"
            "2. Formulas & Mathematical Relations:\n"
            "   - Average Speed (v_avg) = Total Distance / Total Time\n"
            "   - Relative Speed: The speed of a moving object relative to a stationary or moving observer.\n\n"
            "3. Solved Revision Examples:\n"
            "   Example 1: A car moves at a uniform speed of 72 km/h. Convert to m/s.\n"
            "   Solution: 72 * (5 / 18) = 20 m/s.\n\n"
            "   Example 2: A train moves with an acceleration of 2 m/s^2 from rest. Find velocity after 5 seconds.\n"
            "   Solution: v_f = v_i + a*t = 0 + (2 * 5) = 10 m/s.\n\n"
            "----------------------------------------------------\n"
            "Tip: Press F12 or click 'Refresh Notes' to toggle view."
        )
        text_area.insert("1.0", sample_notes)
        text_area.config(state="disabled")

        self.top.bind("<F12>", lambda e: self.restore_hacker_chat())
        self.top.protocol("WM_DELETE_WINDOW", self.restore_hacker_chat)

    def restore_hacker_chat(self):
        self.top.destroy()
        self.on_restore_callback()


# ----------------- MAIN CYBER CHAT APPLICATION -----------------
class CyberChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CYBER-CHAT // SECRET P2P LAN NODE v2.2")
        self.root.geometry("1040x730")
        self.root.minsize(920, 620)
        self.root.configure(bg=COLOR_BG)

        self.local_ip, self.default_host = get_local_ip_and_hostname()
        self.my_nick = self.default_host

        # Admin verification (matches local IP 192.168.20.54 or localhost)
        self.is_admin = (self.local_ip == ADMIN_IP or self.local_ip == "127.0.0.1")

        # Room State
        self.peers = {}               # { ip: {"nick": ..., "last_seen": timestamp} }
        self.private_windows = {}     # { ip: PrivateChatWindow }
        self.replying_to = None       # {"nick": ..., "snippet": ...} or None
        self.is_room_muted = False    # Admin mute toggle
        self.sound_enabled = tk.BooleanVar(value=True)
        self.encrypt_enabled = tk.BooleanVar(value=True)
        self.is_running = True
        self.stealth_win = None

        # Hide main window until authenticated
        self.root.withdraw()
        auth = AuthGateModal(self.root)
        self.root.wait_window(auth.top)

        if not auth.authenticated:
            self.root.destroy()
            sys.exit(0)

        # Show main chat window after login
        self.root.deiconify()

        self._setup_socket()
        self._build_ui()

        # Keyboard shortcuts
        self.root.bind("<F12>", lambda e: self.activate_stealth_mode())
        self.root.bind("<Escape>", lambda e: self.activate_stealth_mode())

        # Start network listener threads
        threading.Thread(target=self._udp_listen_worker, daemon=True).start()
        threading.Thread(target=self._heartbeat_worker, daemon=True).start()
        threading.Thread(target=self._peer_cleanup_worker, daemon=True).start()

        self.add_system_message(f"SYSTEM READY. BOUND TO INTERFACE: {self.local_ip}:{UDP_PORT}")
        if self.is_admin:
            self.add_system_message("👑 ROOT ADMIN PRIVILEGES CONFIRMED FOR THIS NODE.", "YELLOW")
        self.add_system_message("BROADCASTING NODE PRESENCE TO LOCAL NETWORK...")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_socket(self):
        """Creates UDP socket with broadcast permissions."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception:
            pass
        self.sock.bind(("0.0.0.0", UDP_PORT))

    def _build_ui(self):
        # ----------------- TOP HEADER -----------------
        header = tk.Frame(self.root, bg=COLOR_PANEL, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        header.pack(fill="x", padx=10, pady=(10, 4))

        banner_frame = tk.Frame(header, bg=COLOR_PANEL)
        banner_frame.pack(side="left", padx=15, pady=8)

        lbl_logo = tk.Label(
            banner_frame,
            text="[ # ] CYBER-CHAT // P2P ZERO-CONFIG LAN MESH",
            fg=COLOR_GREEN, bg=COLOR_PANEL, font=FONT_TITLE
        )
        lbl_logo.pack(anchor="w")

        role_badge = "👑 ROOT ADMIN" if self.is_admin else "🟢 OPERATOR"
        role_color = COLOR_YELLOW if self.is_admin else COLOR_CYAN

        lbl_sub = tk.Label(
            banner_frame,
            text=f"NODE: {self.local_ip}  |  ROLE: {role_badge}  |  PORT: {UDP_PORT}",
            fg=role_color, bg=COLOR_PANEL, font=("Consolas", 9, "bold")
        )
        lbl_sub.pack(anchor="w")

        # Top Options & Nickname
        opts_frame = tk.Frame(header, bg=COLOR_PANEL)
        opts_frame.pack(side="right", padx=15, pady=8)

        btn_stealth = tk.Button(
            opts_frame, text="🕶️ STEALTH (F12)",
            bg="#182234", fg=COLOR_CYAN, activebackground="#2a3b5c", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", padx=8, pady=2, cursor="hand2",
            command=self.activate_stealth_mode
        )
        btn_stealth.pack(side="right", padx=(8, 0))

        chk_enc = tk.Checkbutton(opts_frame, text="🔒 CIPHER", variable=self.encrypt_enabled,
                                 fg=COLOR_GREEN, bg=COLOR_PANEL, selectcolor=COLOR_ENTRY_BG,
                                 activebackground=COLOR_PANEL, activeforeground=COLOR_GREEN,
                                 font=FONT_MAIN)
        chk_enc.pack(side="right", padx=6)

        chk_sound = tk.Checkbutton(opts_frame, text="🔊 SFX", variable=self.sound_enabled,
                                   fg=COLOR_YELLOW, bg=COLOR_PANEL, selectcolor=COLOR_ENTRY_BG,
                                   activebackground=COLOR_PANEL, activeforeground=COLOR_YELLOW,
                                   font=FONT_MAIN)
        chk_sound.pack(side="right", padx=6)

        tk.Label(opts_frame, text="HANDLE:", fg=COLOR_TEXT, bg=COLOR_PANEL, font=FONT_BOLD).pack(side="right", padx=(6, 2))
        self.entry_nick = tk.Entry(opts_frame, bg=COLOR_ENTRY_BG, fg=COLOR_GREEN, insertbackground=COLOR_GREEN,
                                   font=FONT_BOLD, width=14, bd=1, relief="solid")
        self.entry_nick.insert(0, self.my_nick)
        self.entry_nick.pack(side="right", padx=4)
        self.entry_nick.bind("<FocusOut>", self.update_nickname)
        self.entry_nick.bind("<Return>", self.update_nickname)

        # ----------------- ADMIN COMMAND TOOLBAR (ONLY FOR ADMIN) -----------------
        if self.is_admin:
            admin_bar = tk.Frame(self.root, bg="#1a1402", bd=1, relief="solid", highlightbackground=COLOR_YELLOW)
            admin_bar.pack(fill="x", padx=10, pady=(0, 4))

            tk.Label(
                admin_bar, text="[ 👑 ROOT ADMIN TOOLBAR ]:",
                fg=COLOR_YELLOW, bg="#1a1402", font=FONT_BOLD
            ).pack(side="left", padx=10, pady=4)

            btn_clear = tk.Button(
                admin_bar, text="🧹 WIPE CHAT (ALL PEERS)",
                bg="#451a03", fg=COLOR_YELLOW, activebackground="#78350f", activeforeground="#ffffff",
                font=FONT_BOLD, bd=1, relief="solid", padx=10, pady=2, cursor="hand2",
                command=self.admin_clear_all_chats
            )
            btn_clear.pack(side="left", padx=6, pady=4)

            self.btn_mute = tk.Button(
                admin_bar, text="🔇 MUTE ROOM",
                bg="#3b0712", fg="#ff4d6d", activebackground="#5c0d1e", activeforeground="#ffffff",
                font=FONT_BOLD, bd=1, relief="solid", padx=10, pady=2, cursor="hand2",
                command=self.admin_toggle_mute
            )
            self.btn_mute.pack(side="left", padx=6, pady=4)

            btn_alert = tk.Button(
                admin_bar, text="🚨 BROADCAST FLASH ALERT",
                bg="#2e1065", fg="#d8b4fe", activebackground="#4c1d95", activeforeground="#ffffff",
                font=FONT_BOLD, bd=1, relief="solid", padx=10, pady=2, cursor="hand2",
                command=self.admin_flash_alert
            )
            btn_alert.pack(side="left", padx=6, pady=4)

        # ----------------- MAIN SPLIT BODY -----------------
        main_body = tk.PanedWindow(self.root, orient="horizontal", bg=COLOR_BG, bd=0, sashwidth=4)
        main_body.pack(fill="both", expand=True, padx=10, pady=4)

        # Left: Public Comms Stream
        chat_frame = tk.LabelFrame(main_body, text=" [ PUBLIC ROOM // ALL PEERS ] ",
                                   bg=COLOR_PANEL, fg=COLOR_GREEN, font=FONT_TITLE, bd=1, relief="solid")
        main_body.add(chat_frame, minsize=560)

        msg_container = tk.Frame(chat_frame, bg=COLOR_ENTRY_BG)
        msg_container.pack(fill="both", expand=True, padx=8, pady=8)

        self.txt_messages = tk.Text(
            msg_container, bg=COLOR_ENTRY_BG, fg=COLOR_TEXT, insertbackground=COLOR_GREEN,
            font=FONT_MSG, bd=0, wrap="word", padx=8, pady=8
        )
        msg_scroll = ttk.Scrollbar(msg_container, orient="vertical", command=self.txt_messages.yview)
        self.txt_messages.configure(yscrollcommand=msg_scroll.set)

        self.txt_messages.pack(side="left", fill="both", expand=True)
        msg_scroll.pack(side="right", fill="y")

        # Formatting tags
        self.txt_messages.tag_configure("TIME", foreground=COLOR_DIM, font=FONT_TIME)
        self.txt_messages.tag_configure("SYS", foreground=COLOR_YELLOW, font=FONT_TIME)
        self.txt_messages.tag_configure("ALERT", foreground=COLOR_RED, font=FONT_BOLD)
        self.txt_messages.tag_configure("ADMIN_TAG", foreground=COLOR_YELLOW, font=FONT_BOLD)
        self.txt_messages.tag_configure("ADMIN_MSG", foreground="#fef08a", font=FONT_MSG_BOLD)
        self.txt_messages.tag_configure("ME_TAG", foreground=COLOR_CYAN, font=FONT_BOLD)
        self.txt_messages.tag_configure("ME_MSG", foreground="#ffffff", font=FONT_MSG)
        self.txt_messages.tag_configure("PEER_TAG", foreground=COLOR_GREEN, font=FONT_BOLD)
        self.txt_messages.tag_configure("PEER_MSG", foreground=COLOR_TEXT, font=FONT_MSG)
        self.txt_messages.tag_configure("REPLY_BADGE", foreground="#38bdf8", font=("Consolas", 9, "italic"))

        # Right: Peers / Online Mesh Users
        peers_frame = tk.LabelFrame(main_body, text=" [ NETWORK PEERS ] ",
                                    bg=COLOR_PANEL, fg=COLOR_CYAN, font=FONT_TITLE, bd=1, relief="solid")
        main_body.add(peers_frame, minsize=280)

        self.lbl_peer_count = tk.Label(peers_frame, text="ONLINE NODES: 1", fg=COLOR_YELLOW, bg=COLOR_PANEL, font=FONT_BOLD)
        self.lbl_peer_count.pack(anchor="w", padx=10, pady=(6, 4))

        list_container = tk.Frame(peers_frame, bg=COLOR_ENTRY_BG)
        list_container.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        self.list_peers = tk.Listbox(
            list_container, bg=COLOR_ENTRY_BG, fg=COLOR_GREEN, selectbackground="#004d20",
            selectforeground="#ffffff", font=FONT_MAIN, bd=0, highlightthickness=0
        )
        list_scroll = ttk.Scrollbar(list_container, orient="vertical", command=self.list_peers.yview)
        self.list_peers.configure(yscrollcommand=list_scroll.set)

        self.list_peers.pack(side="left", fill="both", expand=True)
        list_scroll.pack(side="right", fill="y")

        # Double click peer to open private chat
        self.list_peers.bind("<Double-Button-1>", lambda e: self.open_private_chat_from_selection())

        # Peer action buttons
        btn_box = tk.Frame(peers_frame, bg=COLOR_PANEL)
        btn_box.pack(fill="x", padx=8, pady=(0, 8))

        btn_priv = tk.Button(
            btn_box, text="💬 OPEN PRIVATE CHAT",
            bg="#2e1065", fg="#d8b4fe", activebackground="#4c1d95", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", cursor="hand2", pady=4,
            command=self.open_private_chat_from_selection
        )
        btn_priv.pack(fill="x", pady=2)

        btn_reply = tk.Button(
            btn_box, text="↩️ PUBLIC REPLY TO PEER",
            bg="#0c4a6e", fg="#7dd3fc", activebackground="#0369a1", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", cursor="hand2", pady=4,
            command=self.set_reply_from_selection
        )
        btn_reply.pack(fill="x", pady=2)

        # ----------------- BOTTOM INPUT BAR -----------------
        input_frame = tk.Frame(self.root, bg=COLOR_PANEL, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Reply Quote Banner (appears when replying)
        self.reply_banner = tk.Frame(input_frame, bg="#0c233c", bd=1, relief="solid")
        self.lbl_reply_info = tk.Label(
            self.reply_banner, text="↩️ Replying to @...",
            fg="#38bdf8", bg="#0c233c", font=("Segoe UI", 9, "bold")
        )
        self.lbl_reply_info.pack(side="left", padx=10, pady=3)

        btn_cancel_reply = tk.Button(
            self.reply_banner, text="✖ Cancel", bg="#0c233c", fg="#ef4444",
            font=("Consolas", 8, "bold"), bd=0, relief="flat", cursor="hand2",
            command=self.cancel_reply
        )
        btn_cancel_reply.pack(side="right", padx=10, pady=3)

        # Entry row
        entry_box = tk.Frame(input_frame, bg=COLOR_PANEL)
        entry_box.pack(fill="x", padx=10, pady=(6, 8))

        self.entry_message = tk.Entry(
            entry_box, bg=COLOR_ENTRY_BG, fg="#ffffff", insertbackground=COLOR_GREEN,
            font=("Segoe UI", 11), bd=1, relief="solid"
        )
        self.entry_message.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=4)
        self.entry_message.bind("<Return>", lambda e: self.send_public_message())

        self.btn_send = tk.Button(
            entry_box, text="🚀 TRANSMIT [ENTER]",
            bg="#02381b", fg=COLOR_GREEN, activebackground="#056b34", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", padx=15, cursor="hand2",
            command=self.send_public_message
        )
        self.btn_send.pack(side="right")

    # ----------------- REPLY SYSTEM -----------------
    def set_reply_from_selection(self):
        sel = self.list_peers.curselection()
        if not sel:
            messagebox.showinfo("Select Peer", "Click a peer in the list first to reply to them.")
            return

        idx = sel[0]
        if idx == 0:
            target_nick = self.my_nick
        else:
            peer_ips = list(self.peers.keys())
            if idx - 1 < len(peer_ips):
                target_ip = peer_ips[idx - 1]
                target_nick = self.peers[target_ip]["nick"]
            else:
                return

        self.replying_to = {"nick": target_nick}
        self.lbl_reply_info.config(text=f"↩️ Replying to @{target_nick} in Public Stream:")
        self.reply_banner.pack(fill="x", padx=10, pady=(6, 0), before=self.entry_message.master)
        self.entry_message.focus_set()

    def cancel_reply(self):
        self.replying_to = None
        self.reply_banner.pack_forget()

    # ----------------- PRIVATE CHAT WINDOW MANAGER -----------------
    def open_private_chat_from_selection(self):
        sel = self.list_peers.curselection()
        if not sel or sel[0] == 0:
            messagebox.showinfo("Select Peer", "Please select another online peer (not yourself) to chat privately.")
            return

        peer_index = sel[0] - 1
        peer_ips = list(self.peers.keys())
        if 0 <= peer_index < len(peer_ips):
            target_ip = peer_ips[peer_index]
            nick = self.peers[target_ip]["nick"]
            self.get_or_open_private_window(target_ip, nick)

    def get_or_open_private_window(self, ip, nick):
        if ip in self.private_windows:
            win = self.private_windows[ip]
            win.top.deiconify()
            win.top.lift()
            win.top.focus_force()
            return win
        else:
            win = PrivateChatWindow(self, ip, nick)
            self.private_windows[ip] = win
            return win

    # ----------------- STEALTH / PANIC BOSS-KEY MODE -----------------
    def activate_stealth_mode(self):
        """Immediately conceals the chat and presents an innocent disguise."""
        self.root.withdraw()
        # Also hide any open private windows
        for win in self.private_windows.values():
            win.top.withdraw()
        self.stealth_win = StealthDisguiseWindow(on_restore_callback=self.restore_from_stealth)

    def restore_from_stealth(self):
        """Restores the hacker chat window."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        for win in self.private_windows.values():
            win.top.deiconify()

    # ----------------- ADMIN COMMANDS -----------------
    def admin_clear_all_chats(self):
        """Admin command: Clears public chat on all peers."""
        if not self.is_admin:
            return
        
        confirm = messagebox.askyesno("CONFIRM WIPE", "Wipe public chat history on ALL connected peer screens?")
        if not confirm:
            return

        cmd_pkt = {
            "type": "ADMIN_CMD",
            "cmd": "CLEAR_SCREEN",
            "sender_ip": self.local_ip,
            "nick": self.my_nick
        }
        self.send_packet(cmd_pkt, "255.255.255.255")
        self._execute_screen_wipe("YOU (ROOT ADMIN)")

    def admin_toggle_mute(self):
        """Admin command: Mutes or unmutes the room."""
        if not self.is_admin:
            return

        self.is_room_muted = not self.is_room_muted
        status_txt = "MUTED" if self.is_room_muted else "UNMUTED"
        btn_txt = "🔊 UNMUTE ROOM" if self.is_room_muted else "🔇 MUTE ROOM"
        self.btn_mute.config(text=btn_txt)

        cmd_pkt = {
            "type": "ADMIN_CMD",
            "cmd": "ROOM_MUTE",
            "muted": self.is_room_muted,
            "sender_ip": self.local_ip,
            "nick": self.my_nick
        }
        self.send_packet(cmd_pkt, "255.255.255.255")
        self.add_system_message(f"ROOM {status_txt} BY ADMIN.")

    def admin_flash_alert(self):
        """Admin command: Sends a high-priority red alert."""
        if not self.is_admin:
            return

        alert_text = self.entry_message.get().strip()
        if not alert_text:
            alert_text = "⚠️ ATTENTION: PRIORITY NOTICE FROM ROOT ADMIN!"

        cmd_pkt = {
            "type": "ADMIN_CMD",
            "cmd": "FLASH_ALERT",
            "sender_ip": self.local_ip,
            "nick": self.my_nick,
            "text": alert_text
        }
        self.send_packet(cmd_pkt, "255.255.255.255")
        self.add_system_message(f"FLASH ALERT DISPATCHED: \"{alert_text}\"", "ALERT")
        self.entry_message.delete(0, "end")

    def _execute_screen_wipe(self, authority):
        self.txt_messages.delete("1.0", "end")
        ts = time.strftime("[%H:%M:%S] ")
        self.txt_messages.insert("end", ts, "TIME")
        self.txt_messages.insert("end", f"🧹 [SYSTEM] CHAT HISTORY WAS WIPED CLEAN BY: {authority}\n", "SYS")
        self.txt_messages.see("end")

    # ----------------- NETWORK PROTOCOL -----------------
    def update_nickname(self, event=None):
        new_nick = self.entry_nick.get().strip()
        if new_nick and new_nick != self.my_nick:
            old = self.my_nick
            self.my_nick = new_nick
            self.add_system_message(f"IDENTIFIER UPDATED: {old} -> {self.my_nick}")
            self.send_packet({"type": "HEARTBEAT", "nick": self.my_nick, "ip": self.local_ip})

    def send_packet(self, payload, dest_ip="255.255.255.255"):
        try:
            raw_json = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            if self.encrypt_enabled.get():
                raw_json = b"ENC:" + xor_cipher(raw_json)
            self.sock.sendto(raw_json, (dest_ip, UDP_PORT))
        except Exception:
            pass

    def _udp_listen_worker(self):
        """Listens continuously for incoming UDP packets."""
        while self.is_running:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                sender_ip = addr[0]

                if data.startswith(b"ENC:"):
                    decrypted = xor_cipher(data[4:])
                    packet = json.loads(decrypted.decode("utf-8", errors="ignore"))
                else:
                    packet = json.loads(data.decode("utf-8", errors="ignore"))

                p_type = packet.get("type")
                p_nick = packet.get("nick", "ANONYMOUS")

                # 1. Admin Commands
                if p_type == "ADMIN_CMD":
                    if sender_ip == ADMIN_IP or sender_ip == "127.0.0.1":
                        cmd = packet.get("cmd")
                        if cmd == "CLEAR_SCREEN":
                            self.root.after(0, lambda: self._execute_screen_wipe(f"ADMIN [{sender_ip}]"))
                        elif cmd == "ROOM_MUTE":
                            muted = packet.get("muted", False)
                            self.is_room_muted = muted
                            m_status = "MUTED" if muted else "UNMUTED"
                            self.root.after(0, lambda: self.add_system_message(f"ROOM HAS BEEN {m_status} BY ADMIN.", "ALERT"))
                        elif cmd == "FLASH_ALERT":
                            a_text = packet.get("text", "")
                            self.root.after(0, lambda: self.render_flash_alert(p_nick, a_text))
                    continue

                # 2. Heartbeat
                if p_type == "HEARTBEAT":
                    if sender_ip != self.local_ip:
                        is_new = sender_ip not in self.peers
                        self.peers[sender_ip] = {"nick": p_nick, "last_seen": time.time()}
                        if is_new:
                            self.root.after(0, lambda n=p_nick, ip=sender_ip: self.add_system_message(f"[+] NODE JOINED: {n} [{ip}]"))
                        self.root.after(0, self.refresh_peers_ui)

                # 3. Leave
                elif p_type == "LEAVE":
                    if sender_ip in self.peers:
                        del self.peers[sender_ip]
                        self.root.after(0, lambda n=p_nick, ip=sender_ip: self.add_system_message(f"[-] NODE LEFT: {n} [{ip}]"))
                        self.root.after(0, self.refresh_peers_ui)

                # 4. Dedicated Private Message
                elif p_type == "PRIVATE_MSG":
                    target = packet.get("target")
                    if target == self.local_ip:
                        content = packet.get("text", "")
                        ts = packet.get("time", time.strftime("%H:%M:%S"))
                        self.root.after(0, lambda ip=sender_ip, n=p_nick, c=content, t=ts: self._handle_incoming_private(ip, n, c, t))

                # 5. Public Message / Public Reply
                elif p_type == "MSG":
                    if sender_ip == self.local_ip:
                        continue

                    content = packet.get("text", "")
                    ts = packet.get("time", time.strftime("%H:%M:%S"))
                    from_admin = (sender_ip == ADMIN_IP)
                    reply_to = packet.get("reply_to")

                    self.peers[sender_ip] = {"nick": p_nick, "last_seen": time.time()}
                    self.root.after(0, self.refresh_peers_ui)
                    self.root.after(0, lambda: self.render_public_message(p_nick, sender_ip, content, ts, from_admin, reply_to))

            except Exception:
                pass

    def _handle_incoming_private(self, sender_ip, sender_nick, content, ts):
        if self.sound_enabled.get() and HAS_SOUND:
            try:
                winsound.Beep(1100, 80)
            except Exception:
                pass
        win = self.get_or_open_private_window(sender_ip, sender_nick)
        win.append_incoming(content, ts)

    def _heartbeat_worker(self):
        while self.is_running:
            try:
                pkt = {"type": "HEARTBEAT", "nick": self.my_nick, "ip": self.local_ip}
                self.send_packet(pkt)
            except Exception:
                pass
            time.sleep(3)

    def _peer_cleanup_worker(self):
        while self.is_running:
            now = time.time()
            expired = []
            for ip, info in list(self.peers.items()):
                if now - info["last_seen"] > 10:
                    expired.append((ip, info["nick"]))

            for ip, nick in expired:
                if ip in self.peers:
                    del self.peers[ip]
                    self.root.after(0, lambda n=nick, i=ip: self.add_system_message(f"[-] NODE TIMED OUT: {n} [{i}]"))
                    self.root.after(0, self.refresh_peers_ui)

            time.sleep(2)

    # ----------------- UI UPDATES -----------------
    def refresh_peers_ui(self):
        self.list_peers.delete(0, "end")

        self.list_peers.insert("end", f"🟢 {self.my_nick} (YOU) [{self.local_ip}]")
        self.list_peers.itemconfig(0, fg=COLOR_CYAN)

        idx = 1
        for ip, info in self.peers.items():
            crown = "👑 " if ip == ADMIN_IP else "🟢 "
            display = f"{crown}{info['nick']} [{ip}]"
            self.list_peers.insert("end", display)
            if ip == ADMIN_IP:
                self.list_peers.itemconfig(idx, fg=COLOR_YELLOW)
            idx += 1

        total = len(self.peers) + 1
        self.lbl_peer_count.config(text=f"ONLINE NODES: {total}")

    def add_system_message(self, text, tag="SYS"):
        ts = time.strftime("[%H:%M:%S] ")
        self.txt_messages.insert("end", ts, "TIME")
        self.txt_messages.insert("end", f"[SYSTEM] {text}\n", tag)
        self.txt_messages.see("end")

    def render_flash_alert(self, nick, text):
        if self.sound_enabled.get() and HAS_SOUND:
            try:
                winsound.Beep(1500, 250)
            except Exception:
                pass
        ts = time.strftime("[%H:%M:%S] ")
        self.txt_messages.insert("end", ts, "TIME")
        self.txt_messages.insert("end", f"🚨 [ADMIN BROADCAST ALERT FROM {nick}]: {text}\n", "ALERT")
        self.txt_messages.see("end")

    def render_public_message(self, nick, ip, text, ts, from_admin=False, reply_to=None):
        if self.sound_enabled.get() and HAS_SOUND:
            try:
                winsound.Beep(900, 60)
            except Exception:
                pass

        self.txt_messages.insert("end", f"[{ts}] ", "TIME")

        if from_admin:
            self.txt_messages.insert("end", f"👑 <{nick}> (ADMIN)", "ADMIN_TAG")
        else:
            self.txt_messages.insert("end", f"<{nick}>", "PEER_TAG")

        if reply_to:
            self.txt_messages.insert("end", f" ↳ (Replying to @{reply_to})", "REPLY_BADGE")

        self.txt_messages.insert("end", ": ")

        if from_admin:
            self.txt_messages.insert("end", f"{text}\n", "ADMIN_MSG")
        else:
            self.txt_messages.insert("end", f"{text}\n", "PEER_MSG")

        self.txt_messages.see("end")

    def send_public_message(self):
        if self.is_room_muted and not self.is_admin:
            messagebox.showwarning("ROOM MUTED", "The room is currently muted by Root Admin. Only Admin can speak.")
            return

        text = self.entry_message.get().strip()
        if not text:
            return

        ts = time.strftime("%H:%M:%S")
        reply_to_nick = self.replying_to["nick"] if self.replying_to else None

        packet = {
            "type": "MSG",
            "nick": self.my_nick,
            "ip": self.local_ip,
            "target": "ALL",
            "reply_to": reply_to_nick,
            "text": text,
            "time": ts
        }
        self.send_packet(packet, "255.255.255.255")

        # Render locally
        self.txt_messages.insert("end", f"[{ts}] ", "TIME")
        if self.is_admin:
            self.txt_messages.insert("end", f"👑 <{self.my_nick}> (YOU/ADMIN)", "ADMIN_TAG")
        else:
            self.txt_messages.insert("end", f"<{self.my_nick}>", "ME_TAG")

        if reply_to_nick:
            self.txt_messages.insert("end", f" ↳ (Replying to @{reply_to_nick})", "REPLY_BADGE")

        self.txt_messages.insert("end", ": ")

        if self.is_admin:
            self.txt_messages.insert("end", f"{text}\n", "ADMIN_MSG")
        else:
            self.txt_messages.insert("end", f"{text}\n", "ME_MSG")

        self.txt_messages.see("end")
        self.entry_message.delete(0, "end")
        self.cancel_reply()

    def on_close(self):
        self.is_running = False
        try:
            leave_pkt = {"type": "LEAVE", "nick": self.my_nick, "ip": self.local_ip}
            self.send_packet(leave_pkt)
            self.sock.close()
        except Exception:
            pass
        self.root.destroy()


if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    app = CyberChatApp(root)
    root.mainloop()
