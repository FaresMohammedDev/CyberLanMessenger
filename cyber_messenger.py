# -*- coding: utf-8 -*-
"""
CYBER-LAN INJECTOR // REMOTE MESSAGE BROADCASTER
A hacker-themed utility for Windows LAN message popups, device discovery, and mass broadcasting.
"""

import sys
import os
import re
import socket
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------- HACKER PALETTE -----------------
COLOR_BG = "#070b12"         # Deep Terminal Void
COLOR_PANEL = "#0d1424"      # Dark Cyber Panel
COLOR_PANEL_ALT = "#121b30"  # Elevated Cyber Frame
COLOR_ENTRY_BG = "#04070d"   # Inputs
COLOR_GREEN = "#00ff66"      # Neon Matrix Green
COLOR_GREEN_DIM = "#008f39"  # Dim Green
COLOR_CYAN = "#00f0ff"       # Cyberpunk Cyan
COLOR_YELLOW = "#ffd000"     # Alert Yellow
COLOR_RED = "#ff2a55"        # Hazard Red
COLOR_TEXT = "#e2e8f0"       # High-contrast readable text
COLOR_BORDER = "#1f2f4d"     # Border tone
FONT_TITLE = ("Consolas", 11, "bold")
FONT_MAIN = ("Consolas", 10)
FONT_BOLD = ("Consolas", 10, "bold")
FONT_LOG = ("Consolas", 9)


