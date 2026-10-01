import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_my_submissions, main_content, footer_summary


def test_page_loads():
    """MS-001: Forms > My Submissions opens the list of forms you've submitted."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_submissions(page)
        main = main_content(page)

        expect(page).to_have_url(re.compile(r"/my-submissions$"))
        expect(main.get_by_role("heading", name="My Submissions", level=1)).to_be_visible()
        expect(main.get_by_text("Form Title", exact=True)).to_be_visible()
        expect(main.get_by_text(re.compile(r"^\s*Submitted Date"))).to_be_visible()
        expect(main.get_by_text("Actions", exact=True)).to_be_visible()
        expect(footer_summary(page)).to_be_visible()

        browser.close()
