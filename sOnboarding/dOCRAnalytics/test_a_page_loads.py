import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_onboarding_submenu, main_content, kpi_value, ANALYTICS_URL


def test_page_loads():
    """OA-001: Onboarding > OCR Analytics shows the four document KPIs with sensible values."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_onboarding_submenu(page, "ocr-analytics")
        expect(page).to_have_url(ANALYTICS_URL)
        main = main_content(page)

        expect(main.get_by_role("heading", name="Onboarding Document Analytics")).to_be_visible()
        expect(main.get_by_text("Monitor extracted document activity and extraction performance.")).to_be_visible()
        total = int(kpi_value(page, "Total Documents"))
        today = int(kpi_value(page, "Today's Uploads"))
        manual = int(kpi_value(page, "Manual Review"))
        confidence = kpi_value(page, "Avg OCR Confidence")
        assert 0 <= today <= total and 0 <= manual <= total, (total, today, manual)
        assert re.fullmatch(r"\d{1,3}\.\d{2}%", confidence) and float(confidence[:-1]) <= 100, confidence

        browser.close()
