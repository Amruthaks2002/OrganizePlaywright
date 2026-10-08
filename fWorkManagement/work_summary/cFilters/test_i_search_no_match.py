from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_hours, employee_search


def test_search_no_match():
    """WS-029: typing a name nobody has offers no employees to pick."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        search = employee_search(page)
        search.click()
        search.press_sequentially("zz-no-such-employee-zz", delay=40)

        # while the dropdown fades in, vue-select briefly has two #vs1__listbox elements; the open one is the menu
        listbox = page.locator("#vs1__listbox.vs__dropdown-menu")
        expect(listbox.locator(".vs__no-options")).to_have_text("Sorry, no matching options.")
        expect(listbox.get_by_role("option")).to_have_count(0)

        browser.close()
