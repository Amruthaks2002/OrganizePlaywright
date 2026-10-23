import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_my_forms, main_content, search_input, status_filter, type_filter


def test_page_loads():
    """FM-001: Forms > My Forms opens the forms list with its filters and table headers."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        main = main_content(page)

        expect(page).to_have_url(re.compile(r"/forms$"))
        expect(main.get_by_role("link", name="Home")).to_be_visible()
        expect(main.get_by_role("heading", name="My Forms", level=1)).to_be_visible()
        expect(main.get_by_role("link", name="Probation Reviews")).to_be_visible()
        expect(main.get_by_role("link", name=re.compile("New Form"))).to_be_visible()
        expect(search_input(page)).to_be_visible()
        expect(status_filter(page).locator("option")).to_have_text(["All Status", "Active", "Inactive"])
        expect(type_filter(page).locator("option")).to_have_text(["All Types", "General", "Probation Review"])
        expect(main.locator("input[type=date]")).to_have_count(2)
        for header in ["Forms", "Created Date", "Status", "Actions"]:
            expect(main.get_by_text(header, exact=True).first).to_be_visible()

        browser.close()
