from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, export_button, expect_toast, EXPORT_URL,
                                       EXPORT_STARTED)


def test_export():
    """WS-035: Export on Comp Hours queues the compensatory summary report and says so."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        expect(export_button(page)).to_have_count(0)  # only on Comp Hours
        open_tab(page, "Regular Hours")
        expect(export_button(page)).to_have_count(0)
        open_tab(page, "Comp Hours")

        with page.expect_response(lambda r: r.url.startswith(EXPORT_URL)) as response:
            export_button(page).click()
        assert response.value.status < 400, response.value.status
        expect_toast(page, EXPORT_STARTED)

        browser.close()
