# fix_patch.py — repair layer for a.py
# Import BEFORE anything calls a.prelogin / a.processaccount:
#   import fix_patch   # noqa: F401
# The import monkey-patches:
#   • a.get_datadome_cookie  → fresh 5.10.0 payload
#   • a.prelogin             → honest failure reporting (no false "no account")
#   • a.ProxyManager.__init__ → validates every proxy, drops dead ones,
#                               falls back to direct if the pool is empty

import os
import time
import json
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

import a as _engine

log = logging.getLogger("fix_patch")

# =============================================================================
# 1. FRESH DataDome payload (captured 2026-09-20, ddv=5.10.0, jsType=le)
#    When prelogin starts 403-ing again in a few weeks, recapture from
#    Firefox Mobile DevTools and swap the 4 fields below.
# =============================================================================

_FRESH_JSPL = (
    "Bbi2-Cf-KLh0k3a7drf1pyqYmlXbkMK1ItwWzUkrBeha_Q0sXQ1ysG7cyxrwcyL4MP48kMNXe1D7Pbhnt7tXxZNALFj2GyrNZq8MJ5mjuhN644FdzUv_73jF32WiaADneWH9m9QODGvA-6psYjPE0jpMSuywl81Z3JrZimVmVKDwWdcAD7-WHXZQcp1e45oMxwPzyofZfnx-KdAymfmaaggS3NuKsrEE7JZO5QQmmeYhA_lJECWbbyI0n6Z7cIiNGGYJpy06Mr9ODd2YLPOxpjzRaY3C2RQgq27JJKIu2iC-28-O8NHrmdYBsUT3n3-ajcgDyKNMO196LaWBOWmT2qL5zG76sgWweBgkva88-vRn8kIwRIMv3ZaLPn7UGt81U23rD6c6l0rrwzx5PLgl72bl_CMumLk8uiY5rldCkiirZOC0MqSIej5yAYvyYrfsLGVTcYgyWyENTAo9IeGzFJa1HUgJ1q5n8NOFytrMY85EAM0W0C5eZqsXeMtQltg4leRGfUsqtTvEU8daHzidSiStjv9d92KtH17cgZBSmSgro5rZanjTMbl9flXbvtBjm4xPb_y3NR_NmMwajP1j0tzMgWQotsZWVdR02gGd0lEv9D0brqv6nJ2ygwGPOr9NPvXSn7p7wTpVTyDwKTn1krFeiKs9RvHH-WDT_HAl_FinannAUfpjfppSBU-y7YNXTCvI-BX_jgGPKFuKSqAUy3Fu7OPUIHOQKzg4hAcIrxbYGLPQKY1UjdXwS33OxmD3hs6vISeYgKN12tlK_4mASEutKFCDBimBWezbvmtXSTkEWK28iOH-qsbrEg_V2QbmbKEZT_rLGTcHi06y_VaXjuLBPSR8gJyiCbO1_sO0pQVT55BHjvsxhzAew-iwrRp5YDdIcqAn4rZCjD-96-Kj_6xgJ8cXnG6uuFa-qRDbXF86XJmYGHyC47ZjGckaVP2wd1Z7koRA_tTPpzH0uZ7uAdwRd5nP3qv0ygu5-7HotDWuvWkKnY6DDTmB0wJjdiz1yk_rGLJbz6hLyjNTlYaZkxtuBJ48dJhUrscfU_lXfYQFvOH-yxweX0K_I_lME_vnjgdLAjW7gEOdwOWuFafMs8KdpsV2AeusRKCuZGJNZl8U-haRGKlBIBte-0kBiVaroye60o_feTtCrZ568xyuECBnjdIVNTLvXMem4X9gw7Ef7QO_GDLvWYF8igi5RuDjONDdMLYXagcuf9EWJR-EG7VvltD5UDDlmiG_swMA3uUWiRiYPwPF2Zx5cI6LV9VWZsZoFB2h3qXS8fHFAJJEwcDA8Xg430hFMcIfKZhZKEG_pkNaDWzeeuzrFcKUvhzR3C5hJ1ha3aAMmtGlRLzdMiH4AUdwoGDkrI_JO6erzt8_EzSP9cVJDTa43rcQKZT-nHbo52cc5sXcm75BwO8AUJbBiugJy8-lpDptvfV50u6iFdzf5AFbOJ8mO9oD0nE6vhhrFIcJ6Gx51XjfH-qKs0He1hnFK6rFN4QLbqCmEvkMn-oohbNTTJc2xxzQCYqRsoT_4UqGRwmBo4bB0FZjXErIxeF3noj43WHQXk8ZThAje_ZUPBz2dsyv_udzbkWgZbb4fyJZRMlO7rPDZ5t3qEoEB6UKjl-d3b5Q6ynrk7Gg6Xr2clwDd8SPd6gfEXvtPvpcd7WM0xHYynYnBb_YzNwqwmuLFLSa2lCcztNwbUxCxf8XNBD1YouxcL4t80UFFWWEBx9D9u3czkja-sK9fwdLO_vCBaodJ-DDPCuph0OhSjri6zGNsFlviUZTz236Gn360LF2wFhzrEfjUh0eHn1fk8mD4vUUKb-dgaOT-DmZVcV9-i-3KKvK_2jBbAGoB9MMwauVikyMow9IAhNK4iT1FRj6y88RKMcC3HeR5OamrRS1lJQwRKzT7PVUEnEz87i0goY6iP425JF_I8e2rCMakbSDfoUL3skViQ1DIUWy1OIx05DOo6_Ve7NQusrt-urFXpNo27twO9ec65fofXPEjQiHcym80JDyNvwHpdaVQW2fS9qAsD_FDCMFdbAuAfEVr8AWetChRh4TXs7w6WHF6se8dnU3g4VD2ULnppwxTJmiU8YhRNQafbtnkCYHHpMo7txDf-XSI5KleVVhoqoCQwhz6qPwbyYV3D8kuKxcg3LD4SoTSajdVOsPbM-R_R6C3uvsVvDpTS_HaSOygvziiwOsbSpwS7uLeIEIrgr4W-FczZ78Sk7P1Xnr3FbPoVnul7h3foUxxYCoy2C6KGGEts1i_Pvor9JRxz5_O-sLVVTyOsqOYxU7zyXpXX1yVNHpIndyGQCOm9q8YGcLOJU9c4wTuxpOHoL5_hUagN7uTY7TbZCMKGmoBffVE9MfPaUrgWA3VGmcpdeciI0GSbEDnVypdZsj1Oc79hEHAEBM4moK0nBW0BeZPoI-y2e6zKa--yqMBtgvZvKX2paBV1bnTZ1bCmArBKpHMgMdC8w31nz9J_OKtGGsgwQ_Ufww4BN2syRnmvBAeXY4Mz2eax8XcFksgqXRsKdnRnndPFycZKzM2yCvJulJ1PxwVNJEfSp8LIFYkPhqeGg9hXfYICSKmG4_YFWUufACnTFQHMWs-nPzN2T-JREhxdxHWi4luuiXHyc4FDwOM_sXk7zqrUbzJlN7N6MCLL_vABRfOHRgnY9XZmE7zGXnyMtng3UISs5G-U6FSKxgFoY2K5AGAQatdvnW84Mq3FoBbPJ8YBuSnudsi3eCh7dIzF0AFYhBXdcqlBORVvmv6rbXz3xA7-m2Qp2tu38RmtJr_Vt7_XI2lw589sm1dH57pFsNynkUK73ZffpASiiWxLpzve3TKl7uKj6veAjLitpJWIzDjQ-VdZBC23BnKqhSjduNnK4muCOp63Su-UF9UXf3QCA2MKvQG0SoO_qtur_pxzHdU0JwoY2doTDVJHIVXGPz_Ev_WIdboCB2KTKJ2gRSonpznAqdCskWyIOq_2JThSAvMR9JBEVj7rmKERQ2J9wM_nhaDRPr7R--uArd0a3LiLnD6FNUuDj4zHGFJIoegdRLTspTy6a2x8e4vfQQkREUpxj0LHgoKeggNZvvHk_3r44-n3bHuFhuZ0h5WhSePCFmpMH2vxkbGguOQu_O6lFXP1zkRjTTTqEGjsAMku7SYFW33SnpfXBz6Ncnrud3LzE8cLc14GLybVZt4Jpd8VEAQGNdz87SVEZdv15M4y6LUPi31-bllbBoHsqruOb-BhgeGR13pAQtpAVW0364BYAMpo9merrnpPc_y1vbzAUE1B_93GEtsWJn-XqxPZ7xBm1Bz50PLir7lH5UJ01v1TGpw9BtD-SOzkyw6rMvnB9II7v1Qz2Mx_wF05cKKECKSjibRtra8wMZtozasabX1ILHuY0ME2r46sSj54OCrns8XuNjAUOVNvvLCtxhDmV-HfpckPm4GJr4zVkVndRfaVRAeJKaQ6_2StWfJtG-rsI5IDDxTIuJrwj55NDo8Sr3ZAsZ09QGVvugCRJDyzuaXewTEguTepEDezLooPcs-s5KDSpSuhVWyXMDWdN0rmvEVhD2NA9gygd96cU7C5J-DwPrrlmvlhA3En5jDbEixmniqnOBl9ZMooldokLVBT1_A2AvQmb8LeY5RHPBiJicLyEAXwXu4QXhR9YypPUdVhxwTH_nTpbsNDFlhiEMjWuZfC5aot7NbFJVo-dxkCky1J4tYsnCaHdbEEoBrdHcUNHB57vpP0PL2gkJiRFglIeo_w2zJ0-Y-JmzEjgiExnBeUaeBN5cVp0w8IiXZW2BRMlt1TPISDdkyNWR1xYNp_P1juSMz9z2KeZjj7H3djWrUQmTSwc9DiyGSuJgZsBwO-kuAqPoGfctmqyMfKL3eVjQGFgevEgoH_esilk4k8ii2q4H3C2FAm0vosuWh0DQtCgiQUZeYizz59M5cZ7zcgUIxPx0qxj5PmX6WjNa4ndcIDzsgiPMB9MHHyxaA4OeIMxGXacm3xrX12ImnH-RntfIkgrcS7m8Xh-snVlrw9mdusCCHLKi9FnBJASo9NRekMX06UvweTq09sVj9lw8QghH5wOc9dAJkUuYPrWp4NtHDtoQLRnJRk_jkoeVdaqoiRvbmFg2oS7JBGVRc3XT3k8rfZCnyNCZyOJh6H4FWc6ZJ7I21TApe8cSjajyOJ1HpVzpGsC0UQVEuakx2iltkCsLE2VrqsTYgh87WxPj8W4wcSo3UtFTLkp_VtKQwxS_6ruN4ifm0H1OmN7QT0EXlBhosGgn_n1kyi_yYOhFBmtsowYdi3hry8XmQXlXKYQaV3So2svg0uhAVO95pykB4ivuKg482pFxtI2wHuvKtSwXz9FA__ZMVCislznVeObTkJZcTIJS9RkSC3hKBrMgx13k6ZZwAgrGdSKrjKNcxP9_KVGEmH6-6ZaXz46ICIOi74ddlvYJTrpaPJLt3sg_q7AR7TnPtLhXUtFvm35MGXCWP2fKj5Iycz9PBgC9w1zhZsVD2eyq5uskQeyLoHbULJSWdWYxtMzW2NUR0jmF3n6gUblBGwEdq8UM64X2CR0zZlfkNT1n7u8m3Yi4a_QvI6dAImOu7enjXRiylthQZKVWOclgOrDNduIGW_hjb-XpidPC6t86Saf0tAmPKy9gWLB8mGkeCyDbfPNX4M3qxBq0QNk3qb1u6KTRfSbqtQQHneMzM4QSrr_pqJw_lsuzQdrlwIq5zPR4O7BCFaCctn3rAfaDjSzAc6S6nOD_rPsAB2hN8o7ifJIeyqwHarl4hF_YNlOXk-x7-LknITlap6YSt9Z2K6NYJiZetyw3ZJXAmiDjxWEX-dxQNv1VL2JXl3V7AGlf_Rc1daeyx8Sk0UDxmLlVDqmVePHGtNpBLmnQUyTwboqYuMFmevKosew2gfLxzj8kcPHOvghBGrsPlkH3egs2VS6EchcoiUs2EBSzvvOI6MD-j0hiUnJUN5DadtWNwOIVWYlBobSrguijrpjC4VGP0GB2Q6PS3Khd4DrHKd2XCTrXei5hDNEXeen6_N0hyvF_F9sxmQsfWN1FDgVJy41eOb596OsaabTK4lq-Pdy_rMEA0HbUyXKQq6VAQ8juHQUlRWLFMai-urER5irWl7EeRq7ytpE9dVk3Bvbx2os9AAqVtH7tF4GmTsmQ-BBopniTGktKxXRqjMelRXAlgd6Yvtp4iedAqAGpqS4XaX7ALEbTM9m-9nBqSOEWuVr-Tw6m6qZh5-j5A9zyK--WLPtdH6M_2VTmCQOBfkhw4NewvMVAo992LK-ZcIw4vBV20Jnq-O_8s_f70FP3yrURkxqaSpK-NozAvwOJ-X_ELiEZlCuhoOuGB3ctCOdDuczmBzxOZUGFXTVJvlwwYUt675jrRxQYs4fn34Bea2TXjftT2Qaa3iFIPv68vrdlxQ3AbyuyabmbIDlFgI3b8N0R7GjvVLE6qwxDUfRwKzG9Lvij2a6BaNrr4wFfq0163NxuyoC8dXNy8adKk-eZ_xmnTQXqx6KqL185oFPL_nu6vw7BQRHdk9EvH_CTqElACfqdhC3m4FWW9lnJBeqoVWLU6paaRnOHLejYZMGzqmXzahCwBUVxiYaGL3gNGQIiads8S6ueT3ChHuZJRTY2zaXGiwxBuFbpQneijuKX8HyOjUoNFhjTa-Truy0hosBFUObOHowRPS07zy8kLH7cbIs75BBcE6vCW2B02c5RLorr1DsXXkS-njPUTqNVvKKX6iG7FRyrzIIEsd5Qdl7KrqJ5ej5HUszxfI1H8-bZ4_j6FdevryJsD_yUOZg5X77mSqrazRhEPTbeH7ixm7RNUkts9Nc9CktcBBzbo4Ry6DtwpE1PsZgdc37Ta9VyN8oSbQQLGtCMmk2F--osGSKMhRrcS76BmTls14W6M8ypgkEfB4tBH5fSablNW3ORl-gZTlccQrWvN8elggbPKmheAcwgD5M7oc-R1O6_yVBkk0jptCI3JOIPmAzlHNhTCkt13EWJPxu8aTRwg1SvfvDPjmqKTa-NgLzlLyDTR4bWlabo8aZ_13onR-3VLMCipZ7xS8gCg7ffCNNAcWyjT9-1NpuoF7J1SX2O_D_ygv4ZWlUebuhGmFw_UQGbsc2Rujog-FsSGsYEpItOlqaQNmsuegvdTzaJvCheK-gLMga7rwQbI20Zzb5_vaVrCauQl4SG9n3BAz4PqrK-24bx6PxdL7FMxr9QiOOpfze8iha3lN-1W7d4rOMiAq989VgczzEWV0o0W-gOiZ__3cQINLHK1RctqwWiQqXfSHI58y-3Hkw_J5aU4mKisnF0noe96vnBVc1hBrkwph4rVFf6Zh5pqDmHHFlxLHAiKP1pdty7G5vHbQAiU8wMgYXwlp7ZN1LdV2dGuGFEtm3IgHgFzJCSLgW-qG4a48hrkYRR5Asg4gxkjlxX-QhQ9sxJMYKIDu_51Z9v76adupursLa0tCG5a0Hwzvsphiiq3NMsLI1y6X7eVNuFtwzIVxezwRWJN8ihbEcc7EOEGRJmKbsVx2dTeO8FQ4n09xNzUOz4yApJjXsPP0M9QgpVPtfscZHe74q_F83GzAn2HH7arASrZEx91tUirUITspKMoEmeG2J-RYsD9DvWFd3-F8T1T3T2JqrBaQOwzkB9ZqKLy0YmMFnpwpzY5IiD_H2KHzoATHrgZ3_IiP9oaSLCTKPhZf5kEe2f446l4CRAYkger_vO-p_Oki07k6bewIOqhfbQsL9gGvTq-4E3Culmlh4SCGRUP6Hl8zDav2kIz9V6w1tVkW5muWCEOJZxLLlW9OXKzY7rXvm3p7d19hjRw_Zuke4npG7aDp5czTU3FzL23yNu6bSy13dC8ZOEY7no72XD4886fFn8GoognBo4Ucjy7WGvuUyr_hDculcfZbctiZM0czfNAfZhb50r59DOj2s7HrbHNn9TraE2PxEGeLt4ICLUY1tlu4MJn1vEgln6UT5lYW_qUzTDtIqNZyfEhKKdZ5-1lmYk0clloZglxhc3RJCEM_SuCA6juVTPNqsTagxZ776PnK-04WtC3SpaCddxIpiPiQQ"
)

