from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, main_content, month_label, month_label_text, next_month, prev_month,
                                    today)


def test_month_label_returns_to_today():
    """DB-027: clicking the month label jumps back to the current month from a later or earlier one."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        for step in [next_month, prev_month]:
            step(page)
            step(page)
            expect(month_label(page)).not_to_have_text(month_label_text(today()))
            month_label(page).click()
            expect(month_label(page)).to_have_text(month_label_text(today()))
            expect(main_content(page).locator("td.fc-day-today")).to_have_count(1)
        browser.close()
