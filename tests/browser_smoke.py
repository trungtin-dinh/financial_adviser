"""Actual headless Chromium exercise at desktop/tablet/mobile viewport sizes.

Run after starting streamlit on localhost:8501. Screenshots are uploaded by CI.
"""
from pathlib import Path
import re
import time
import urllib.request
from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8501"
OUT = Path("artifacts/screenshots")
OUT.mkdir(parents=True, exist_ok=True)

for attempt in range(80):
    try:
        with urllib.request.urlopen(BASE + "/_stcore/health", timeout=3) as resp:
            if resp.status == 200:
                break
    except OSError:
        time.sleep(1)
else:
    raise RuntimeError("Streamlit server was not ready")

CASES = [
    ("fr", "desktop", 1440, 900, "Paramètres essentiels", "Événements de vie et risques"),
    ("en", "tablet", 834, 1112, "Essential inputs", "Life events and risks"),
    ("vi", "mobile", 390, 844, "Thông số cần thiết", "Sự kiện cuộc sống và rủi ro"),
    ("fr", "mobile_small", 360, 800, "Paramètres essentiels", "Événements de vie et risques"),
]

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    for lang, device, width, height, basic, life in CASES:
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(f"{BASE}/?lang={lang}", wait_until="domcontentloaded", timeout=60000)
        page.get_by_text(basic, exact=True).first.wait_for(timeout=45000)
        child_add = {"fr":"Ajouter un enfant", "en":"Add a child", "vi":"Thêm một người con"}[lang]
        page.get_by_role("button", name=re.compile(re.escape(child_add))).first.wait_for(timeout=15000)
        page.screenshot(path=str(OUT / f"{lang}_{device}_overview.png"), full_page=True)
        overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 8, f"Unexpected page-level horizontal scroll: {lang}/{device}, {overflow}px"
        # Expand event form; verify Add is accessible and rendered after a rerun.
        page.get_by_text(life, exact=False).first.click(timeout=10000)
        add = {"fr":"Ajouter un événement", "en":"Add an event", "vi":"Thêm sự kiện"}[lang]
        page.get_by_role("button", name=re.compile(re.escape(add))).click(timeout=10000)
        event = {"fr":"Événement 1", "en":"Event 1", "vi":"Sự kiện 1"}[lang]
        title = page.get_by_text(event, exact=True).first
        title.wait_for(timeout=30000)
        short_label = {"fr": "Description courte", "en": "Short description", "vi": "Mô tả ngắn"}[lang]
        description_input = page.get_by_role("textbox", name=short_label, exact=True)
        description_input.fill(f"UI check {lang}")
        description_input.press("Tab")
        assert page.get_by_role("textbox", name=short_label, exact=True).input_value() == f"UI check {lang}"
        title.scroll_into_view_if_needed()
        page.screenshot(path=str(OUT / f"{lang}_{device}_event.png"), full_page=True)
        assert not errors, f"Client errors: {lang}/{device}: {errors}"
        overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 8, f"Event form overflow: {lang}/{device}, {overflow}px"
        print(f"OK {lang} {device} {width}x{height}: no page overflow, event card usable")
        page.close()

    # Statistical reference page on different viewports and languages.
    for lang, width, height in [("fr", 1440, 900), ("en", 390, 844), ("vi", 360, 800)]:
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"{BASE}/benchmarks?lang={lang}", wait_until="domcontentloaded", timeout=60000)
        title = {"fr": "Références statistiques", "en": "Statistical references", "vi": "Số liệu thống kê tham khảo"}[lang]
        try:
            page.get_by_role("heading", name=re.compile(re.escape(title))).first.wait_for(timeout=15000)
        except Exception:
            print("STATISTICS PAGE DEBUG:", lang, page.url, page.locator("body").inner_text()[-3500:])
            raise
        assert page.evaluate("document.documentElement.scrollWidth - window.innerWidth") <= 8
        metric = page.locator('[data-testid="stMetricValue"]').first
        metric.wait_for(state="visible", timeout=30000)
        assert "€" in metric.inner_text() or "₫" in metric.inner_text()
        page.screenshot(path=str(OUT / f"{lang}_benchmarks.png"), full_page=True)
        page.close()
    browser.close()