# -*- coding: utf-8 -*-
"""
CYBER-LAN SUPER SUITE v3.2 (MASTER EDITION)
Customized to user specifications:
1. 50 messages history limit
2. Open / unlimited file & video transfer
3. Single-host Watch Party with Admin priority override
4. Both built-in and custom favorite stickers
5. 4-hour streak warning with Friday/Saturday freeze + 3 & 10-day milestone celebrations with total messages count
6. Groups creation open to all users with MANDATORY Admin inclusion
7. Unlimited players Snakes & Ladders (join mid-game at square 1)
8. Bio displayed alongside Nickname everywhere
9. Admin Lockdown (Option A) to pause games/movies during lecture time and delete stories
"""

import os
import sys
import time
import json
import socket
import threading
import shutil
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import winsound
    HAS_SOUND = True
except Exception:
    HAS_SOUND = False

from db_manager import DatabaseManager, ADMIN_IP
from media_server import media_server_instance, WATCH_PARTY_STATE, MEDIA_DIR, DOWNLOADS_DIR
from games_engine import TicTacToeGame, SnakesLaddersGame

# ----------------- CONFIGURATION -----------------
UDP_PORT = 54321
BUFFER_SIZE = 65535
XOR_KEY = 0x5A
REQUIRED_PASSWORD = "Sd2027"

# ----------------- HACKER PALETTE -----------------
COLOR_BG = "#05070c"
COLOR_SIDEBAR = "#090d16"
COLOR_PANEL = "#0d1320"
COLOR_PANEL_ALT = "#121b2d"
COLOR_ENTRY_BG = "#03060a"
COLOR_GREEN = "#00ff66"
COLOR_CYAN = "#00f0ff"
COLOR_YELLOW = "#ffd000"
COLOR_RED = "#ff2a55"
COLOR_PURPLE = "#c084fc"
COLOR_TEXT = "#e2e8f0"
COLOR_DIM = "#64748b"
COLOR_BORDER = "#1b2a47"

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
    return bytes([b ^ XOR_KEY for b in data_bytes])


