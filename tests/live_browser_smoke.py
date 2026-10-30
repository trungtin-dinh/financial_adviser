"""Real hosted Streamlit UX verification after a GitHub deployment.

Checks actual production content, not just HTTP 200. Site can use a browser
iframe, so inspect frames and compare displayed app version to checkout HEAD.
Uses synthetic example data only.
"""
from __future__ import annotations

import os
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

BASE = os.environ.get('APP_URL', 'https://financial-adviser.streamlit.app').rstrip('/')
ROOT = Path(__file__).resolve().parents[1]
VERSION = re.search(r'^__version__\s*=\s*"([^"]+)"',
    (ROOT / 'financial_adviser' / '__init__.py').read_text(encoding='utf-8'), re.M).group(1)
OUT = ROOT / 'artifacts' / 'live'
OUT.mkdir(parents=True, exist_ok=True)


def find_visible_frame(page, heading: str, deadline_s: float = 140.0):
    """Find the rendered Streamlit app, even if Cloud hosts it in an iframe."""
    end = time.monotonic() + deadline_s
    while time.monotonic() < end:
        for frame in page.frames:
            try:
                if frame.get_by_role('heading', name=heading, exact=True).first.is_visible(timeout=500):
                    return frame
            except Exception:
                pass
        wake = page.get_by_role('button', name=re.compile('wake|restart|get this app back up', re.I))
        try:
            if wake.count() and wake.first.is_visible(timeout=300):
                wake.first.click(timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(1000)
    details=[]
    for frame in page.frames:
        try:
            details.append(f'{frame.url}: {frame.locator("body").inner_text(timeout=2000)[:900]!r}')
        except Exception as e:
            details.append(f'{frame.url}: {type(e).__name__}')
    raise AssertionError(f'Hosted app heading {heading!r} not found. Frames: {details}')


def capture(page, name):
    try:
        page.screenshot(path=str(OUT / name), full_page=True, timeout=20000)
    except Exception as exc:
        print(f'Could not save screenshot: {exc}')


def ensure_version(frame):
    match = frame.get_by_text(re.compile(r'v' + re.escape(VERSION)))
    match.first.wait_for(state='visible', timeout=20000)
    print(f'Version observed on hosted site: v{VERSION}')


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
    try:
        context = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = context.new_page()
        page.goto(f'{BASE}/?lang=fr', wait_until='domcontentloaded', timeout=90000)
        try:
            app = find_visible_frame(page, 'Paramètres essentiels')
            ensure_version(app)
            app.get_by_text('Composition du foyer et dépenses selon l\'âge', exact=True).first.wait_for(timeout=20000)
            capture(page, 'fr_desktop_before.png')

            # Open the collapsible file actions, load synthetic example and confirm.
            app.get_by_text('Scénarios : charger, exemple et exporter', exact=False).first.click(timeout=20000)
            app.get_by_role('button', name=re.compile('Charger un exemple')).first.click(timeout=20000)
            app.get_by_role('button', name='Confirmer le remplacement').first.click(timeout=20000)
            app.get_by_role('button', name=re.compile('Lancer la projection')).first.click(timeout=20000)
            app.get_by_text('Patrimoine net nominal', exact=True).first.wait_for(timeout=45000)
            capture(page, 'fr_desktop_result.png')
            print('PASS hosted French: matched version, household editor, example, projection, results')
        except Exception:
            capture(page, 'fr_desktop_error.png')
            raise
        finally:
            context.close()

        context = browser.new_context(viewport={'width': 390, 'height': 844}, is_mobile=True, device_scale_factor=1)
        page = context.new_page()
        page.goto(f'{BASE}/?lang=vi', wait_until='domcontentloaded', timeout=90000)
        try:
            app = find_visible_frame(page, 'Thông số cần thiết')
            ensure_version(app)
            app.get_by_text('Thành viên gia đình và chi tiêu theo độ tuổi', exact=True).first.wait_for(timeout=20000)
            overflow = app.evaluate('document.documentElement.scrollWidth - innerWidth')
            if overflow > 8:
                raise AssertionError(f'Mobile horizontal overflow: {overflow} CSS px')
            capture(page, 'vi_mobile.png')
            print('PASS hosted Vietnamese mobile: correct version, household editor, no overflow')
        except Exception:
            capture(page, 'vi_mobile_error.png')
            raise
        finally:
            context.close()
    finally:
        browser.close()