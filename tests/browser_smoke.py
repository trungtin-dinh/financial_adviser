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
        basic_heading = page.get_by_role("heading", name=basic, exact=True).first
        basic_heading.wait_for(timeout=45000)
        results_text = {"fr": "Résultats", "en": "Results", "vi": "Kết quả"}[lang]
        results_heading = page.get_by_role("heading", name=results_text, exact=True).first
        # Initial load: only input controls, no empty dashboard occupying space.
        assert results_heading.count() == 0, f"Results visible before Run: {lang}/{device}"
        child_add = {"fr":"Ajouter un enfant", "en":"Add a child", "vi":"Thêm một người con"}[lang]
        page.get_by_role("button", name=re.compile(re.escape(child_add))).first.wait_for(timeout=15000)
        page.screenshot(path=str(OUT / f"{lang}_{device}_overview.png"), full_page=True)
        overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 8, f"Unexpected page-level horizontal scroll: {lang}/{device}, {overflow}px"
        # Life events are directly accessible; no hidden expander click is needed.
        page.get_by_text(life, exact=False).first.wait_for(timeout=10000)
        add = {"fr":"Ajouter un événement", "en":"Add an event", "vi":"Thêm sự kiện"}[lang]
        page.get_by_role("button", name=re.compile(re.escape(add))).click(timeout=10000)
        event = {"fr":"Événement 1", "en":"Event 1", "vi":"Sự kiện 1"}[lang]
        title = page.get_by_role("button", name=re.compile(r"▸.*" + re.escape(event))).first
        title.wait_for(timeout=30000)
        short_label = {"fr": "Description courte", "en": "Short description", "vi": "Mô tả ngắn"}[lang]
        description_input = page.get_by_role("textbox", name=short_label, exact=True)
        # New items must be collapsed, with delete reachable in the header.
        assert description_input.count() == 0
        assert page.get_by_role("button", name="✕", exact=True).count() >= 1
        title.click()
        description_input.wait_for(state="visible", timeout=10000)
        description_input.fill(f"UI check {lang}")
        description_input.press("Tab")
        page.get_by_role("button", name=re.compile(r"▾.*📅")).first.click()
        description_input.wait_for(state="hidden", timeout=10000)
        page.get_by_role("button", name=re.compile(r"▸.*📅")).first.click()
        description_input.wait_for(state="visible", timeout=10000)
        assert description_input.input_value() == f"UI check {lang}"
        page.screenshot(path=str(OUT / f"{lang}_{device}_event.png"), full_page=True)
        page.get_by_role("button", name=re.compile(re.escape(child_add))).first.click(timeout=15000)
        child_title = {"fr": "Enfant 1", "en": "Child 1", "vi": "Con 1"}[lang]
        child_header = page.get_by_role("button", name=re.compile(r"▸.*" + re.escape(child_title))).first
        child_header.wait_for(timeout=15000)
        age_label = {"fr":"Âge au début","en":"Age at start","vi":"Tuổi lúc bắt đầu"}[lang]
        end_label = {"fr":"Âge de fin","en":"Support ends at age","vi":"Tuổi ngừng chu cấp"}[lang]
        age_input = page.get_by_role("spinbutton", name=age_label, exact=True)
        end_input = page.get_by_role("spinbutton", name=end_label, exact=True)
        assert age_input.count() == 0, "A newly added child is unexpectedly expanded"
        child_header.click()
        age_input.wait_for(state="visible", timeout=15000)
        if width >= 1024:
            a_box, b_box = age_input.bounding_box(), end_input.bounding_box()
            assert a_box and b_box and abs(a_box["y"]-b_box["y"]) <= 12, (
                f"Child age fields misaligned on desktop: {a_box}, {b_box}")
        page.get_by_role("button", name=re.compile(r"▾.*" + re.escape(child_title))).first.click()
        age_input.wait_for(state="hidden", timeout=10000)
        dependent_add = {"fr":"Ajouter une personne à charge", "en":"Add another dependent",
                         "vi":"Thêm người phụ thuộc"}[lang]
        page.get_by_role("button", name=re.compile(re.escape(dependent_add))).first.click(timeout=15000)
        # An additional dependent must also appear collapsed.
        dependent_title = {"fr": "Proche 1", "en": "Dependent 1",
                           "vi": "Người phụ thuộc 1"}[lang]
        dep_header = page.get_by_role("button", name=re.compile(r"▸.*" + re.escape(dependent_title))).first
        dep_header.wait_for(timeout=15000)
        # Close controls stay on the header line, also on narrow mobile.
        x = page.get_by_role("button", name="✕", exact=True).first
        hx, dx = child_header.bounding_box(), x.bounding_box()
        assert hx and dx and abs(hx["y"] - dx["y"]) < 18, (
            f"Close button wrapped below its card header: {hx}, {dx}")
        assert dx["width"] >= 40, f"Close button clipped: {dx}"
        page.screenshot(path=str(OUT / f"{lang}_{device}_household.png"), full_page=True)
        if width >= 1024:
            house_title = {"fr":"Composition du foyer et dépenses selon l'âge",
                "en":"Household members and age-related expenses",
                "vi":"Thành viên gia đình và chi tiêu theo độ tuổi"}[lang]
            house_heading = page.get_by_role("heading", name=house_title, exact=True).first
            event_heading = page.get_by_role("heading", name=re.compile(re.escape(life))).first
            house_rect, event_rect = house_heading.bounding_box(), event_heading.bounding_box()
            assert house_rect and event_rect and event_rect["x"] > house_rect["x"] + 180, (
                f"Household and events are not side by side: {house_rect}, {event_rect}")
        assert not errors, f"Client errors: {lang}/{device}: {errors}"
        overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
        assert overflow <= 8, f"Event form overflow: {lang}/{device}, {overflow}px"
        print(f"OK {lang} {device} {width}x{height}: compact cards and no overflow")
        if device in ("desktop", "mobile"):
            example = {"fr":"Charger un exemple","en":"Load example","vi":"Nạp dữ liệu ví dụ"}[lang]
            confirm = {"fr":"Confirmer le remplacement","en":"Confirm replacement","vi":"Xác nhận thay thế"}[lang]
            run_name = {"fr":"Lancer la projection","en":"Run projection","vi":"Chạy dự phóng"}[lang]
            page.get_by_role("button", name=re.compile(re.escape(example))).first.click(timeout=15000)
            page.get_by_role("button", name=confirm, exact=True).first.click(timeout=15000)
            page.get_by_role("button", name=re.compile(re.escape(run_name))).first.click(timeout=20000)
            results_heading.wait_for(timeout=30000)
            overview_title = {
                "fr": "À retenir sur votre projection",
                "vi": "Những điểm chính từ kết quả dự phóng",
            }[lang]
            overview = page.get_by_role("heading", name=overview_title, exact=True).first
            overview.wait_for(timeout=15000)
            # Cash resilience is discoverable after running the calculation;
            # its inputs are editable without replacing the saved scenario.
            resilience_label = {
                "fr": "Résilience : réserve et dépense imprévue",
                "vi": "Khả năng chống chịu: dự phòng và chi phí bất ngờ",
            }[lang]
            page.get_by_text(resilience_label, exact=True).first.click(timeout=15000)
            extra_amount_label = {
                "fr": "Montant supplémentaire simulé",
                "vi": "Chi phí phát sinh mô phỏng",
            }[lang]
            cash_shock = page.get_by_role(
                "spinbutton", name=extra_amount_label, exact=True).first
            cash_shock.wait_for(state="visible", timeout=15000)
            cash_shock.fill("500", timeout=15000)
            cash_shock.press("Tab")
            assert float(cash_shock.input_value().replace(",", ".")) == 500.0
            page.screenshot(path=str(OUT / f"{lang}_{device}_resilience.png"), full_page=True)
            # Two core curves are visible by default; the remaining series
            # are selectable without leaving the results area.
            curves_label = {"fr": "Afficher / masquer les courbes",
                            "vi": "Hiện / ẩn đường biểu diễn"}[lang]
            page.get_by_role("button", name=curves_label).first.click(timeout=15000)
            cash_name = {"fr": "Trésorerie", "vi": "Tiền mặt"}[lang]
            cash_curve = page.get_by_role("checkbox", name=cash_name, exact=True).first
            cash_curve.wait_for(state="visible", timeout=15000)
            assert not cash_curve.is_checked(), "Secondary chart line enabled by default"
            # Streamlit renders a styled label over the native checkbox input.
            # Click the visible label, as a real user would, rather than the input.
            cash_curve.locator("xpath=ancestor::label[1]").click(timeout=15000)
            assert cash_curve.is_checked(), "Chart curve cannot be enabled"
            page.screenshot(path=str(OUT / f"{lang}_{device}_chart_controls.png"), full_page=True)
            # Check the risk dashboard is usable after an actual projection.
            page.keyboard.press("Escape")
            risk_start_name = {
                "fr": "Début du choc (mois de projection)",
                "vi": "Bắt đầu cú sốc (tháng dự phóng)",
            }[lang]
            stress_start = page.get_by_role(
                "spinbutton", name=risk_start_name, exact=True).first
            stress_start.wait_for(state="visible", timeout=15000)
            stress_start.fill("4", timeout=15000)
            stress_start.press("Tab")
            assert stress_start.input_value() == "4", (
                f"Stress start month did not update: {lang}/{device}")
            page.screenshot(path=str(OUT / f"{lang}_{device}_stress_controls.png"), full_page=True)
            bb, rb = basic_heading.bounding_box(), results_heading.bounding_box()
            assert bb and rb
            if width >= 1024:
                assert rb["x"] > bb["x"] + 150 and abs(rb["y"] - bb["y"]) < 160, (
                    f"Desktop post-run layout is not side-by-side: {bb}, {rb}")
            else:
                assert rb["y"] > bb["y"], f"Mobile post-run vertical order broken: {bb}, {rb}"
            page.screenshot(path=str(OUT / f"{lang}_{device}_results.png"), full_page=True)
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