import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_my_forms, main_content


def test_probation_reviews_button():
    """FM-014: the Probation Reviews button opens the probation review forms list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)

        main_content(page).get_by_role("link", name="Probation Reviews").click()
        expect(page).to_have_url(re.compile(r"/probation-reviews$"))
        expect(main_content(page).get_by_role("heading", name="Probation Review Forms")).to_be_visible()

        browser.close()
