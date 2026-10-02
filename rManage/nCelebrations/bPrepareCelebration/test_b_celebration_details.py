import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, open_prepare, main_content, EMPLOYEE, CELEBRATION_DATE_TEXT


def test_celebration_details():
    """PC-002: the Celebration Details panel matches the celebration on the list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_prepare(page)
        details = main_content(page).get_by_role("heading", name="Celebration Details").locator("xpath=..")

        text = re.sub(r":\s*", ": ", re.sub(r"\s+", " ", details.inner_text()))
        for expected in [f"Employee: {EMPLOYEE}", "Type: Work Anniversary", "Years: 2",
                         f"Date: {CELEBRATION_DATE_TEXT}", "Status: APPROVED"]:
            assert expected in text, f"'{expected}' missing from Celebration Details: {text}"

        browser.close()
