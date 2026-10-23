import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_progress, progress_url, main_content, progress_search, progress_rows, settle,
)


def test_clear_filters():
    """JP-010: Clear resets the search and every filter and lists everyone again."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page, progress_url(search="Anjana", role="employee", status="completed"))
        main = main_content(page)
        expect(main.locator(".vs__selected")).to_have_count(2)

        main.get_by_role("button", name="Clear", exact=True).click()
        expect(page).to_have_url(re.compile(r"journey=&role=&search=&status=$"))
        settle(page)
        expect(progress_search(page)).to_have_value("")
        expect(main.locator(".vs__selected")).to_have_count(0)
        expect(progress_rows(page)).to_have_count(10)

        browser.close()