_FRESH_CID = (
    "RYqucyB~MVQeldXTh4wb04zZ91NafuvoLrjRGBDDWyjZNm1KGdEB3GUKBlvEEt2njo7m55"
    "~RC~Vj2qxBmKs1nDuZvGEqi2Agi12suHFpU4HVLmJl6LkOFxyztGUfPXRJ"
)

_FRESH_EVENT_COUNTERS = (
    '{"mousemove":4,"pointermove":1,"click":4,"scroll":0,'
    '"touchstart":5,"touchend":4,"touchcancel":1,"touchmove":2,'
    '"keydown":0,"keyup":0}'
)

_REFERER_VALUE = (
    "https%3A%2F%2Fsso.garena.com%2Funiversal%2Flogin%3Fapp_id%3D10100"
    "%26redirect_uri%3Dhttps%253A%252F%252Faccount.garena.com%252F"
    "%26locale%3Den-SG"
)
_REQUEST_VALUE = (
    "%2Funiversal%2Flogin%3Fapp_id%3D10100%26redirect_uri%3Dhttps%253A"
    "%252F%252Faccount.garena.com%252F%26locale%3Den-SG"
)


def get_datadome_cookie_v2(session, proxies=None):
    """Fresh DataDome fetch matching the 2026-09-20 Firefox capture."""
    url = "https://datadome.garena.com/js/"

    headers = {
        "Host": "datadome.garena.com",
        "User-Agent": "Mozilla/5.0 (Android 12; Mobile; rv:156.0) Gecko/156.0 Firefox/156.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://sso.garena.com",
        "Referer": "https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=en-SG",
        "Connection": "keep-alive",
    }

    payload = {
        "jspl": _FRESH_JSPL,
        "eventCounters": _FRESH_EVENT_COUNTERS,
        "jsType": "le",
        "cid": _FRESH_CID,
        "ddk": "AE3F04AD3F0D3A462481A337485081",
        "Referer": _REFERER_VALUE,
        "request": _REQUEST_VALUE,
        "responsePage": "origin",
        "ddv": "5.10.0",
    }

    try:
        r = session.post(url, headers=headers, data=payload,
                         proxies=proxies, timeout=20)
        log.info("[datadome] status=%d len=%d",
                 r.status_code, len(r.content or b""))
        if r.status_code == 200:
            try:
                data = r.json()
                cookie_value = data.get("cookie") or data.get("cookieValue")
                if cookie_value:
                    if "datadome=" in cookie_value:
                        return cookie_value.split("datadome=")[1].split(";")[0].strip()
                    return cookie_value.split(";")[0].strip()
            except Exception as e:
                log.warning("[datadome] json parse failed: %r", e)
            if "datadome" in r.cookies:
                return r.cookies["datadome"]
        else:
            log.warning("[datadome] non-200 body: %r", (r.text or "")[:200])
    except Exception as e:
        log.warning("[datadome] exception: %r", e)
    return None