def get_local_network_info():
    """Detects local IPv4 and default /24 subnet prefix."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        subnet_prefix = ".".join(local_ip.split(".")[:3]) + "."
        hostname = socket.gethostname()
        return local_ip, subnet_prefix, hostname
    except Exception:
        return "127.0.0.1", "192.168.1.", "LOCALHOST"


def resolve_hostname(ip):
    """Attempts fast reverse DNS lookup for PC name."""
    try:
        socket.setdefaulttimeout(0.35)
        full_name = socket.gethostbyaddr(ip)[0]
        return full_name.split(".")[0].upper()
    except Exception:
        return "HOST-" + ip.split(".")[-1]


def parse_arp_table():
    """Reads ARP table for quick cached devices and MACs."""
    arp_map = {}
    try:
        res = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=3)
        for line in res.stdout.splitlines():
            line = line.strip()
            # Match: 192.168.20.53   d0-8e-79-18-d0-84   dynamic
            match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]+)\s+(\w+)", line)
            if match:
                ip, mac, ip_type = match.groups()
                if not ip.startswith("224.") and not ip.startswith("239.") and not ip.endswith(".255"):
                    arp_map[ip] = mac.upper()
    except Exception:
        pass
    return arp_map


class CyberMessengerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CYBER-LAN INJECTOR // v2.4")
        self.root.geometry("1100x740")
        self.root.minsize(980, 650)
        self.root.configure(bg=COLOR_BG)

        self.local_ip, self.subnet_prefix, self.my_hostname = get_local_network_info()
        self.active_devices = []  # List of dicts: {'ip': ..., 'hostname': ..., 'mac': ..., 'status': ...}
        self.is_scanning = False
        self.is_broadcasting = False

        self._setup_styles()
        self._build_ui()

        # Initial Welcome Log
        self.log(f"[+] SYSTEM INITIALIZED ON HOST: {self.my_hostname} [{self.local_ip}]", "CYAN")
        self.log(f"[+] DETECTED LOCAL SUBNET: {self.subnet_prefix}0/24", "GREEN")
        self.log("[*] Click [RADAR DEEP SCAN] to scan all devices in the room, or [QUICK ARP SCAN] for cache.", "YELLOW")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Treeview styling (Hacker Grid)
        style.configure(
            "Cyber.Treeview",
            background=COLOR_ENTRY_BG,
            foreground=COLOR_GREEN,
            fieldbackground=COLOR_ENTRY_BG,
            bordercolor=COLOR_BORDER,
            rowheight=26,
            font=FONT_MAIN
        )
        style.map(
            "Cyber.Treeview",
            background=[("selected", "#004d20")],
            foreground=[("selected", "#ffffff")]
        )
        style.configure(
            "Cyber.Treeview.Heading",
            background=COLOR_PANEL_ALT,
            foreground=COLOR_CYAN,
            font=FONT_BOLD,
            relief="flat"
        )
        style.map(
            "Cyber.Treeview.Heading",
            background=[("active", "#1b2a47")]
        )

        # Progressbar
        style.configure(
            "Cyber.Horizontal.TProgressbar",
            troughcolor=COLOR_ENTRY_BG,
            background=COLOR_GREEN,
            bordercolor=COLOR_BORDER,
            lightcolor=COLOR_GREEN,
            darkcolor=COLOR_GREEN_DIM
        )

    def _build_ui(self):
        # ----------------- TOP HEADER -----------------
        header = tk.Frame(self.root, bg=COLOR_PANEL, bd=1, relief="solid", highlightbackground=COLOR_BORDER)
        header.pack(fill="x", padx=10, pady=(10, 5))

        banner_text = (
            "░█████╗░██╗░░░██╗██████╗░███████╗██████╗░░░░░░███╗░░░███╗░██████╗░██████╗░\n"
            "██╔══██╗╚██╗░██╔╝██╔══██╗██╔════╝██╔══██╗░░░░░████╗░████║██╔════╝██╔════╝░\n"
            "██║░░╚═╝░╚████╔╝░██████╦╝█████╗░░██████╔╝█████╗██╔████╔██║╚█████╗░██║░░██╗░\n"
            "██║░░██╗░░╚██╔╝░░██╔══██╗██╔══╝░░██╔══██╗╚════╝██║╚██╔╝██║░╚═══██╗██║░░╚██╗\n"
            "╚█████╔╝░░░██║░░░██████╦╝███████╗██║░░██║░░░░░░██║░╚═╝░██║██████╔╝╚██████╔╝\n"
            "░╚════╝░░░░╚═╝░░░╚═════╝░╚══════╝╚═╝░░╚═╝░░░░░░╚═╝░░░░░╚═╝╚═════╝░░╚═════╝░"
        )
        lbl_banner = tk.Label(header, text=banner_text, fg=COLOR_GREEN, bg=COLOR_PANEL, font=("Consolas", 6), justify="left")
        lbl_banner.pack(side="left", padx=15, pady=6)

        info_frame = tk.Frame(header, bg=COLOR_PANEL)
        info_frame.pack(side="right", padx=15, pady=8)

        lbl_title = tk.Label(info_frame, text="LAN INJECTION CONSOLE", fg=COLOR_CYAN, bg=COLOR_PANEL, font=FONT_TITLE)
        lbl_title.pack(anchor="e")

        info_sub = f"INTERFACE: {self.local_ip}  |  NODE: {self.my_hostname}  |  SECURITY: ARMED"
        lbl_node = tk.Label(info_frame, text=info_sub, fg=COLOR_YELLOW, bg=COLOR_PANEL, font=("Consolas", 9))
        lbl_node.pack(anchor="e", pady=(2, 0))

        # ----------------- MAIN SPLIT BODY -----------------
        main_body = tk.PanedWindow(self.root, orient="horizontal", bg=COLOR_BG, bd=0, sashwidth=4, sashpad=2)
        main_body.pack(fill="both", expand=True, padx=10, pady=5)

        # LEFT PANE: Network Radar & Targets
        left_frame = tk.LabelFrame(main_body, text=" [ 01 // NETWORK RADAR & TARGET DISCOVERY ] ",
                                  bg=COLOR_PANEL, fg=COLOR_GREEN, font=FONT_TITLE, bd=1, relief="solid")
        main_body.add(left_frame, minsize=480)

        # Target Scan Controls
        scan_ctrls = tk.Frame(left_frame, bg=COLOR_PANEL)
        scan_ctrls.pack(fill="x", padx=10, pady=8)

        tk.Label(scan_ctrls, text="SUBNET:", fg=COLOR_TEXT, bg=COLOR_PANEL, font=FONT_BOLD).pack(side="left")
        self.entry_subnet = tk.Entry(scan_ctrls, bg=COLOR_ENTRY_BG, fg=COLOR_GREEN, insertbackground=COLOR_GREEN,
                                     font=FONT_MAIN, width=15, bd=1, relief="solid")
        self.entry_subnet.insert(0, self.subnet_prefix + "x")
        self.entry_subnet.pack(side="left", padx=6)

        self.btn_radar = tk.Button(scan_ctrls, text="📡 RADAR DEEP SCAN", bg="#003d19", fg=COLOR_GREEN,
                                   activebackground="#006622", activeforeground="#ffffff",
                                   font=FONT_BOLD, bd=1, relief="solid", cursor="hand2", command=self.start_radar_scan)
        self.btn_radar.pack(side="left", padx=4)

        self.btn_arp = tk.Button(scan_ctrls, text="⚡ QUICK ARP", bg="#06283b", fg=COLOR_CYAN,
                                 activebackground="#0e4b6c", activeforeground="#ffffff",
                                 font=FONT_BOLD, bd=1, relief="solid", cursor="hand2", command=self.quick_arp_scan)
        self.btn_arp.pack(side="left", padx=4)

        # Filter bar
        filter_frame = tk.Frame(left_frame, bg=COLOR_PANEL)
        filter_frame.pack(fill="x", padx=10, pady=(0, 6))

        tk.Label(filter_frame, text="🔍 FILTER:", fg=COLOR_TEXT, bg=COLOR_PANEL, font=FONT_BOLD).pack(side="left")
        self.entry_filter = tk.Entry(filter_frame, bg=COLOR_ENTRY_BG, fg=COLOR_CYAN, insertbackground=COLOR_CYAN,
                                     font=FONT_MAIN, bd=1, relief="solid")
        self.entry_filter.pack(side="left", fill="x", expand=True, padx=6)
        self.entry_filter.bind("<KeyRelease>", lambda e: self.filter_device_list())

        self.lbl_count = tk.Label(filter_frame, text="HOSTS: 0", fg=COLOR_YELLOW, bg=COLOR_PANEL, font=FONT_BOLD)
        self.lbl_count.pack(side="right", padx=4)

        # Targets Table (Treeview)
        table_frame = tk.Frame(left_frame, bg=COLOR_PANEL)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        columns = ("ip", "hostname", "mac", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Cyber.Treeview")
        self.tree.heading("ip", text="IP ADDRESS")
        self.tree.heading("hostname", text="PC / HOSTNAME")
        self.tree.heading("mac", text="MAC ADDRESS")
        self.tree.heading("status", text="STATUS")

        self.tree.column("ip", width=125, anchor="w")
        self.tree.column("hostname", width=150, anchor="w")
        self.tree.column("mac", width=130, anchor="center")
        self.tree.column("status", width=80, anchor="center")

        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll_y.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_target_selected)

        # Progress bar under table
        self.scan_progress = ttk.Progressbar(left_frame, style="Cyber.Horizontal.TProgressbar", mode="determinate")
        self.scan_progress.pack(fill="x", padx=10, pady=(0, 8))

        # RIGHT PANE: Payload & Transmitter
        right_frame = tk.LabelFrame(main_body, text=" [ 02 // PAYLOAD TRANSMITTER ] ",
                                   bg=COLOR_PANEL, fg=COLOR_CYAN, font=FONT_TITLE, bd=1, relief="solid")
        main_body.add(right_frame, minsize=420)

        # Target IP Entry
        target_box = tk.Frame(right_frame, bg=COLOR_PANEL)
        target_box.pack(fill="x", padx=12, pady=10)

        tk.Label(target_box, text="TARGET IP:", fg=COLOR_GREEN, bg=COLOR_PANEL, font=FONT_BOLD).pack(anchor="w")
        self.entry_target_ip = tk.Entry(target_box, bg=COLOR_ENTRY_BG, fg=COLOR_GREEN, insertbackground=COLOR_GREEN,
                                        font=("Consolas", 12, "bold"), bd=1, relief="solid")
        self.entry_target_ip.pack(fill="x", pady=(4, 0))

        # Display duration
        opts_box = tk.Frame(right_frame, bg=COLOR_PANEL)
        opts_box.pack(fill="x", padx=12, pady=(0, 10))

        tk.Label(opts_box, text="DISPLAY TIMEOUT (SEC):", fg=COLOR_TEXT, bg=COLOR_PANEL, font=FONT_MAIN).pack(side="left")
        self.entry_timeout = tk.Entry(opts_box, bg=COLOR_ENTRY_BG, fg=COLOR_YELLOW, font=FONT_MAIN, width=6, bd=1, relief="solid")
        self.entry_timeout.insert(0, "0")
        self.entry_timeout.pack(side="left", padx=8)
        tk.Label(opts_box, text="(0 = Until dismissed)", fg="#64748b", bg=COLOR_PANEL, font=("Consolas", 8)).pack(side="left")

        # Payload Message Box
        tk.Label(right_frame, text="MESSAGE PAYLOAD (ARABIC / ENGLISH):", fg=COLOR_CYAN, bg=COLOR_PANEL, font=FONT_BOLD).pack(anchor="w", padx=12)

        self.txt_message = tk.Text(right_frame, bg=COLOR_ENTRY_BG, fg="#ffffff", insertbackground=COLOR_GREEN,
                                   font=("Segoe UI", 11), height=6, bd=1, relief="solid", wrap="word")
        self.txt_message.pack(fill="both", expand=True, padx=12, pady=(4, 10))
        self.txt_message.insert("1.0", "طب كنتِ قوليلي")

        # Action Buttons
        btn_frame = tk.Frame(right_frame, bg=COLOR_PANEL)
        btn_frame.pack(fill="x", padx=12, pady=(0, 12))

        # Single Send Button
        self.btn_send_single = tk.Button(
            btn_frame, text="🚀 INJECT PAYLOAD (SINGLE TARGET)",
            bg="#02381b", fg=COLOR_GREEN, activebackground="#056b34", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", pady=8, cursor="hand2", command=self.send_to_single_target
        )
        self.btn_send_single.pack(fill="x", pady=3)

        # Broadcast All Button
        self.btn_broadcast = tk.Button(
            btn_frame, text="💥 MASS BROADCAST (ALL ONLINE HOSTS)",
            bg="#4a0815", fg="#ff4d6d", activebackground="#780e24", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", pady=8, cursor="hand2", command=self.broadcast_to_all
        )
        self.btn_broadcast.pack(fill="x", pady=3)

        # Test Self Button
        btn_test = tk.Button(
            btn_frame, text="🧪 TEST POPUP ON MY SCREEN (SELF-TEST)",
            bg="#111c33", fg=COLOR_CYAN, activebackground="#1e325c", activeforeground="#ffffff",
            font=FONT_MAIN, bd=1, relief="solid", pady=4, cursor="hand2", command=self.test_self
        )
        btn_test.pack(fill="x", pady=3)

        # Launch Cyber Chat Button
        btn_chat = tk.Button(
            btn_frame, text="💬 LAUNCH SECRET P2P LAN CHAT",
            bg="#2e1065", fg="#d8b4fe", activebackground="#4c1d95", activeforeground="#ffffff",
            font=FONT_BOLD, bd=1, relief="solid", pady=5, cursor="hand2", command=self.open_p2p_chat
        )
        btn_chat.pack(fill="x", pady=3)

        # ----------------- BOTTOM CONSOLE LOG -----------------
        console_frame = tk.LabelFrame(self.root, text=" [ 03 // LIVE EVENT & SECURITY CONSOLE ] ",
                                      bg=COLOR_PANEL, fg=COLOR_YELLOW, font=FONT_TITLE, bd=1, relief="solid")
        console_frame.pack(fill="both", expand=False, padx=10, pady=(0, 10))
        console_frame.configure(height=160)

        self.txt_log = tk.Text(console_frame, bg=COLOR_ENTRY_BG, fg=COLOR_GREEN, insertbackground=COLOR_GREEN,
                               font=FONT_LOG, height=7, bd=0, wrap="word")
        log_scroll = ttk.Scrollbar(console_frame, orient="vertical", command=self.txt_log.yview)
        self.txt_log.configure(yscrollcommand=log_scroll.set)

        self.txt_log.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=6)
        log_scroll.pack(side="right", fill="y", padx=(0, 8), pady=6)

        # Text Tags for colorful terminal logs
        self.txt_log.tag_configure("GREEN", foreground=COLOR_GREEN)
        self.txt_log.tag_configure("CYAN", foreground=COLOR_CYAN)
        self.txt_log.tag_configure("YELLOW", foreground=COLOR_YELLOW)
        self.txt_log.tag_configure("RED", foreground=COLOR_RED)
        self.txt_log.tag_configure("DIM", foreground="#64748b")

    # ----------------- LOGGING HELPER -----------------
    def log(self, text, level="GREEN"):
        timestamp = time.strftime("[%H:%M:%S]")
        self.txt_log.insert("end", f"{timestamp} ", "DIM")
        self.txt_log.insert("end", f"{text}\n", level)
        self.txt_log.see("end")

    # ----------------- RADAR SCANNING -----------------
    def quick_arp_scan(self):
        """Instant scan from Windows ARP Cache."""
        self.log("[*] Querying local ARP cache...", "CYAN")
        arp_map = parse_arp_table()
        if not arp_map:
            self.log("[-] No ARP entries found. Run Deep Scan to discover hosts.", "YELLOW")
            return

        self.active_devices = []
        for ip, mac in arp_map.items():
            self.active_devices.append({
                "ip": ip,
                "hostname": "PENDING...",
                "mac": mac,
                "status": "ONLINE 🟢"
            })

        self.render_device_list()
        self.log(f"[✓] Quick scan loaded {len(self.active_devices)} cached hosts.", "GREEN")

        # Resolve hostnames in background
        threading.Thread(target=self._resolve_all_hostnames, daemon=True).start()

    def start_radar_scan(self):
        """Starts multi-threaded fast ping sweep of entire subnet."""
        if self.is_scanning:
            return

        subnet_input = self.entry_subnet.get().strip()
        prefix_match = re.match(r"^(\d+\.\d+\.\d+)\.", subnet_input)
        if prefix_match:
            prefix = prefix_match.group(1) + "."
        else:
            prefix = self.subnet_prefix

        self.is_scanning = True
        self.btn_radar.config(state="disabled", text="📡 SCANNING...")
        self.btn_arp.config(state="disabled")
        self.scan_progress["value"] = 0
        self.log(f"[+] INITIATING RADAR SWEEP ON {prefix}0/24 (254 HOSTS)...", "CYAN")

        threading.Thread(target=self._radar_worker, args=(prefix,), daemon=True).start()

    def _radar_worker(self, prefix):
        found_ips = []
        arp_map = parse_arp_table()

        def ping_test(idx):
            ip = f"{prefix}{idx}"
            # Ping with 1 packet, 150ms timeout
            res = subprocess.run(
                ["ping", "-n", "1", "-w", "150", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return ip if res.returncode == 0 else None

        total = 254
        completed = 0

        with ThreadPoolExecutor(max_workers=60) as executor:
            futures = [executor.submit(ping_test, i) for i in range(1, 255)]
            for fut in futures:
                res = fut.result()
                if res:
                    found_ips.append(res)
                completed += 1
                prog = (completed / total) * 100
                self.root.after(0, lambda p=prog: self.scan_progress.configure(value=p))

        # Re-fetch ARP after pinging
        arp_map = parse_arp_table()

        # Build device list
        new_devices = []
        # Sort by IP last octet numeric value
        def ip_key(ip_str):
            try:
                return int(ip_str.split(".")[-1])
            except:
                return 0

        found_ips.sort(key=ip_key)

        for ip in found_ips:
            mac = arp_map.get(ip, "DYNAMIC")
            new_devices.append({
                "ip": ip,
                "hostname": "RESOLVING...",
                "mac": mac,
                "status": "ONLINE 🟢"
            })

        self.active_devices = new_devices

        def on_complete():
            self.render_device_list()
            self.is_scanning = False
            self.btn_radar.config(state="normal", text="📡 RADAR DEEP SCAN")
            self.btn_arp.config(state="normal")
            self.log(f"[✓] RADAR SCAN COMPLETED: {len(found_ips)} ALIVE HOSTS FOUND!", "GREEN")
            # Start resolving hostnames
            threading.Thread(target=self._resolve_all_hostnames, daemon=True).start()

        self.root.after(0, on_complete)

    def _resolve_all_hostnames(self):
        """Resolves DNS names concurrently for discovered PCs."""
        self.root.after(0, lambda: self.log("[*] Querying DNS / NetBIOS hostnames in background...", "DIM"))

        def resolve_one(dev):
            name = resolve_hostname(dev["ip"])
            dev["hostname"] = name

        with ThreadPoolExecutor(max_workers=25) as ex:
            list(ex.map(resolve_one, self.active_devices))

        self.root.after(0, self.render_device_list)
        self.root.after(0, lambda: self.log("[✓] All hostnames resolved and updated.", "GREEN"))

    # ----------------- TABLE DISPLAY -----------------
    def render_device_list(self):
        query = self.entry_filter.get().strip().lower()
        self.tree.delete(*self.tree.get_children())

        count = 0
        for dev in self.active_devices:
            ip = dev["ip"]
            hostname = dev["hostname"]
            mac = dev["mac"]
            status = dev["status"]

            # Filter check
            if query and (query not in ip.lower() and query not in hostname.lower()):
                continue

            # Special label for self
            if ip == self.local_ip:
                hostname += " (YOU)"

            self.tree.insert("", "end", values=(ip, hostname, mac, status))
            count += 1

        self.lbl_count.config(text=f"HOSTS: {count}")

    def filter_device_list(self):
        self.render_device_list()

    def on_target_selected(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            ip = item["values"][0]
            hostname = item["values"][1]
            self.entry_target_ip.delete(0, "end")
            self.entry_target_ip.insert(0, ip)
            self.log(f"[*] Target locked: {ip} [{hostname}]", "CYAN")

    # ----------------- MESSAGE INJECTION -----------------
    def send_msg_cmd(self, target_ip, message, timeout_val):
        """Executes the Windows msg command with proper arguments."""
        cmd = ["msg"]

        # If sending to remote server
        if target_ip and target_ip != "127.0.0.1" and target_ip != self.local_ip:
            cmd.append(f"/server:{target_ip}")

        # Send to all logged in sessions on target machine
        cmd.append("*")

        # Duration
        if timeout_val > 0:
            cmd.append(f"/TIME:{timeout_val}")

        cmd.append(message)

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=5
            )
            return res.returncode == 0, res.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "Timed out (Target RPC port closed or firewalled)"
        except Exception as e:
            return False, str(e)

    def open_p2p_chat(self):
        """Launches the P2P Cyber Chat room in a new process."""
        script_path = os.path.join(os.path.dirname(__file__), "cyber_chat.py")
        subprocess.Popen([sys.executable, script_path])
        self.log("[+] Initialized P2P LAN Chat node process.", "CYAN")

    def test_self(self):
        """Sends a popup to the local computer screen."""
        msg = self.txt_message.get("1.0", "end").strip()
        if not msg:
            messagebox.showwarning("Empty Message", "Please type a message first!")
            return

        self.log(f"[TEST] Sending test popup locally: \"{msg}\"", "YELLOW")
        threading.Thread(target=self._send_single_worker, args=("127.0.0.1", msg, 0), daemon=True).start()

    def send_to_single_target(self):
        target_ip = self.entry_target_ip.get().strip()
        msg = self.txt_message.get("1.0", "end").strip()
        timeout_str = self.entry_timeout.get().strip()

        try:
            timeout_val = int(timeout_str)
        except ValueError:
            timeout_val = 0

        if not target_ip:
            messagebox.showerror("Missing Target", "Please enter or click a Target IP from the radar list.")
            return
        if not msg:
            messagebox.showerror("Missing Message", "Please enter a message payload.")
            return

        self.log(f"[!] TRANSMITTING PAYLOAD TO: {target_ip}...", "CYAN")
        threading.Thread(target=self._send_single_worker, args=(target_ip, msg, timeout_val), daemon=True).start()

    def _send_single_worker(self, ip, msg, timeout_val):
        ok, err = self.send_msg_cmd(ip, msg, timeout_val)
        if ok:
            self.root.after(0, lambda: self.log(f"[✓] SUCCESS: Payload delivered to {ip}!", "GREEN"))
        else:
            err_msg = err if err else "Connection refused / RPC Error"
            self.root.after(0, lambda: self.log(f"[✕] FAILED on {ip}: {err_msg}", "RED"))
            self.root.after(0, lambda: self.log("    [TIP] Remote PC may need 'AllowRemoteRPC' enabled in registry.", "DIM"))

    def broadcast_to_all(self):
        """Mass broadcast to all online discovered hosts."""
        if self.is_broadcasting:
            return

        if not self.active_devices:
            messagebox.showwarning("Radar Empty", "No online hosts discovered yet! Run [RADAR DEEP SCAN] first.")
            return

        msg = self.txt_message.get("1.0", "end").strip()
        if not msg:
            messagebox.showerror("Missing Message", "Please enter a message to broadcast.")
            return

        timeout_str = self.entry_timeout.get().strip()
        try:
            timeout_val = int(timeout_str)
        except ValueError:
            timeout_val = 0

        # Confirmation alert
        count = len(self.active_devices)
        confirm = messagebox.askyesno(
            "⚠️ CONFIRM MASS BROADCAST",
            f"Are you sure you want to broadcast this popup message to ALL {count} ONLINE PCs on the network?\n\nPayload:\n\"{msg}\""
        )
        if not confirm:
            return

        self.is_broadcasting = True
        self.btn_broadcast.config(state="disabled", text="💥 BROADCASTING...")
        self.btn_send_single.config(state="disabled")

        self.log(f"[⚠️ MASS BROADCAST INITIATED] Target count: {count} machines...", "YELLOW")
        threading.Thread(target=self._broadcast_worker, args=(msg, timeout_val), daemon=True).start()

    def _broadcast_worker(self, msg, timeout_val):
        targets = [dev["ip"] for dev in self.active_devices]
        success_count = 0
        failed_count = 0

        def send_target(ip):
            return ip, self.send_msg_cmd(ip, msg, timeout_val)

        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(send_target, ip) for ip in targets]
            for fut in futures:
                ip, (ok, err) = fut.result()
                if ok:
                    success_count += 1
                    self.root.after(0, lambda ip=ip: self.log(f"  [✓] Delivered -> {ip}", "GREEN"))
                else:
                    failed_count += 1
                    self.root.after(0, lambda ip=ip, e=err: self.log(f"  [✕] Denied -> {ip} ({e[:30]}...)", "DIM"))

        def on_done():
            self.is_broadcasting = False
            self.btn_broadcast.config(state="normal", text="💥 MASS BROADCAST (ALL ONLINE HOSTS)")
            self.btn_send_single.config(state="normal")
            self.log(f"[✓] MASS BROADCAST COMPLETE! Delivered: {success_count} | Denied/Blocked: {failed_count}", "CYAN")

        self.root.after(0, on_done)


if __name__ == "__main__":
    # Ensure Windows DPI awareness for crisp hacker font
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    app = CyberMessengerApp(root)
    root.mainloop()
