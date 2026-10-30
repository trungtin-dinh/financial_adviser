"""Browser-level smoke check against the public Streamlit deployment.

The Streamlit Community Cloud authentication handshake requires a real browser
(cookie + JS), so raw urllib/curl redirects are not a reliable uptime signal.
Run with: python tests/live_browser_smoke.py
"""
from __future__ import annotations

from pathlib import Path
import os
import re
import time

from playwright.sync_api import sync_playwright

BASE = os.environ.get("APP_URL", "https://financial-adviser.streamlit.app").rstrip("/")
OUT = Path("artifacts/live")
OUT.mkdir(parents=True, exist_ok=True)


def load_app(browser, lang: str, viewport: dict, expected: str):
    context = browser.new_context(viewport=viewport)
    page = context.new_page()
    page.set_default_timeout(20000)
    page.goto(f"{BASE}/?lang={lang}", wait_until="domcontentloaded", timeout=90000)
    for attempt in range(3):
        try:
            page.get_by_text(expected, exact=True).first.wait_for(timeout=60000)
            return context, page
        except Exception:
            # An idle Community Cloud app may expose a wake-up button.
            wake = page.get_by_role("button", name=re.compile(r"get this app back up|wake|restart", re.I))
            if wake.count():
                wake.first.click(timeout=10000)
                page.wait_for_timeout(8000)
                continue
            if attempt < 2:
                page.reload(wait_until="domcontentloaded", timeout=90000)
                page.wait_for_timeout(5000)
    try:
        page.screenshot(path=str(OUT / f"{lang}_startup_error.png"), full_page=True)
        print(f"Could not load live UI for {lang}. URL: {page.url}; body excerpt: {page.locator('body').inner_text()[:700]!r}")
    finally:
        context.close()
    raise AssertionError(f"Public Streamlit UI did not render expected heading for {lang}")


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    try:
        ctx, page = load_app(browser, "fr", {"width": 1440, "height": 900}, "Paramètres essentiels")
        try:
            errors = []
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            # Use only bundled synthetic demo values, never real private finances.
            page.get_by_role("button", name=re.compile("Charger un exemple")).first.click(timeout=30000)
            page.get_by_role("button", name=re.compile("Lancer la projection")).first.click(timeout=30000)
            page.get_by_role("tab", name=re.compile("Résultats")).first.click(timeout=30000)
            page.get_by_text("Patrimoine net nominal", exact=True).first.wait_for(timeout=45000)
            assert not errors, f"Live browser JavaScript errors: {errors}"
            page.screenshot(path=str(OUT / "fr_desktop_after_projection.png"), full_page=True)
            print("PASS live desktop French: example -> projection -> results")
        except Exception:
            page.screenshot(path=str(OUT / "fr_desktop_error.png"), full_page=True)
            raise
        finally:
            ctx.close()

        ctx, page = load_app(browser, "vi", {"width": 390, "height": 844}, "Thông số cần thiết")
        try:
            width_diff = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            assert width_diff <= 8, f"Live mobile horizontal overflow: {width_diff} px"
            page.screenshot(path=str(OUT / "vi_mobile_loaded.png"), full_page=True)
            print("PASS live mobile Vietnamese: localized heading, no page overflow")
        except Exception:
            page.screenshot(path=str(OUT / "vi_mobile_error.png"), full_page=True)
            raise
        finally:
            ctx.close()
    finally:
        browser.close()