_engine.get_datadome_cookie = get_datadome_cookie_v2
log.info("fix_patch: a.get_datadome_cookie replaced with 5.10.0 payload")


# =============================================================================
# 2. HONEST PRELOGIN — never says "Account Doesn't Exist" for infra failures
# =============================================================================

class PreloginFailure(Exception):
    def __init__(self, status):
        self.status = status
        super().__init__(f"PRELOGIN_{status.upper()}")


def prelogin_v2(session, account, datadome_manager, cookie_manager,
                retries=3, proxy_manager=None):
    all_403 = True
    last_status = "unknown"

    for attempt in range(retries):
        try:
            url = "https://sso.garena.com/api/prelogin"
            params = {
                "app_id": "10100", "account": account,
                "format": "json", "id": str(int(time.time() * 1000)),
            }
            current = session.cookies.get_dict()
            parts = [f"{n}={current[n]}" for n in
                     ["apple_state_key", "datadome", "sso_key", "_ga",
                      "_ga_XB5PSHEQB4", "_ga_1M7M9L6VPX"] if n in current]
            cookie_header = "; ".join(parts) if parts else ""

            headers = {
                "Host": "sso.garena.com",
                "Connection": "keep-alive",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Android 12; Mobile; rv:156.0) Gecko/156.0 Firefox/156.0",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=en-SG",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
            }
            if cookie_header:
                headers["Cookie"] = cookie_header

            r = session.get(url, headers=headers, params=params, timeout=30)
            log.info("[prelogin] try=%d status=%d len=%d",
                     attempt + 1, r.status_code, len(r.content or b""))

            if r.status_code == 403:
                proxy_dict = (dict(session.proxies)
                              if getattr(session, "proxies", None) else None)
                fresh = _engine.get_datadome_cookie(session, proxies=proxy_dict)
                if fresh:
                    datadome_manager.set_datadome(fresh)
                    datadome_manager.set_session_datadome(session, fresh)
                else:
                    datadome_manager.handle_403(session)
                if attempt < retries - 1:
                    time.sleep(1); continue
                all_403 = True; last_status = "ip_blocked"; break

            if r.status_code == 429:
                last_status = "rate_limited"
                time.sleep(3); continue

            r.raise_for_status()
            all_403 = False

            try:
                data = r.json()
            except json.JSONDecodeError:
                last_status = "server"
                log.warning("[prelogin] non-json: %r", (r.text or "")[:200])
                if attempt < retries - 1:
                    time.sleep(2); continue
                break

            new_cookies = r.cookies.get_dict()
            new_dd = new_cookies.get("datadome")
            if new_dd:
                datadome_manager.set_datadome(new_dd)

            log.info("[prelogin] json keys=%s", list(data.keys()))

            if "error" in data:
                err = str(data.get("error", "")).upper()
                has_dd = bool(session.cookies.get("datadome"))
                if "ACCOUNT" in err and ("EXIST" in err or "NOT" in err):
                    if has_dd:
                        last_status = "no_account"
                    else:
                        last_status = "server"
                        if attempt < retries - 1:
                            fresh = _engine.get_datadome_cookie(session)
                            if fresh:
                                datadome_manager.set_datadome(fresh)
                                datadome_manager.set_session_datadome(session, fresh)
                            time.sleep(1); continue
                else:
                    last_status = "server"
                if attempt < retries - 1 and last_status == "server":
                    time.sleep(1); continue
                break

            v1, v2 = data.get("v1"), data.get("v2")
            if not v1 or not v2:
                last_status = "server"
                log.warning("[prelogin] no v1/v2 in response: %s",
                            {k: str(v)[:30] for k, v in data.items()})
                if attempt < retries - 1:
                    time.sleep(1); continue
                break

            return (v1, v2, new_dd)

        except requests.exceptions.ConnectionError:
            all_403 = False; last_status = "network"
            if proxy_manager and proxy_manager.is_loaded():
                session.proxies.clear()
                session.proxies.update(proxy_manager.get_next())
            if attempt < retries - 1:
                time.sleep(2); continue
        except requests.exceptions.Timeout:
            all_403 = False; last_status = "network"
            if attempt < retries - 1:
                time.sleep(0.5); continue
        except Exception as e:
            all_403 = False; last_status = "server"
            log.warning("[prelogin] exc: %r", e)
            if attempt < retries - 1:
                time.sleep(1); continue

    if all_403:
        return ("IP_BLOCKED", None, None)
    if last_status == "no_account":
        return (None, None, None)
    raise PreloginFailure(last_status)


