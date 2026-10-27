# -*- coding: utf-8 -*-
"""
CYBER-LAN DATABASE MANAGER (SQLite) - v3.1
Handles persistent storage for messages, user profiles, favorite stickers,
groups, ephemeral stories, weekend-aware streaks, and milestone analytics.
"""

import os
import sqlite3
import json
import datetime
from datetime import datetime as dt, date, timedelta

DB_FILE = os.path.join(os.path.dirname(__file__), "cyber_lan.db")
ADMIN_IP = "192.168.20.54"


class DatabaseManager:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cur = conn.cursor()

            # 1. User Profile & Local Settings
            cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """)

            # 2. Messages (Public, Private, Group)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                msg_uuid TEXT UNIQUE,
                sender_ip TEXT,
                sender_nick TEXT,
                target_type TEXT, -- 'PUBLIC', 'PRIVATE', 'GROUP'
                target_id TEXT,   -- 'ALL', peer_ip, or group_id
                content TEXT,
                msg_type TEXT,    -- 'TEXT', 'FILE', 'STICKER', 'GAME'
                file_meta TEXT,   -- JSON metadata for files/media
                reply_to TEXT,
                timestamp TEXT,
                is_me INTEGER DEFAULT 0
            )
            """)

            # 3. Groups (Admin is mandatory member)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                group_id TEXT PRIMARY KEY,
                group_name TEXT,
                creator_ip TEXT,
                description TEXT,
                created_at TEXT
            )
            """)

            # 4. Stickers & Favorites
            cur.execute("""
            CREATE TABLE IF NOT EXISTS stickers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                symbol TEXT,
                image_path TEXT,
                is_favorite INTEGER DEFAULT 1,
                created_at TEXT
            )
            """)

            # 5. Stories (24h ephemeral updates)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS stories (
                story_id TEXT PRIMARY KEY,
                author_ip TEXT,
                author_nick TEXT,
                content_text TEXT,
                media_path TEXT,
                created_at TEXT,
                expires_at TEXT
            )
            """)

            # 6. Streaks (Public, Private pairs, Groups)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS streaks (
                streak_id TEXT PRIMARY KEY,
                streak_type TEXT,
                target_id TEXT,
                count INTEGER DEFAULT 1,
                last_interaction TEXT
            )
            """)

            conn.commit()

        self._seed_default_stickers()

    def _seed_default_stickers(self):
        defaults = [
            ("Cyber Skull", "💀", "cyber_skull"),
            ("Matrix Hacker", "🕶️", "matrix_neo"),
            ("Fire Streak", "🔥", "fire_streak"),
            ("Party Popper", "🎉", "party_cyber"),
            ("Alien Node", "👾", "alien_node"),
            ("Cyber Crown", "👑", "cyber_crown"),
            ("Warning Alert", "⚠️", "warning_node"),
            ("Robot Brain", "🤖", "robot_brain"),
            ("Rocket Payload", "🚀", "rocket_payload"),
            ("Ghost Stealth", "👻", "ghost_stealth"),
            ("Lock Secured", "🔒", "lock_cipher"),
            ("Laser Eye", "👁️", "laser_eye")
        ]
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as cnt FROM stickers")
            if cur.fetchone()["cnt"] == 0:
                now = dt.now().isoformat()
                for name, sym, img in defaults:
                    cur.execute(
                        "INSERT INTO stickers (name, symbol, image_path, is_favorite, created_at) VALUES (?, ?, ?, 1, ?)",
                        (name, sym, img, now)
                    )
                conn.commit()

    # --- Profile & Settings Methods ---
    def get_setting(self, key, default=None):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cur.fetchone()
            return row["value"] if row else default

    def set_setting(self, key, value):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()

    def get_profile(self, default_ip, default_host):
        nick = self.get_setting("user_nickname", default_host)
        avatar = self.get_setting("user_avatar", "⚡")
        bio = self.get_setting("user_bio", "Cyber Operator // LAN Node")
        return {"ip": default_ip, "nickname": nick, "avatar": avatar, "bio": bio}

    def save_profile(self, nickname, avatar, bio):
        self.set_setting("user_nickname", nickname)
        self.set_setting("user_avatar", avatar)
        self.set_setting("user_bio", bio)

    # --- Messages Methods (Limited to 50) ---
    def save_message(self, msg_uuid, sender_ip, sender_nick, target_type, target_id,
                     content, msg_type="TEXT", file_meta=None, reply_to=None, timestamp=None, is_me=0):
        if not timestamp:
            timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        if file_meta and not isinstance(file_meta, str):
            file_meta = json.dumps(file_meta)

        with self.get_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute("""
                INSERT OR IGNORE INTO messages
                (msg_uuid, sender_ip, sender_nick, target_type, target_id, content, msg_type, file_meta, reply_to, timestamp, is_me)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (msg_uuid, sender_ip, sender_nick, target_type, target_id, content, msg_type, file_meta, reply_to, timestamp, is_me))
                conn.commit()
            except Exception:
                pass

    def get_messages(self, target_type, target_id, limit=50):
        """Returns the most recent 50 messages."""
        with self.get_connection() as conn:
            cur = conn.cursor()
            if target_type == "PUBLIC":
                cur.execute("""
                SELECT * FROM (
                    SELECT * FROM messages
                    WHERE target_type = 'PUBLIC'
                    ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
                """, (limit,))
            elif target_type == "PRIVATE":
                cur.execute("""
                SELECT * FROM (
                    SELECT * FROM messages
                    WHERE target_type = 'PRIVATE' AND (target_id = ? OR sender_ip = ?)
                    ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
                """, (target_id, target_id, limit))
            elif target_type == "GROUP":
                cur.execute("""
                SELECT * FROM (
                    SELECT * FROM messages
                    WHERE target_type = 'GROUP' AND target_id = ?
                    ORDER BY id DESC LIMIT ?
                ) ORDER BY id ASC
                """, (target_id, limit))
            return [dict(r) for r in cur.fetchall()]

    def get_total_messages_count(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) as cnt FROM messages")
            row = cur.fetchone()
            return row["cnt"] if row else 0

    def clear_public_messages(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM messages WHERE target_type = 'PUBLIC'")
            conn.commit()

    # --- Stickers Methods ---
    def get_favorite_stickers(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM stickers WHERE is_favorite = 1 ORDER BY id DESC")
            return [dict(r) for r in cur.fetchall()]

    def add_favorite_sticker(self, name, symbol, image_path=""):
        with self.get_connection() as conn:
            cur = conn.cursor()
            now = dt.now().isoformat()
            cur.execute(
                "INSERT INTO stickers (name, symbol, image_path, is_favorite, created_at) VALUES (?, ?, ?, 1, ?)",
                (name, symbol, image_path, now)
            )
            conn.commit()

    # --- Groups Methods (Mandatory Admin Membership) ---
    def create_group(self, group_id, group_name, creator_ip, description=""):
        with self.get_connection() as conn:
            cur = conn.cursor()
            now = dt.now().strftime("%Y-%m-%d %H:%M:%S")
            desc = f"{description} [Mandatory Admin: {ADMIN_IP}]"
            cur.execute("""
            INSERT OR REPLACE INTO groups (group_id, group_name, creator_ip, description, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (group_id, group_name, creator_ip, desc, now))
            conn.commit()

    def get_groups(self):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM groups ORDER BY created_at DESC")
            return [dict(r) for r in cur.fetchall()]

    # --- Stories Methods ---
    def post_story(self, story_id, author_ip, author_nick, content_text, media_path=""):
        now = dt.now()
        expires = now + timedelta(hours=24)
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            INSERT OR REPLACE INTO stories (story_id, author_ip, author_nick, content_text, media_path, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (story_id, author_ip, author_nick, content_text, media_path, now.isoformat(), expires.isoformat()))
            conn.commit()

    def get_active_stories(self):
        now_str = dt.now().isoformat()
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
            SELECT * FROM stories
            WHERE expires_at > ?
            ORDER BY created_at DESC
            """, (now_str,))
            return [dict(r) for r in cur.fetchall()]

    def delete_story(self, story_id):
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM stories WHERE story_id = ?", (story_id,))
            conn.commit()

    # --- Streaks Methods (Weekend-Aware + Milestones at 3 & 10) ---
    def record_streak_interaction(self, streak_type, target_id):
        """
        Updates streak count according to 24h rule,
        with Friday (4) and Saturday (5) exempted from streak breaks.
        Returns: (new_count, is_milestone)
        """
        streak_id = f"{streak_type}:{target_id}"
        now = dt.now()
        now_iso = now.isoformat()
        today = now.date()

        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM streaks WHERE streak_id = ?", (streak_id,))
            row = cur.fetchone()

            if not row:
                cur.execute(
                    "INSERT INTO streaks (streak_id, streak_type, target_id, count, last_interaction) VALUES (?, ?, ?, 1, ?)",
                    (streak_id, streak_type, target_id, now_iso)
                )
                conn.commit()
                return 1, False

            last_dt = dt.fromisoformat(row["last_interaction"])
            last_date = last_dt.date()
            current_count = row["count"]

            if today == last_date:
                cur.execute("UPDATE streaks SET last_interaction = ? WHERE streak_id = ?", (now_iso, streak_id))
                conn.commit()
                return current_count, False

            days_diff = (today - last_date).days
            if days_diff == 1:
                new_count = current_count + 1
            else:
                all_weekend = True
                check_date = last_date + timedelta(days=1)
                while check_date < today:
                    if check_date.weekday() not in (4, 5):
                        all_weekend = False
                        break
                    check_date += timedelta(days=1)

                if all_weekend:
                    new_count = current_count + 1
                else:
                    new_count = 1

            cur.execute(
                "UPDATE streaks SET count = ?, last_interaction = ? WHERE streak_id = ?",
                (new_count, now_iso, streak_id)
            )
            conn.commit()

            # Milestones: 3, 10, 20, 30, etc.
            is_milestone = (new_count in (3, 10) or (new_count > 10 and new_count % 10 == 0))
            return new_count, is_milestone

    def get_streak_status(self, streak_type, target_id):
        """
        Returns (count, hours_left, is_warning_4h, is_weekend_frozen)
        """
        streak_id = f"{streak_type}:{target_id}"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM streaks WHERE streak_id = ?", (streak_id,))
            row = cur.fetchone()
            if not row:
                return 0, 24, False, False

            count = row["count"]
            last_dt = dt.fromisoformat(row["last_interaction"])
            now = dt.now()

            # Check if today is Friday (4) or Saturday (5) -> Frozen!
            if now.weekday() in (4, 5):
                return count, 24, False, True

            elapsed_hours = (now - last_dt).total_seconds() / 3600.0
            hours_left = max(0.0, 24.0 - elapsed_hours)
            is_warning_4h = (hours_left <= 4.0 and hours_left > 0.0)
            return count, round(hours_left, 1), is_warning_4h, False
