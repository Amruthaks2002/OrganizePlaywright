from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, from_date, to_date, wait_for_logs, tab_button,
                                       first_of_month, today, LOGS_URL)


def test_default_date_range():
    """WS-023: every tab starts on the current month so far - From is the 1st, To is today - and the table
    asks the server for exactly that range."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        expect(from_date(page)).to_have_value(first_of_month().isoformat())
        expect(to_date(page)).to_have_value(today().isoformat())

        for tab in ["Regular Hours", "Comp Hours"]:
            with page.expect_request(lambda r: r.url.startswith(LOGS_URL)) as request:
                tab_button(page, tab).click()
            query = parse_qs(urlparse(request.value.url).query)
            assert query["hours[date_from]"] == [first_of_month().isoformat()], query
            assert query["hours[date_to]"] == [today().isoformat()], query
            expect(from_date(page)).to_have_value(first_of_month().isoformat())
            expect(to_date(page)).to_have_value(today().isoformat())

        browser.close()
