from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, celebrations_toggle, event_types, find_month_with,
                                    month_label, retry_if_data_changed)


def test_celebrations_toggle():
    """DB-031: switching celebrations Off hides birthdays and anniversaries and leaves everything
    else; switching back On brings them back."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")

        def check():
            open_dashboard(page)
            assert find_month_with(page, "birthday"), "no birthdays in the next six months"
            before = event_types(page)
            toggle = celebrations_toggle(page)
            expect(toggle).to_have_text("On")
            try:
                toggle.click()
                expect(toggle).to_have_text("Off")
                page.wait_for_timeout(1200)
                after = event_types(page)
                assert "birthday" not in after and "anniversary" not in after, f"still shown: {after}"
                assert sorted(after) == sorted(k for k in before if k not in ("birthday", "anniversary"))
            finally:
                if celebrations_toggle(page).inner_text().strip() == "Off":
                    celebrations_toggle(page).click()
            expect(toggle).to_have_text("On")
            page.wait_for_timeout(1200)
            assert sorted(event_types(page)) == sorted(before), f"month {month_label(page).inner_text()}"

        retry_if_data_changed(check)
        browser.close()
