from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_hours, open_log_dialog, fill_log, submit_log, log_dialog, HOURS_URL


def test_browser_blocks_empty_submit():
    """WS-011: with no project or hours the browser's required checks stop the form - nothing is sent
    and the dialog stays open."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        posts = []
        page.on("request", lambda r: posts.append(r.url) if r.method == "POST" and r.url == HOURS_URL else None)

        dialog = open_log_dialog(page)
        fill_log(dialog, project=None, hours=None, desc="")
        submit_log(dialog)
        page.wait_for_timeout(1000)

        assert dialog.locator("select").evaluate("e => e.validity.valueMissing")
        assert dialog.locator("input[type=number]").evaluate("e => e.validity.valueMissing")
        expect(log_dialog(page)).to_be_visible()
        assert posts == [], posts

        browser.close()
