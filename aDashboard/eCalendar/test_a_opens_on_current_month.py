from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, main_content, month_label, month_label_text, today


def test_opens_on_current_month():
    """DB-025: the calendar opens on the current month with today's cell highlighted."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        expect(month_label(page)).to_have_text(month_label_text(today()))
        today_cell = main_content(page).locator("td.fc-day-today")
        expect(today_cell).to_have_count(1)
        expect(today_cell).to_have_attribute("data-date", today().isoformat())
        browser.close()
