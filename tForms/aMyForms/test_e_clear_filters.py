import re
import uuid
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, main_content, search_forms, search_input, status_filter, type_filter, settle,
)


def test_clear_filters():
    """FM-005: Clear all / Clear filters resets the search and every filter."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        main = main_content(page)

        search_forms(page, f"zz-no-match-{uuid.uuid4().hex[:8]}")
        status_filter(page).select_option("inactive")
        expect(page).to_have_url(re.compile("status=inactive"))
        type_filter(page).select_option("general")
        expect(page).to_have_url(re.compile("type=general"))
        settle(page)

        main.get_by_text("Clear filters", exact=True).click()
        settle(page)
        expect(search_input(page)).to_have_value("")
        expect(status_filter(page)).to_have_value("")
        expect(type_filter(page)).to_have_value("")

        status_filter(page).select_option("active")
        expect(page).to_have_url(re.compile("status=active"))
        main.get_by_role("button", name="Clear all").click()
        settle(page)
        expect(status_filter(page)).to_have_value("")

        browser.close()