_engine.prelogin = prelogin_v2
log.info("fix_patch: a.prelogin replaced (honest reporting)")


# =============================================================================
# 3. PROXY VALIDATION — drop dead proxies at load, fall back to direct if empty
# =============================================================================

def _install_proxy_validation():
    """Monkeypatch a.ProxyManager.__init__ to validate every proxy once."""
    _orig_init = _engine.ProxyManager.__init__

    def _check(p):
        try:
            r = requests.get(
                "https://api.ipify.org",
                proxies=p,
                timeout=4,
            )
            return p if r.status_code == 200 else None
        except Exception:
            return None

    def _new_init(self, proxy_file="proxies.txt"):
        _orig_init(self, proxy_file=proxy_file)

        # Env kill-switch: DISABLE_PROXIES=1 → run direct, skip validation.
        if os.getenv("DISABLE_PROXIES", "").lower() in ("1", "true", "yes"):
            self.proxies = []
            log.warning("[proxy] DISABLE_PROXIES=1 — running direct, no proxies")
            return

        if not self.proxies:
            log.info("[proxy] no proxies to validate")
            return

        total = len(self.proxies)
        log.info("[proxy] validating %d proxies (4s timeout, 100 workers)…", total)

        valid = []
        with ThreadPoolExecutor(max_workers=100) as ex:
            futs = {ex.submit(_check, p): p for p in self.proxies}
            for f in as_completed(futs):
                try:
                    v = f.result()
                    if v:
                        valid.append(v)
                except Exception:
                    pass

        self.proxies = valid
        log.info("[proxy] %d/%d alive after validation", len(valid), total)

        if not valid:
            log.warning("[proxy] ZERO alive — running direct. Get fresh proxies.")

    _engine.ProxyManager.__init__ = _new_init
    log.info("fix_patch: proxy validation installed")


_install_proxy_validation()

print("[fix_patch] a.py patched — DataDome 5.10.0, honest prelogin, "
      "proxy validation, direct fallback.")
