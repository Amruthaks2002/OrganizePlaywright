import re
from datetime import date, timedelta
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, date_from,
    date_to, form_row, settle,
)


def test_date_filter():
    """FM-008: a date range excludes forms created outside it and includes forms created inside it."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        today = date.today()
        try:
            create_form_api(page, title)
            search_forms(page, title)
            expect(form_row(page, title)).to_have_count(1)

            tomorrow = (today + timedelta(days=1)).isoformat()
            date_from(page).fill(tomorrow)
            expect(page).to_have_url(re.compile(f"from_date={tomorrow}"))
            settle(page)
            expect(form_row(page, title)).to_have_count(0)

            date_from(page).fill((today - timedelta(days=7)).isoformat())
            date_to(page).fill(today.isoformat())
            expect(page).to_have_url(re.compile(f"to_date={today.isoformat()}"))
            settle(page)
            expect(form_row(page, title)).to_have_count(1)
        finally:
            delete_forms(page, title)

        browser.close()
