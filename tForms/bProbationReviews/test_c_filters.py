import re
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_probation_reviews, unique_form_title, create_form_api, toggle_status_api, delete_forms,
    search_forms, status_filter, date_from, row_titles, settle,
)


def test_filters():
    """PR-003: search, status and date filters work on the probation list."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_probation_reviews(page)
        base = unique_form_title()
        try:
            create_form_api(page, f"{base} On", type="probation_review")
            off = create_form_api(page, f"{base} Off", type="probation_review")
            toggle_status_api(page, off["id"])

            search_forms(page, base)
            assert sorted(row_titles(page)) == [f"{base} Off", f"{base} On"]
            search_forms(page, f"{base} On")
            assert row_titles(page) == [f"{base} On"]

            search_forms(page, base)
            status_filter(page).select_option("inactive")
            expect(page).to_have_url(re.compile("status=inactive"))
            settle(page)
            assert row_titles(page) == [f"{base} Off"]
            status_filter(page).select_option("active")
            expect(page).to_have_url(re.compile("status=active"))
            settle(page)
            assert row_titles(page) == [f"{base} On"]

            tomorrow = (date.today() + timedelta(days=1)).isoformat()
            date_from(page).fill(tomorrow)
            expect(page).to_have_url(re.compile(f"from_date={tomorrow}"))
            settle(page)
            assert row_titles(page) == []
        finally:
            delete_forms(page, base)

        browser.close()
