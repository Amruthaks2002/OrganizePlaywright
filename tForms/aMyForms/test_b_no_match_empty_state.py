import uuid
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_my_forms, main_content, search_forms, form_rows, footer_summary


def test_no_match_empty_state():
    """FM-002: a search with no matches shows the empty state and a Clear filters link."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        main = main_content(page)
        text = f"zz-no-match-{uuid.uuid4().hex[:8]}"

        search_forms(page, text)

        expect(form_rows(page)).to_have_count(0)
        expect(main.get_by_text(f'find any forms matching "{text}"')).to_be_visible()
        expect(main.get_by_text("Clear filters", exact=True)).to_be_visible()
        expect(footer_summary(page)).to_have_text("Showing 0 to 0 of 0 rows")

        browser.close()
