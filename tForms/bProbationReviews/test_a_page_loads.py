import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_probation_reviews, main_content, search_input, status_filter, type_filter


def test_page_loads():
    """PR-001: Forms > Probation Reviews opens the probation review forms list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_probation_reviews(page)
        main = main_content(page)

        expect(page).to_have_url(re.compile(r"/probation-reviews$"))
        expect(main.get_by_role("heading", name="Probation Review Forms", level=1)).to_be_visible()
        expect(search_input(page)).to_be_visible()
        expect(status_filter(page).locator("option")).to_have_text(["All Status", "Active", "Inactive"])
        expect(type_filter(page)).to_have_count(0)
        expect(main.locator("input[type=date]")).to_have_count(2)
        for header in ["Forms", "Created Date", "Status", "Actions"]:
            expect(main.get_by_text(header, exact=True).first).to_be_visible()

        browser.close()