# ----------------- AUTHENTICATION MODAL -----------------
class AuthGateModal:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.top.title("SECURITY CLEARANCE // GATEWAY")
        self.top.geometry("460x310")
        self.top.resizable(False, False)
        self.top.configure(bg=COLOR_BG)
        self.top.attributes("-topmost", True)
        self.authenticated = False
        self.attempts_left = 3

        self.top.update_idletasks()
        x = (self.top.winfo_screenwidth() - 460) // 2
        y = (self.top.winfo_screenheight() - 310) // 2
        self.top.geometry(f"+{x}+{y}")

        self._build_ui()
        self.top.protocol("WM_DELETE_WINDOW", self.top.destroy)
        self.entry_pass.focus_set()

    def _build_ui(self):
        frame = tk.Frame(self.top, bg=COLOR_PANEL, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(frame, text="[ # ] CYBER-LAN SUPER SUITE v3.2", fg=COLOR_GREEN, bg=COLOR_PANEL, font=FONT_TITLE).pack(pady=(16, 2))
        tk.Label(frame, text="ENTER NETWORK CLEARANCE PASSPHRASE:", fg=COLOR_CYAN, bg=COLOR_PANEL, font=("Consolas", 9)).pack(pady=(0, 15))

        self.entry_pass = tk.Entry(
            frame, bg=COLOR_ENTRY_BG, fg=COLOR_GREEN, insertbackground=COLOR_GREEN,
            font=("Consolas", 14, "bold"), show="*", justify="center", bd=1, relief="solid", width=20
        )
        self.entry_pass.pack(pady=5, ipady=4)
        self.entry_pass.bind("<Return>", lambda e: self.check_password())

        self.lbl_status = tk.Label(frame, text="STATUS: LOCKED // ENTER KEY", fg=COLOR_DIM, bg=COLOR_PANEL, font=("Consolas", 8))
        self.lbl_status.pack(pady=(10, 15))

        btn = tk.Button(
            frame, text="🔓 UNLOCK PLATFORM [ENTER]",
            bg="#02381b", fg=COLOR_GREEN, activebackground="#056b34", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", padx=20, pady=5, cursor="hand2", command=self.check_password
        )
        btn.pack()

    def check_password(self):
        if self.entry_pass.get() == REQUIRED_PASSWORD:
            self.authenticated = True
            if HAS_SOUND:
                try: winsound.Beep(1200, 100)
                except Exception: pass
            self.top.destroy()
        else:
            self.attempts_left -= 1
            if HAS_SOUND:
                try: winsound.Beep(400, 200)
                except Exception: pass
            if self.attempts_left > 0:
                self.lbl_status.config(text=f"[!] INVALID PASSPHRASE. {self.attempts_left} ATTEMPTS LEFT.", fg=COLOR_RED)
                self.entry_pass.delete(0, "end")
            else:
                messagebox.showerror("LOCKOUT", "Access Terminated.")
                self.top.destroy()


# ----------------- STEALTH DISGUISE WINDOW (BOSS KEY) -----------------
class StealthDisguiseWindow:
    def __init__(self, on_restore):
        self.on_restore = on_restore
        self.top = tk.Toplevel()
        self.top.title("Physics Unit 1 - Scientific Reference & Model Revision Notes")
        self.top.geometry("900x600")
        self.top.configure(bg="#f8fafc")

        tb = tk.Frame(self.top, bg="#e2e8f0", bd=1, relief="solid")
        tb.pack(fill="x", side="top")
        tk.Label(tb, text="📘 Ministry of Education - Science & Physics Digital Library", bg="#e2e8f0", fg="#1e293b", font=("Segoe UI", 9, "bold")).pack(side="left", padx=10, pady=6)
        
        btn_stealth = tk.Button(tb, text="🔍 Refresh Notes (F12)", bg="#cbd5e1", fg="#475569", font=("Segoe UI", 8), bd=0, relief="flat", cursor="hand2", command=self.restore)
        btn_stealth.pack(side="right", padx=10, pady=4)

        text_area = tk.Text(self.top, bg="#ffffff", fg="#0f172a", font=("Segoe UI", 11), wrap="word", padx=25, pady=20, bd=0)
        text_area.pack(fill="both", expand=True)
        text_area.insert("1.0", "UNIT 1: MOTION IN ONE DIRECTION & PHYSICAL QUANTITIES\nSpeed = Distance / Time\nAcceleration = Change in Velocity / Time.\n[F12 to return]")
        text_area.config(state="disabled")

        self.top.bind("<F12>", lambda e: self.restore())
        self.top.protocol("WM_DELETE_WINDOW", self.restore)

    def restore(self):
        self.top.destroy()
        self.on_restore()


# ----------------- MASTER SUPER SUITE APPLICATION -----------------
class CyberSuperSuiteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CYBER-LAN SUPER SUITE v3.2 // MASTER EDITION")
        self.root.geometry("1220x820")
        self.root.minsize(1080, 700)
        self.root.configure(bg=COLOR_BG)

        # Database & Local Profile
        self.db = DatabaseManager()
        self.local_ip, self.default_host = get_local_ip_and_hostname()
        self.profile = self.db.get_profile(self.local_ip, self.default_host)
        self.my_nick = self.profile["nickname"]
        self.my_avatar = self.profile["avatar"]
        self.my_bio = self.profile.get("bio", "Lab Operator")
        self.is_admin = (self.local_ip == ADMIN_IP or self.local_ip == "127.0.0.1")

        # Media Server Start
        ok, p = media_server_instance.start()
        self.media_port = p

        # App State
        self.peers = {}               # { ip: {"nick": ..., "avatar": ..., "bio": ..., "last_seen": ...} }
        self.active_tab = "PUBLIC"
        self.current_group_id = None
        self.replying_to = None
        self.active_game = None       # TicTacToeGame or SnakesLaddersGame instance
        self.is_room_muted = False
        self.is_locked_down = False   # Admin Lockdown (Option A)
        self.is_running = True
        self.watch_host_ip = None

        # Password Gate
        self.root.withdraw()
        auth = AuthGateModal(self.root)
        self.root.wait_window(auth.top)
        if not auth.authenticated:
            self.root.destroy()
            sys.exit(0)

        self.root.deiconify()
        self._setup_socket()
        self._build_ui()

        # Keyboard shortcuts
        self.root.bind("<F12>", lambda e: self.activate_stealth())
        self.root.bind("<Escape>", lambda e: self.activate_stealth())

        # Network worker threads
        threading.Thread(target=self._udp_listen_worker, daemon=True).start()
        threading.Thread(target=self._heartbeat_worker, daemon=True).start()
        threading.Thread(target=self._peer_cleanup_worker, daemon=True).start()

        self.load_history_for_active_view()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _setup_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try: self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except Exception: pass
        self.sock.bind(("0.0.0.0", UDP_PORT))

    def _build_ui(self):
        # ----------------- TOP HEADER BAR -----------------
        header = tk.Frame(self.root, bg=COLOR_PANEL, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        header.pack(fill="x", side="top", padx=8, pady=(8, 4))

        tk.Label(header, text="[ # ] CYBER-LAN SUPER SUITE v3.2", fg=COLOR_GREEN, bg=COLOR_PANEL, font=FONT_TITLE).pack(side="left", padx=12, pady=8)
        
        role_tag = "👑 ROOT ADMIN" if self.is_admin else "🟢 OPERATOR"
        role_fg = COLOR_YELLOW if self.is_admin else COLOR_CYAN
        
        # Displaying Bio alongside Name
        tk.Label(header, text=f"{self.my_avatar} {self.my_nick} [{self.my_bio}] | {role_tag}", fg=role_fg, bg=COLOR_PANEL, font=FONT_BOLD).pack(side="left", padx=10)

        btn_stealth = tk.Button(header, text="🕶️ STEALTH (F12)", bg="#182234", fg=COLOR_CYAN, font=FONT_BOLD, bd=1, relief="solid", cursor="hand2", padx=8, command=self.activate_stealth)
        btn_stealth.pack(side="right", padx=10, pady=6)

        # Streak Indicator Top Pill with 4-hour warning & weekend freeze
        count, hours_left, is_warning_4h, is_frozen = self.db.get_streak_status("PUBLIC", "ALL")
        if is_frozen:
            streak_txt = f"🔥 LOBBY STREAK: {count} DAYS [❄️ WEEKEND FROZEN]"
            streak_color = "#38bdf8"
        elif is_warning_4h:
            streak_txt = f"⚠️ STREAK EXPIRES IN {hours_left}H! ({count} DAYS)"
            streak_color = COLOR_RED
        else:
            streak_txt = f"🔥 LOBBY STREAK: {count} DAYS ({hours_left}h left)"
            streak_color = COLOR_YELLOW

        self.lbl_streak_top = tk.Label(header, text=streak_txt, fg=streak_color, bg=COLOR_PANEL, font=FONT_BOLD)
        self.lbl_streak_top.pack(side="right", padx=12)

        # Admin Super-Controls (Option A)
        if self.is_admin:
            self.btn_lockdown = tk.Button(
                header, text="🚫 LOCKDOWN LECTURE", bg="#3b0712", fg="#ff4d6d",
                font=FONT_BOLD, bd=1, relief="solid", padx=6, cursor="hand2", command=self.admin_toggle_lockdown
            )
            self.btn_lockdown.pack(side="right", padx=4)

            btn_wipe = tk.Button(header, text="🧹 WIPE CHAT", bg="#451a03", fg=COLOR_YELLOW, font=FONT_BOLD, bd=1, relief="solid", padx=6, cursor="hand2", command=self.admin_wipe)
            btn_wipe.pack(side="right", padx=4)

        # ----------------- MAIN HORIZONTAL SPLIT -----------------
        main_container = tk.Frame(self.root, bg=COLOR_BG)
        main_container.pack(fill="both", expand=True, padx=8, pady=4)

        # 1. NAVIGATION SIDEBAR (LEFT)
        sidebar = tk.Frame(main_container, bg=COLOR_SIDEBAR, width=210, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        sidebar.pack(side="left", fill="y", padx=(0, 6))

        tk.Label(sidebar, text=" NAVIGATION ", fg=COLOR_DIM, bg=COLOR_SIDEBAR, font=("Consolas", 8, "bold")).pack(anchor="w", padx=12, pady=(10, 6))

        nav_items = [
            ("💬 Public Lobby", "PUBLIC"),
            ("👥 Groups Hub", "GROUPS"),
            ("🎮 Games Arena", "GAMES"),
            ("🎬 Watch Party", "WATCH"),
            ("📸 Stories Vault", "STORIES"),
            ("⭐ Stickers & Media", "STICKERS"),
            ("⚙️ Profile & ID", "PROFILE")
        ]

        self.nav_buttons = {}
        for text, tab_id in nav_items:
            btn = tk.Button(
                sidebar, text=text, bg=COLOR_PANEL, fg=COLOR_TEXT, activebackground="#1e293b", activeforeground="#ffffff",
                font=FONT_BOLD, bd=0, relief="flat", anchor="w", padx=15, pady=8, cursor="hand2",
                command=lambda t=tab_id: self.switch_tab(t)
            )
            btn.pack(fill="x", pady=2, padx=6)
            self.nav_buttons[tab_id] = btn

        # Total Messages Counter at bottom of sidebar
        tot = self.db.get_total_messages_count()
        self.lbl_tot_msgs = tk.Label(sidebar, text=f"📊 MSGS LOGGED: {tot}", fg=COLOR_CYAN, bg=COLOR_SIDEBAR, font=("Consolas", 8))
        self.lbl_tot_msgs.pack(side="bottom", pady=(0, 5))

        self.lbl_peer_count = tk.Label(sidebar, text="🟢 ONLINE: 1 PEERS", fg=COLOR_GREEN, bg=COLOR_SIDEBAR, font=FONT_BOLD)
        self.lbl_peer_count.pack(side="bottom", pady=(5, 5))

        # 2. CENTRAL CONTENT AREA
        self.content_area = tk.Frame(main_container, bg=COLOR_PANEL, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        self.content_area.pack(side="left", fill="both", expand=True)

        # 3. RIGHT PANEL (PEERS LIST WITH BIOS & ACTIONS)
        self.right_panel = tk.Frame(main_container, bg=COLOR_PANEL, width=260, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        self.right_panel.pack(side="right", fill="y", padx=(6, 0))

        tk.Label(self.right_panel, text=" [ LAN PEERS & BIOS ] ", fg=COLOR_CYAN, bg=COLOR_PANEL, font=FONT_BOLD).pack(pady=8)
        self.list_peers = tk.Listbox(self.right_panel, bg=COLOR_ENTRY_BG, fg=COLOR_GREEN, selectbackground="#004d20", selectforeground="#ffffff", font=FONT_MAIN, bd=0)
        self.list_peers.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        btn_p_reply = tk.Button(self.right_panel, text="↩️ Public Reply", bg="#0c4a6e", fg="#7dd3fc", font=FONT_BOLD, bd=1, relief="solid", cursor="hand2", command=self.set_reply_from_peer)
        btn_p_reply.pack(fill="x", padx=8, pady=2)

        btn_p_invite = tk.Button(self.right_panel, text="🎮 Challenge X-O", bg="#3b0764", fg="#d8b4fe", font=FONT_BOLD, bd=1, relief="solid", cursor="hand2", command=self.quick_challenge_game)
        btn_p_invite.pack(fill="x", padx=8, pady=2)

        self.build_chat_view(self.content_area)

    # ----------------- TAB SWITCHER (LOCKDOWN ENFORCEMENT) -----------------
    def switch_tab(self, tab_id):
        # Admin Lockdown Option A: non-admins cannot open Games or Watch Party during lecture lockdown
        if self.is_locked_down and not self.is_admin and tab_id in ("GAMES", "WATCH"):
            messagebox.showwarning("🔒 LECTURE LOCKDOWN", "Games and Watch Party are currently paused by Root Admin for lecture focus!")
            return

        self.active_tab = tab_id
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.config(bg="#004d20", fg="#ffffff")
            else:
                btn.config(bg=COLOR_PANEL, fg=COLOR_TEXT)

        for widget in self.content_area.winfo_children():
            widget.destroy()

        if tab_id == "PUBLIC":
            self.build_chat_view(self.content_area, "PUBLIC")
        elif tab_id == "GROUPS":
            self.build_groups_view(self.content_area)
        elif tab_id == "GAMES":
            self.build_games_view(self.content_area)
        elif tab_id == "WATCH":
            self.build_watch_view(self.content_area)
        elif tab_id == "STORIES":
            self.build_stories_view(self.content_area)
        elif tab_id == "STICKERS":
            self.build_stickers_view(self.content_area)
        elif tab_id == "PROFILE":
            self.build_profile_view(self.content_area)

    # ----------------- 1. CHAT VIEW (50 MESSAGES LIMIT) -----------------
    def build_chat_view(self, parent, mode="PUBLIC"):
        title_text = "💬 PUBLIC ROOM // ALL PEERS (LAST 50 MSGS)" if mode == "PUBLIC" else f"👥 GROUP // {self.current_group_id}"
        hdr = tk.Frame(parent, bg=COLOR_PANEL_ALT, bd=1, relief="solid")
        hdr.pack(fill="x")
        tk.Label(hdr, text=title_text, fg=COLOR_GREEN, bg=COLOR_PANEL_ALT, font=FONT_TITLE).pack(side="left", padx=12, pady=6)

        # Stories bar at top of chat
        stories_bar = tk.Frame(parent, bg=COLOR_BG, bd=1, relief="solid")
        stories_bar.pack(fill="x", padx=6, pady=4)
        tk.Label(stories_bar, text="📸 Stories:", fg=COLOR_YELLOW, bg=COLOR_BG, font=FONT_BOLD).pack(side="left", padx=8)

        active_stories = self.db.get_active_stories()
        if not active_stories:
            tk.Label(stories_bar, text="No stories yet. Click Stories Vault to post!", fg=COLOR_DIM, bg=COLOR_BG, font=("Consolas", 8)).pack(side="left")
        else:
            for s in active_stories[:6]:
                btn_st = tk.Button(
                    stories_bar, text=f"🟣 {s['author_nick']}", bg="#1e1b4b", fg="#c084fc", font=("Consolas", 8, "bold"),
                    bd=0, relief="flat", cursor="hand2", command=lambda st=s: self.view_single_story(st)
                )
                btn_st.pack(side="left", padx=4, pady=2)

        msg_container = tk.Frame(parent, bg=COLOR_ENTRY_BG)
        msg_container.pack(fill="both", expand=True, padx=6, pady=4)

        self.txt_messages = tk.Text(msg_container, bg=COLOR_ENTRY_BG, fg=COLOR_TEXT, insertbackground=COLOR_GREEN, font=FONT_MSG, bd=0, wrap="word", padx=8, pady=8)
        scroll = ttk.Scrollbar(msg_container, orient="vertical", command=self.txt_messages.yview)
        self.txt_messages.configure(yscrollcommand=scroll.set)
        self.txt_messages.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.txt_messages.tag_configure("TIME", foreground=COLOR_DIM, font=FONT_TIME)
        self.txt_messages.tag_configure("SYS", foreground=COLOR_YELLOW, font=FONT_TIME)
        self.txt_messages.tag_configure("ME_TAG", foreground=COLOR_CYAN, font=FONT_BOLD)
        self.txt_messages.tag_configure("PEER_TAG", foreground=COLOR_GREEN, font=FONT_BOLD)
        self.txt_messages.tag_configure("BIO_TAG", foreground="#94a3b8", font=("Consolas", 8))
        self.txt_messages.tag_configure("REPLY_BADGE", foreground="#38bdf8", font=("Consolas", 9, "italic"))
        self.txt_messages.tag_configure("MILESTONE", foreground="#f43f5e", font=("Consolas", 10, "bold"))

        # Reply Banner
        self.reply_banner = tk.Frame(parent, bg="#0c233c", bd=1, relief="solid")
        self.lbl_reply_info = tk.Label(self.reply_banner, text="↩️ Replying to @...", fg="#38bdf8", bg="#0c233c", font=FONT_BOLD)
        self.lbl_reply_info.pack(side="left", padx=10, pady=3)
        tk.Button(self.reply_banner, text="✖ Cancel", bg="#0c233c", fg="#ef4444", bd=0, relief="flat", cursor="hand2", command=self.cancel_reply).pack(side="right", padx=10)

        # Bottom Input Bar
        input_bar = tk.Frame(parent, bg=COLOR_PANEL_ALT, bd=1, relief="solid")
        input_bar.pack(fill="x", side="bottom", padx=6, pady=6)

        btn_attach = tk.Button(input_bar, text="📎 Open File", bg="#1e293b", fg=COLOR_CYAN, font=FONT_BOLD, bd=1, relief="solid", cursor="hand2", command=self.send_file_dialog)
        btn_attach.pack(side="left", padx=(6, 2), pady=6)

        btn_stick = tk.Button(input_bar, text="⭐ Stickers", bg="#1e293b", fg=COLOR_YELLOW, font=FONT_BOLD, bd=1, relief="solid", cursor="hand2", command=lambda: self.switch_tab("STICKERS"))
        btn_stick.pack(side="left", padx=2, pady=6)

        self.entry_message = tk.Entry(input_bar, bg=COLOR_ENTRY_BG, fg="#ffffff", insertbackground=COLOR_GREEN, font=("Segoe UI", 11), bd=1, relief="solid")
        self.entry_message.pack(side="left", fill="x", expand=True, padx=6, pady=6, ipady=3)
        self.entry_message.bind("<Return>", lambda e: self.send_chat_message())

        btn_send = tk.Button(input_bar, text="🚀 SEND", bg="#02381b", fg=COLOR_GREEN, font=FONT_BOLD, bd=1, relief="solid", padx=15, cursor="hand2", command=self.send_chat_message)
        btn_send.pack(side="right", padx=(0, 6), pady=6)

        self.load_history_for_active_view()

    # ----------------- 2. GROUPS VIEW (MANDATORY ADMIN INCLUSION) -----------------
    def build_groups_view(self, parent):
        tk.Label(parent, text="👥 GROUPS HUB // OPEN TO ALL (ADMIN MANDATORY MEMBER)", fg=COLOR_CYAN, bg=COLOR_PANEL, font=FONT_TITLE).pack(pady=10)

        top_ctrl = tk.Frame(parent, bg=COLOR_PANEL)
        top_ctrl.pack(fill="x", padx=15, pady=6)

        tk.Label(top_ctrl, text="NEW GROUP NAME:", fg=COLOR_TEXT, bg=COLOR_PANEL, font=FONT_BOLD).pack(side="left")
        entry_grp = tk.Entry(top_ctrl, bg=COLOR_ENTRY_BG, fg=COLOR_GREEN, font=FONT_MAIN, width=20)
        entry_grp.pack(side="left", padx=8)

        def create_grp():
            gname = entry_grp.get().strip()
            if gname:
                gid = f"GRP_{int(time.time())}"
                # Mandatory admin inclusion
                self.db.create_group(gid, gname, self.local_ip, description=f"Admin {ADMIN_IP} included automatically")
                self.send_packet({"type": "GROUP_CREATED", "gid": gid, "name": gname, "creator": self.my_nick, "admin_included": ADMIN_IP})
                self.switch_tab("GROUPS")

        tk.Button(top_ctrl, text="➕ Create Group", bg="#02381b", fg=COLOR_GREEN, font=FONT_BOLD, command=create_grp).pack(side="left")

        groups = self.db.get_groups()
        g_frame = tk.Frame(parent, bg=COLOR_ENTRY_BG, bd=1, relief="solid")
        g_frame.pack(fill="both", expand=True, padx=15, pady=10)

        for g in groups:
            row = tk.Frame(g_frame, bg=COLOR_PANEL, bd=1, relief="solid")
            row.pack(fill="x", padx=8, pady=4)
            count, h_left, warn, frozen = self.db.get_streak_status("GROUP", g["group_id"])
            tag = "[FROZEN ❄️]" if frozen else f"({h_left}h left)"
            tk.Label(row, text=f"👥 {g['group_name']} [🔥 Streak: {count} {tag}] [👑 Admin Inside]", fg=COLOR_GREEN, bg=COLOR_PANEL, font=FONT_BOLD).pack(side="left", padx=10, pady=8)

            btn_open = tk.Button(
                row, text="Open Group Chat", bg="#0c4a6e", fg="#7dd3fc", font=FONT_MAIN,
                command=lambda gid=g["group_id"]: self.open_group_chat(gid)
            )
            btn_open.pack(side="right", padx=10)

    def open_group_chat(self, group_id):
        self.current_group_id = group_id
        for widget in self.content_area.winfo_children():
            widget.destroy()
        self.build_chat_view(self.content_area, mode="GROUP")

    # ----------------- 3. GAMES ARENA VIEW (UNLIMITED PLAYERS) -----------------
    def build_games_view(self, parent):
        tk.Label(parent, text="🎮 GAMES ARENA // UNLIMITED PLAYERS & SPECTATOR", fg=COLOR_PURPLE, bg=COLOR_PANEL, font=FONT_TITLE).pack(pady=10)

        card_frame = tk.Frame(parent, bg=COLOR_PANEL)
        card_frame.pack(fill="x", padx=20, pady=8)

        # X-O Card
        c1 = tk.LabelFrame(card_frame, text=" [ X-O // TIC-TAC-TOE ] ", bg=COLOR_PANEL_ALT, fg=COLOR_CYAN, font=FONT_BOLD, bd=1, relief="solid")
        c1.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        tk.Label(c1, text="2 Players turn-based duel.\nSpectators can watch live!", fg=COLOR_TEXT, bg=COLOR_PANEL_ALT, font=FONT_MAIN).pack(pady=8)
        tk.Button(c1, text="⚔️ Challenge Peer to X-O", bg="#02381b", fg=COLOR_GREEN, font=FONT_BOLD, command=lambda: self.launch_game_challenge("XO")).pack(pady=6)

        # Snakes & Ladders Card (Unlimited Players)
        c2 = tk.LabelFrame(card_frame, text=" [ 🪜 SNAKES & LADDERS (السلم والتعبان) ] ", bg=COLOR_PANEL_ALT, fg=COLOR_YELLOW, font=FONT_BOLD, bd=1, relief="solid")
        c2.pack(side="right", fill="both", expand=True, padx=8, pady=8)
        tk.Label(c2, text="UNLIMITED PLAYERS!\nAnyone can jump in mid-game (starts at Sq 1)!", fg=COLOR_TEXT, bg=COLOR_PANEL_ALT, font=FONT_MAIN).pack(pady=8)
        
        btn_bar = tk.Frame(c2, bg=COLOR_PANEL_ALT)
        btn_bar.pack(pady=6)
        tk.Button(btn_bar, text="🎲 Start Game", bg="#3b0764", fg="#d8b4fe", font=FONT_BOLD, command=lambda: self.launch_game_challenge("SNAKES")).pack(side="left", padx=4)
        tk.Button(btn_bar, text="➕ Join Active Race (Sq 1)", bg="#064e3b", fg="#6ee7b7", font=FONT_BOLD, command=self.join_snakes_race).pack(side="left", padx=4)

        # Active Games / Spectator Board
        spectate_frame = tk.LabelFrame(parent, text=" [ 👁️ ACTIVE GAME BOARD & LIVE SPECTATORS ] ", bg=COLOR_PANEL, fg=COLOR_YELLOW, font=FONT_BOLD, bd=1, relief="solid")
        spectate_frame.pack(fill="both", expand=True, padx=20, pady=8)

        if not self.active_game:
            tk.Label(spectate_frame, text="No game currently running. Challenge a peer or join the race above!", fg=COLOR_DIM, bg=COLOR_PANEL, font=FONT_MAIN).pack(pady=30)
        else:
            self.render_active_game_canvas(spectate_frame)

    def launch_game_challenge(self, game_type):
        sel = self.list_peers.curselection()
        if not sel:
            messagebox.showinfo("Select Target", "Please click a peer in the right-side list first to challenge them!")
            return
        idx = sel[0]
        peer_ips = list(self.peers.keys())
        if idx < len(peer_ips):
            target_ip = peer_ips[idx]
            target_nick = self.peers[target_ip]["nick"]
            gid = f"GAME_{int(time.time())}"
            self.send_packet({
                "type": "GAME_INVITE",
                "game_type": game_type,
                "game_id": gid,
                "challenger_ip": self.local_ip,
                "challenger_nick": self.my_nick,
                "target_ip": target_ip
            })
            messagebox.showinfo("Challenge Sent", f"Invitation sent to {target_nick}! Waiting for them to accept...")

    def join_snakes_race(self):
        """Unlimited player join mid-game at square 1."""
        if not self.active_game or not isinstance(self.active_game, SnakesLaddersGame):
            messagebox.showinfo("No Active Race", "No Snakes & Ladders game is currently running to join. Start one first!")
            return

        ok, msg = self.active_game.join_game(self.local_ip, self.my_nick)
        if ok:
            self.send_packet({"type": "GAME_STATE", "state": self.active_game.to_dict()})
            self.switch_tab("GAMES")
            messagebox.showinfo("Joined Race!", f"You joined the Snakes & Ladders race at Square 1!")
        else:
            messagebox.showinfo("Status", msg)

    def quick_challenge_game(self):
        self.launch_game_challenge("XO")

    def render_active_game_canvas(self, parent):
        g = self.active_game
        if isinstance(g, TicTacToeGame):
            frm = tk.Frame(parent, bg=COLOR_BG)
            frm.pack(pady=10)
            tk.Label(frm, text=f"X-O: {g.player_x['nick']} (X) vs {g.player_o['nick']} (O) | Turn: {g.current_turn}", fg=COLOR_CYAN, bg=COLOR_BG, font=FONT_BOLD).pack(pady=5)
            b_grid = tk.Frame(frm, bg=COLOR_BORDER)
            b_grid.pack(pady=5)
            for i in range(9):
                val = g.board[i]
                btn = tk.Button(
                    b_grid, text=val, width=4, height=2, font=("Consolas", 16, "bold"),
                    bg="#0f172a", fg=COLOR_GREEN if val == "X" else COLOR_CYAN,
                    command=lambda idx=i: self.make_xo_move(idx)
                )
                btn.grid(row=i//3, column=i%3, padx=2, pady=2)
        elif isinstance(g, SnakesLaddersGame):
            frm = tk.Frame(parent, bg=COLOR_BG)
            frm.pack(fill="both", expand=True, pady=10)
            tk.Label(frm, text=f"SNAKES & LADDERS (UNLIMITED PLAYERS) | {g.last_event_msg}", fg=COLOR_YELLOW, bg=COLOR_BG, font=FONT_BOLD).pack(pady=4)

            pos_box = tk.Frame(frm, bg=COLOR_PANEL_ALT)
            pos_box.pack(fill="x", padx=15, pady=4)
            for p in g.players:
                sq = g.positions.get(p["ip"], 1)
                tk.Label(pos_box, text=f"{p['nick']}: Sq {sq}/100", fg=p.get("color", COLOR_GREEN), bg=COLOR_PANEL_ALT, font=FONT_BOLD).pack(side="left", padx=10, pady=4)

            curr_p = g.players[g.current_player_idx]
            if curr_p["ip"] == self.local_ip:
                tk.Button(frm, text="🎲 ROLL DICE", bg="#02381b", fg=COLOR_GREEN, font=FONT_BOLD, padx=20, pady=5, command=self.roll_snakes_dice).pack(pady=8)
            else:
                tk.Label(frm, text=f"Waiting for {curr_p['nick']} to roll...", fg=COLOR_CYAN, bg=COLOR_BG, font=FONT_MAIN).pack(pady=8)

    def make_xo_move(self, idx):
        if isinstance(self.active_game, TicTacToeGame):
            my_sym = "X" if self.active_game.player_x["ip"] == self.local_ip else "O"
            ok, msg = self.active_game.make_move(idx, my_sym)
            if ok:
                self.send_packet({"type": "GAME_STATE", "state": self.active_game.to_dict()})
                self.switch_tab("GAMES")

    def roll_snakes_dice(self):
        if isinstance(self.active_game, SnakesLaddersGame):
            ok, msg = self.active_game.roll_dice(self.local_ip)
            if ok:
                self.send_packet({"type": "GAME_STATE", "state": self.active_game.to_dict()})
                self.switch_tab("GAMES")

    # ----------------- 4. WATCH PARTY VIEW (SINGLE HOST & ADMIN PRIORITY) -----------------
    def build_watch_view(self, parent):
        tk.Label(parent, text="🎬 CYBER WATCH-PARTY // LOCAL HOST STREAMING", fg=COLOR_CYAN, bg=COLOR_PANEL, font=FONT_TITLE).pack(pady=10)

        card = tk.Frame(parent, bg=COLOR_PANEL_ALT, bd=1, relief="solid")
        card.pack(fill="x", padx=25, pady=10)

        host_label = WATCH_PARTY_STATE['host_nick']
        status_txt = f"ACTIVE MOVIE: {WATCH_PARTY_STATE['movie_title']} [Broadcaster: {host_label}]"
        tk.Label(card, text=status_txt, fg=COLOR_YELLOW, bg=COLOR_PANEL_ALT, font=FONT_BOLD).pack(pady=10)

        btn_box = tk.Frame(card, bg=COLOR_PANEL_ALT)
        btn_box.pack(pady=8)

        # Host button with Admin priority override
        tk.Button(btn_box, text="📁 Host Movie from My Machine", bg="#02381b", fg=COLOR_GREEN, font=FONT_BOLD, command=self.pick_movie_file).pack(side="left", padx=6)
        
        btn_open_browser = tk.Button(
            btn_box, text="🚀 OPEN SYNCED CINEMA & SIDE-CHAT",
            bg="#2e1065", fg="#d8b4fe", font=("Consolas", 11, "bold"), padx=12, pady=6, cursor="hand2",
            command=self.open_cinema_theater
        )
        btn_open_browser.pack(side="left", padx=6)

        desc = (
            "Rule: Only ONE Host can broadcast at a time (Admin has priority override).\n"
            "The Host streams the movie directly from their machine; all peers view the synced stream and chat side-by-side!"
        )
        tk.Label(parent, text=desc, fg=COLOR_DIM, bg=COLOR_PANEL, font=FONT_MAIN, justify="center").pack(pady=10)

    def pick_movie_file(self):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.webm *.mkv")])
        if path:
            title = os.path.basename(path)
            ok, res = media_server_instance.claim_host(self.local_ip, self.my_nick, path, title)
            if not ok:
                messagebox.showerror("Host Conflict", res)
                return

            self.send_packet({
                "type": "WATCH_ANNOUNCE",
                "movie_title": title,
                "host_ip": self.local_ip,
                "host_nick": self.my_nick
            })
            messagebox.showinfo("Cinema Ready", f"You are broadcasting '{title}'! Everyone on the LAN can now watch.")
            self.switch_tab("WATCH")

    def open_cinema_theater(self):
        host = WATCH_PARTY_STATE.get("host_ip") or self.local_ip
        url = f"http://{host}:{self.media_port}/watch"
        webbrowser.open(url)

    # ----------------- 5. STORIES VIEW (ADMIN CAN DELETE) -----------------
    def build_stories_view(self, parent):
        tk.Label(parent, text="📸 STORIES VAULT // 24H EPHEMERAL STATUS", fg=COLOR_YELLOW, bg=COLOR_PANEL, font=FONT_TITLE).pack(pady=10)

        post_box = tk.LabelFrame(parent, text=" [ POST A NEW STORY ] ", bg=COLOR_PANEL_ALT, fg=COLOR_GREEN, font=FONT_BOLD, bd=1, relief="solid")
        post_box.pack(fill="x", padx=20, pady=8)

        self.entry_story_text = tk.Entry(post_box, bg=COLOR_ENTRY_BG, fg="#ffffff", font=FONT_MAIN)
        self.entry_story_text.pack(fill="x", padx=10, pady=8, ipady=3)

        btn_post = tk.Button(post_box, text="🚀 Post Story (Expires in 24h)", bg="#02381b", fg=COLOR_GREEN, font=FONT_BOLD, command=self.post_story)
        btn_post.pack(pady=(0, 8))

        tk.Label(parent, text="ACTIVE STORIES ON NETWORK:", fg=COLOR_CYAN, bg=COLOR_PANEL, font=FONT_BOLD).pack(anchor="w", padx=20, pady=(10, 4))
        stories = self.db.get_active_stories()
        st_frame = tk.Frame(parent, bg=COLOR_ENTRY_BG, bd=1, relief="solid")
        st_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        for s in stories:
            c = tk.Frame(st_frame, bg=COLOR_PANEL, bd=1, relief="solid")
            c.pack(fill="x", padx=8, pady=4)
            tk.Label(c, text=f"🟣 {s['author_nick']}: \"{s['content_text']}\"", fg=COLOR_TEXT, bg=COLOR_PANEL, font=FONT_BOLD).pack(side="left", padx=10, pady=8)
            
            # Admin delete button
            if self.is_admin:
                btn_del = tk.Button(
                    c, text="🗑️ Delete", bg="#450a0a", fg="#fca5a5", font=("Consolas", 8, "bold"),
                    command=lambda sid=s["story_id"]: self.admin_delete_story(sid)
                )
                btn_del.pack(side="right", padx=6)

            tk.Label(c, text=f"Expires: {s['expires_at'][:16]}", fg=COLOR_DIM, bg=COLOR_PANEL, font=("Consolas", 8)).pack(side="right", padx=10)

    def post_story(self):
        val = self.entry_story_text.get().strip()
        if not val: return
        sid = f"STORY_{int(time.time())}"
        self.db.post_story(sid, self.local_ip, self.my_nick, val)
        self.send_packet({"type": "STORY_POST", "story_id": sid, "author_nick": self.my_nick, "text": val})
        self.entry_story_text.delete(0, "end")
        self.switch_tab("STORIES")

    def admin_delete_story(self, sid):
        if not self.is_admin: return
        self.db.delete_story(sid)
        self.send_packet({"type": "ADMIN_DELETE_STORY", "story_id": sid})
        self.switch_tab("STORIES")

    def view_single_story(self, st):
        messagebox.showinfo(f"Story from @{st['author_nick']}", f"\"{st['content_text']}\"\n\nPosted: {st['created_at']}\nExpires: {st['expires_at']}")

    # ----------------- 6. STICKERS & MEDIA VIEW (BOTH TYPES) -----------------
    def build_stickers_view(self, parent):
        tk.Label(parent, text="⭐ STICKERS & MEDIA VAULT // BOTH BUILT-IN & CUSTOM FAVORITES", fg=COLOR_YELLOW, bg=COLOR_PANEL, font=FONT_TITLE).pack(pady=10)

        top_bar = tk.Frame(parent, bg=COLOR_PANEL)
        top_bar.pack(fill="x", padx=20, pady=6)
        tk.Button(top_bar, text="➕ Add Custom Image / GIF to Favorite Stickers", bg="#02381b", fg=COLOR_GREEN, font=FONT_BOLD, command=self.add_custom_sticker_dialog).pack(side="left")

        stickers = self.db.get_favorite_stickers()
        grid = tk.Frame(parent, bg=COLOR_ENTRY_BG, bd=1, relief="solid")
        grid.pack(fill="both", expand=True, padx=20, pady=10)

        for i, st in enumerate(stickers):
            btn = tk.Button(
                grid, text=f"{st['symbol']}\n{st['name']}", width=12, height=3,
                bg=COLOR_PANEL, fg=COLOR_GREEN, font=("Segoe UI", 12, "bold"), bd=1, relief="solid",
                cursor="hand2", command=lambda s=st['symbol']: self.send_sticker(s)
            )
            btn.grid(row=i//4, column=i%4, padx=8, pady=8)

    def send_sticker(self, symbol):
        self.send_chat_message(custom_text=f"[STICKER: {symbol}]", msg_type="STICKER")
        self.switch_tab("PUBLIC")

    def add_custom_sticker_dialog(self):
        name = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.gif")])
        if name:
            bname = os.path.basename(name)
            self.db.add_favorite_sticker(bname, "🖼️", name)
            messagebox.showinfo("Sticker Added", f"'{bname}' added to your favorite stickers!")
            self.switch_tab("STICKERS")

    # ----------------- 7. PROFILE & IDENTITY (BIO WITH NAME) -----------------
    def build_profile_view(self, parent):
        tk.Label(parent, text="⚙️ IDENTITY & USER PROFILE // BIO SAVED TO DATABASE", fg=COLOR_CYAN, bg=COLOR_PANEL, font=FONT_TITLE).pack(pady=10)

        box = tk.LabelFrame(parent, text=" [ CUSTOMIZE PROFILE ] ", bg=COLOR_PANEL_ALT, fg=COLOR_GREEN, font=FONT_BOLD, bd=1, relief="solid")
        box.pack(fill="x", padx=30, pady=15)

        tk.Label(box, text="NICKNAME / HANDLE:", fg=COLOR_TEXT, bg=COLOR_PANEL_ALT, font=FONT_BOLD).pack(anchor="w", padx=15, pady=(10, 2))
        entry_nick = tk.Entry(box, bg=COLOR_ENTRY_BG, fg=COLOR_GREEN, font=FONT_MAIN)
        entry_nick.insert(0, self.my_nick)
        entry_nick.pack(fill="x", padx=15, pady=(0, 10))

        tk.Label(box, text="CYBER AVATAR (Emoji / Icon):", fg=COLOR_TEXT, bg=COLOR_PANEL_ALT, font=FONT_BOLD).pack(anchor="w", padx=15, pady=(5, 2))
        entry_avatar = tk.Entry(box, bg=COLOR_ENTRY_BG, fg=COLOR_YELLOW, font=FONT_MAIN)
        entry_avatar.insert(0, self.my_avatar)
        entry_avatar.pack(fill="x", padx=15, pady=(0, 10))

        tk.Label(box, text="BIO / STATUS LINE (Appears next to your name):", fg=COLOR_TEXT, bg=COLOR_PANEL_ALT, font=FONT_BOLD).pack(anchor="w", padx=15, pady=(5, 2))
        entry_bio = tk.Entry(box, bg=COLOR_ENTRY_BG, fg=COLOR_CYAN, font=FONT_MAIN)
        entry_bio.insert(0, self.my_bio)
        entry_bio.pack(fill="x", padx=15, pady=(0, 15))

        def save_p():
            nn = entry_nick.get().strip() or self.my_nick
            av = entry_avatar.get().strip() or "⚡"
            bi = entry_bio.get().strip() or "Operator"
            self.db.save_profile(nn, av, bi)
            self.my_nick = nn
            self.my_avatar = av
            self.my_bio = bi
            messagebox.showinfo("Saved", "Profile & Bio saved permanently in database!")
            self.switch_tab("PUBLIC")

        tk.Button(box, text="💾 Save Profile to Database", bg="#02381b", fg=COLOR_GREEN, font=FONT_BOLD, padx=15, pady=6, command=save_p).pack(pady=(0, 15))

    # ----------------- CHAT & INTERACTIVE ATTACHMENTS -----------------
    def load_history_for_active_view(self):
        if not hasattr(self, "txt_messages"): return
        self.txt_messages.delete("1.0", "end")

        target_type = "PUBLIC" if self.active_tab == "PUBLIC" else "GROUP"
        target_id = "ALL" if target_type == "PUBLIC" else self.current_group_id
        if not target_id: return

        msgs = self.db.get_messages(target_type, target_id, limit=50)
        for m in msgs:
            ts = m["timestamp"]
            sender = m["sender_nick"]
            reply_to = m["reply_to"]
            content = m["content"]
            is_me = m["is_me"]
            mtype = m.get("msg_type", "TEXT")
            fmeta = m.get("file_meta")

            self.render_single_message(sender, content, ts, is_me, reply_to, mtype, fmeta)

        self.txt_messages.see("end")

    def render_single_message(self, sender, content, ts, is_me, reply_to=None, mtype="TEXT", file_meta=None):
        if not hasattr(self, "txt_messages"): return

        # Parse file_meta if string
        if file_meta and isinstance(file_meta, str):
            try:
                file_meta = json.loads(file_meta)
            except Exception:
                file_meta = None

        # Fallback detection for older attachment text formats
        if (mtype == "FILE" or "FILE ATTACHMENT:" in content) and not file_meta:
            import re
            m = re.search(r"FILE ATTACHMENT:\s*([^\s(]+)", content)
            if m:
                fname = m.group(1).strip()
                file_meta = {
                    "filename": fname,
                    "size_mb": 0.04,
                    "url": f"http://{self.local_ip}:{self.media_port}/files/{fname}"
                }

        # Timestamp and Sender header
        self.txt_messages.insert("end", f"[{ts[-8:]}] ", "TIME")
        tag = "ME_TAG" if is_me else "PEER_TAG"
        self.txt_messages.insert("end", f"<{sender}>", tag)
        if reply_to:
            self.txt_messages.insert("end", f" ↳ (Replying to @{reply_to})", "REPLY_BADGE")

        if mtype == "FILE" or file_meta:
            self.txt_messages.insert("end", ":\n")
            self._insert_file_attachment_card(file_meta)
            self.txt_messages.insert("end", "\n")
        else:
            self.txt_messages.insert("end", f": {content}\n")

        self.txt_messages.see("end")

    def _insert_file_attachment_card(self, file_meta):
        if not file_meta: return
        filename = file_meta.get("filename", "file")
        size_mb = file_meta.get("size_mb", 0.0)

        ext = os.path.splitext(filename)[1].lower()
        is_img = ext in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")
        is_vid = ext in (".mp4", ".webm", ".mkv", ".avi")
        is_doc = ext in (".pdf", ".docx", ".pptx", ".txt", ".xlsx")

        if is_img:
            icon = "🖼️"
            type_label = "IMAGE // صورة"
            open_btn_text = "👁️ عرض وفتح الصورة"
        elif is_vid:
            icon = "🎬"
            type_label = "VIDEO // فيديو"
            open_btn_text = "▶️ تشغيل الفيديو"
        elif is_doc:
            icon = "📄"
            type_label = "DOCUMENT // مستند"
            open_btn_text = "📖 فتح المستند"
        else:
            icon = "📁"
            type_label = "FILE // ملف"
            open_btn_text = "📥 فتح الملف"

        # Interactive Cyber Card Frame inside Chat
        card = tk.Frame(self.txt_messages, bg="#0b172a", bd=1, relief="solid", highlightbackground=COLOR_CYAN, padx=12, pady=8)

        # Header inside Card
        hdr_frame = tk.Frame(card, bg="#0b172a")
        hdr_frame.pack(fill="x", pady=(0, 6))

        tk.Label(
            hdr_frame, text=f"{icon} {filename}",
            fg=COLOR_GREEN, bg="#0b172a", font=("Segoe UI", 11, "bold")
        ).pack(side="left")

        tk.Label(
            hdr_frame, text=f"[{size_mb} MB]  ● {type_label}",
            fg=COLOR_YELLOW, bg="#0b172a", font=("Consolas", 9)
        ).pack(side="right", padx=10)

        # Buttons row
        btn_row = tk.Frame(card, bg="#0b172a")
        btn_row.pack(fill="x", pady=(2, 0))

        btn_open = tk.Button(
            btn_row, text=open_btn_text,
            bg="#02381b", fg=COLOR_GREEN, activebackground="#056b34", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", padx=14, pady=4, cursor="hand2"
        )
        btn_open.config(command=lambda fm=file_meta, b=btn_open: self.open_or_download_attachment(fm, b))
        btn_open.pack(side="left", padx=(0, 8))

        btn_folder = tk.Button(
            btn_row, text="📂 فتح في المجلد",
            bg="#1e293b", fg="#7dd3fc", activebackground="#334155", activeforeground="#ffffff",
            font=FONT_MAIN, bd=1, relief="solid", padx=10, pady=4, cursor="hand2",
            command=lambda fm=file_meta: self.open_file_folder(fm)
        )
        btn_folder.pack(side="left")

        # Embed Card Widget into Text widget
        self.txt_messages.window_create("end", window=card)

    def open_or_download_attachment(self, file_meta, btn=None):
        filename = file_meta.get("filename", "")
        url = file_meta.get("url", "")

        # 1. Check local media dir (sent by me)
        local_path = os.path.join(MEDIA_DIR, filename)
        if os.path.exists(local_path):
            try:
                os.startfile(os.path.abspath(local_path))
                return
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
                return

        # 2. Check downloads dir (already downloaded from peer)
        dl_path = os.path.join(DOWNLOADS_DIR, filename)
        if os.path.exists(dl_path):
            try:
                os.startfile(os.path.abspath(dl_path))
                return
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
                return

        # 3. Download from sender peer URL
        if not url:
            messagebox.showerror("Missing URL", "No download URL provided for this file.")
            return

        def download_worker():
            if btn:
                self.root.after(0, lambda: btn.config(text="⏳ جاري التحميل...", state="disabled"))
            try:
                import urllib.request
                os.makedirs(DOWNLOADS_DIR, exist_ok=True)
                urllib.request.urlretrieve(url, dl_path)
                if btn:
                    self.root.after(0, lambda: btn.config(text="✅ تم الفتح", state="normal"))
                self.root.after(0, lambda: os.startfile(os.path.abspath(dl_path)))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Download Error", f"فشل تحميل الملف من جهاز الزميل:\n{e}\n\nتأكد من فتح البرنامج على كلا الجهازين."))
                if btn:
                    self.root.after(0, lambda: btn.config(text="❌ إعادة المحاولة", state="normal"))

        threading.Thread(target=download_worker, daemon=True).start()

    def open_file_folder(self, file_meta):
        filename = file_meta.get("filename", "")
        local_path = os.path.join(MEDIA_DIR, filename)
        dl_path = os.path.join(DOWNLOADS_DIR, filename)

        target = local_path if os.path.exists(local_path) else dl_path
        if os.path.exists(target):
            import subprocess
            subprocess.Popen(f'explorer /select,"{os.path.abspath(target)}"')
        else:
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            os.startfile(os.path.abspath(DOWNLOADS_DIR))

    def send_chat_message(self, custom_text=None, msg_type="TEXT", file_meta=None):
        if self.is_room_muted and not self.is_admin:
            messagebox.showwarning("Muted", "Room is muted by Admin.")
            return

        text = custom_text if custom_text else self.entry_message.get().strip()
        if not text and not file_meta: return

        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        target_type = "PUBLIC" if self.active_tab == "PUBLIC" else "GROUP"
        target_id = "ALL" if target_type == "PUBLIC" else self.current_group_id
        reply_to_nick = self.replying_to["nick"] if self.replying_to else None
        muuid = f"MSG_{int(time.time()*1000)}"

        # Save to DB (50 limit query automatically trims on retrieval)
        self.db.save_message(muuid, self.local_ip, self.my_nick, target_type, target_id, text, msg_type, file_meta, reply_to_nick, ts, 1)

        # Update Streak & Check 3/10 milestones
        new_streak, is_milestone = self.db.record_streak_interaction(target_type, target_id)
        tot_msgs = self.db.get_total_messages_count()
        self.lbl_tot_msgs.config(text=f"📊 MSGS LOGGED: {tot_msgs}")
        self.lbl_streak_top.config(text=f"🔥 LOBBY STREAK: {new_streak} DAYS")

        if is_milestone:
            milestone_alert = f"🎉 [STREAK MILESTONE REACHED: {new_streak} DAYS! Total Messages Logged: {tot_msgs}!] 🚀"
            self.db.save_message(f"MILESTONE_{int(time.time())}", "SYSTEM", "LAN-BOT", target_type, target_id, milestone_alert, "SYS", None, None, ts, 0)

        # Network broadcast
        pkt = {
            "type": "CHAT_MSG",
            "muuid": muuid,
            "nick": self.my_nick,
            "bio": self.my_bio,
            "ip": self.local_ip,
            "target_type": target_type,
            "target_id": target_id,
            "reply_to": reply_to_nick,
            "text": text,
            "msg_type": msg_type,
            "file_meta": file_meta,
            "time": ts
        }
        self.send_packet(pkt)

        if hasattr(self, "txt_messages"):
            self.render_single_message(self.my_nick, text, ts, True, reply_to_nick, msg_type, file_meta)
            if is_milestone:
                self.txt_messages.insert("end", f"🎉 [STREAK MILESTONE: {new_streak} DAYS! Total Messages: {tot_msgs}!]\n", "MILESTONE")
            self.txt_messages.see("end")

        if hasattr(self, "entry_message"):
            self.entry_message.delete(0, "end")
        self.cancel_reply()

    def send_file_dialog(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*")]
        )
        if filepath:
            filename = os.path.basename(filepath)
            dest = os.path.join(MEDIA_DIR, filename)
            if os.path.abspath(filepath) != os.path.abspath(dest):
                shutil.copy2(filepath, dest)

            file_size_mb = os.path.getsize(dest) / (1024 * 1024)
            file_meta = {
                "filename": filename,
                "size_mb": round(file_size_mb, 2),
                "url": f"http://{self.local_ip}:{self.media_port}/files/{filename}"
            }
            msg_text = f"📁 [FILE ATTACHMENT: {filename} ({file_meta['size_mb']} MB)]"
            self.send_chat_message(custom_text=msg_text, msg_type="FILE", file_meta=file_meta)

    # ----------------- REPLIES & STEALTH -----------------
    def set_reply_from_peer(self):
        sel = self.list_peers.curselection()
        if not sel: return
        idx = sel[0]
        peer_ips = list(self.peers.keys())
        if idx < len(peer_ips):
            target_nick = self.peers[peer_ips[idx]]["nick"]
            self.replying_to = {"nick": target_nick}
            if hasattr(self, "lbl_reply_info"):
                self.lbl_reply_info.config(text=f"↩️ Replying to @{target_nick} in Public Stream:")
                self.reply_banner.pack(fill="x", padx=6, pady=(4, 0), before=self.entry_message.master)
                self.entry_message.focus_set()

    def cancel_reply(self):
        self.replying_to = None
        if hasattr(self, "reply_banner"):
            self.reply_banner.pack_forget()

    def activate_stealth(self):
        self.root.withdraw()
        self.stealth_win = StealthDisguiseWindow(on_restore=self.restore_from_stealth)

    def restore_from_stealth(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    # ----------------- ADMIN CONTROLS (OPTION A) -----------------
    def admin_toggle_lockdown(self):
        if not self.is_admin: return
        self.is_locked_down = not self.is_locked_down
        state_txt = "ENABLED" if self.is_locked_down else "DISABLED"
        btn_txt = "✅ UNLOCK LECTURE" if self.is_locked_down else "🚫 LOCKDOWN LECTURE"
        self.btn_lockdown.config(text=btn_txt)

        self.send_packet({"type": "ADMIN_LOCKDOWN", "locked": self.is_locked_down})
        messagebox.showinfo("Admin Lockdown", f"Lecture Lockdown is now {state_txt}. Games and Watch Party are {'restricted' if self.is_locked_down else 'restored'}.")

    def admin_wipe(self):
        if not self.is_admin: return
        if messagebox.askyesno("Confirm", "Wipe all public chats on all screens?"):
            self.db.clear_public_messages()
            self.send_packet({"type": "ADMIN_WIPE"})
            self.load_history_for_active_view()

    # ----------------- NETWORK PROTOCOL -----------------
    def send_packet(self, payload, dest="255.255.255.255"):
        try:
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            enc = b"ENC:" + xor_cipher(raw)
            self.sock.sendto(enc, (dest, UDP_PORT))
        except Exception: pass

    def _udp_listen_worker(self):
        while self.is_running:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                sender_ip = addr[0]

                if data.startswith(b"ENC:"):
                    decrypted = xor_cipher(data[4:])
                    pkt = json.loads(decrypted.decode("utf-8", errors="ignore"))
                else:
                    pkt = json.loads(data.decode("utf-8", errors="ignore"))

                ptype = pkt.get("type")
                pnick = pkt.get("nick", "Node")
                pbio = pkt.get("bio", "Operator")

                if ptype == "HEARTBEAT":
                    if sender_ip != self.local_ip:
                        self.peers[sender_ip] = {
                            "nick": pnick, "avatar": pkt.get("avatar", "🟢"),
                            "bio": pbio, "last_seen": time.time()
                        }
                        self.root.after(0, self.refresh_peers_list)

                elif ptype == "CHAT_MSG":
                    if sender_ip == self.local_ip: continue
                    self.db.save_message(
                        pkt["muuid"], sender_ip, pnick, pkt["target_type"], pkt["target_id"],
                        pkt["text"], pkt.get("msg_type", "TEXT"), pkt.get("file_meta"), pkt.get("reply_to"), pkt["time"], 0
                    )
                    new_st, _ = self.db.record_streak_interaction(pkt["target_type"], pkt["target_id"])
                    self.root.after(0, lambda: self.lbl_streak_top.config(text=f"🔥 LOBBY STREAK: {new_st} DAYS"))
                    self.root.after(0, self.load_history_for_active_view)

                elif ptype == "WATCH_ANNOUNCE":
                    WATCH_PARTY_STATE["movie_title"] = pkt["movie_title"]
                    WATCH_PARTY_STATE["host_ip"] = pkt["host_ip"]
                    WATCH_PARTY_STATE["host_nick"] = pkt["host_nick"]
                    self.root.after(0, lambda: messagebox.showinfo("Watch Party!", f"🎬 @{pkt['host_nick']} started streaming '{pkt['movie_title']}'!"))

                elif ptype == "GAME_INVITE":
                    if pkt.get("target_ip") == self.local_ip:
                        self.root.after(0, lambda p=pkt: self._handle_game_invite(p))

                elif ptype == "GAME_STATE":
                    self.root.after(0, lambda s=pkt["state"]: self._handle_game_state_sync(s))

                elif ptype == "ADMIN_LOCKDOWN":
                    self.is_locked_down = pkt["locked"]
                    if self.is_locked_down and not self.is_admin:
                        self.root.after(0, lambda: messagebox.showwarning("Lockdown Active", "Root Admin has enabled Lecture Lockdown. Games and Watch Party are paused!"))
                        if self.active_tab in ("GAMES", "WATCH"):
                            self.root.after(0, lambda: self.switch_tab("PUBLIC"))

                elif ptype == "ADMIN_DELETE_STORY":
                    self.db.delete_story(pkt["story_id"])
                    if self.active_tab == "STORIES":
                        self.root.after(0, lambda: self.switch_tab("STORIES"))

                elif ptype == "ADMIN_WIPE":
                    self.db.clear_public_messages()
                    self.root.after(0, self.load_history_for_active_view)

            except Exception: pass

    def _handle_game_invite(self, pkt):
        gtype = pkt["game_type"]
        cnick = pkt["challenger_nick"]
        ans = messagebox.askyesno("Game Challenge!", f"@{cnick} has challenged you to a game of {gtype}!\nDo you accept?")
        if ans:
            if gtype == "XO":
                self.active_game = TicTacToeGame(pkt["game_id"], pkt["challenger_ip"], cnick, self.local_ip, self.my_nick)
            else:
                players = [{"ip": pkt["challenger_ip"], "nick": cnick, "color": "#00ff66"},
                           {"ip": self.local_ip, "nick": self.my_nick, "color": "#00f0ff"}]
                self.active_game = SnakesLaddersGame(pkt["game_id"], players)

            self.send_packet({"type": "GAME_STATE", "state": self.active_game.to_dict()})
            self.switch_tab("GAMES")

    def _handle_game_state_sync(self, state):
        gtype = state["game_type"]
        if gtype == "XO":
            g = TicTacToeGame(state["game_id"], state["player_x"]["ip"], state["player_x"]["nick"], state["player_o"]["ip"], state["player_o"]["nick"])
            g.board = state["board"]
            g.current_turn = state["current_turn"]
            g.winner = state["winner"]
            self.active_game = g
        elif gtype == "SNAKES":
            g = SnakesLaddersGame(state["game_id"], state["players"])
            g.positions = state["positions"]
            g.current_player_idx = state["current_player_idx"]
            g.last_event_msg = state["last_event_msg"]
            g.winner = state["winner"]
            self.active_game = g

        if self.active_tab == "GAMES":
            self.switch_tab("GAMES")

    def _heartbeat_worker(self):
        while self.is_running:
            try:
                pkt = {
                    "type": "HEARTBEAT", "nick": self.my_nick, "avatar": self.my_avatar,
                    "bio": self.my_bio, "ip": self.local_ip
                }
                self.send_packet(pkt)
            except Exception: pass
            time.sleep(3)

    def _peer_cleanup_worker(self):
        while self.is_running:
            now = time.time()
            for ip, info in list(self.peers.items()):
                if now - info["last_seen"] > 10:
                    del self.peers[ip]
            self.root.after(0, self.refresh_peers_list)
            time.sleep(2)

    def refresh_peers_list(self):
        if not hasattr(self, "list_peers"): return
        self.list_peers.delete(0, "end")
        for ip, info in self.peers.items():
            crown = "👑 " if ip == ADMIN_IP else f"{info.get('avatar', '🟢')} "
            bio_disp = f" [{info.get('bio', '')}]" if info.get('bio') else ""
            self.list_peers.insert("end", f"{crown}{info['nick']}{bio_disp} [{ip}]")
        self.lbl_peer_count.config(text=f"🟢 ONLINE: {len(self.peers)+1} PEERS")

    def on_close(self):
        self.is_running = False
        try:
            self.send_packet({"type": "LEAVE", "nick": self.my_nick, "ip": self.local_ip})
            self.sock.close()
        except Exception: pass
        self.root.destroy()


if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception: pass

    root = tk.Tk()
    app = CyberSuperSuiteApp(root)
    root.mainloop()
