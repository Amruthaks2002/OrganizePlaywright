import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_my_submissions, main_content, settle


def test_sort_by_submitted_date():
    """MS-004: the Submitted Date header switches between oldest-first and newest-first."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_submissions(page)
        header = main_content(page).get_by_text(re.compile(r"^\s*Submitted Date"))
        expect(header).to_contain_text("↓")

        header.click()
        expect(page).to_have_url(re.compile(r"sort=submitted_at"))
        expect(page).to_have_url(re.compile(r"direction=asc"))
        settle(page)
        expect(header).to_contain_text("↑")

        header.click()
        expect(page).to_have_url(re.compile(r"direction=desc"))
        settle(page)
        expect(header).to_contain_text("↓")

        browser.close()
