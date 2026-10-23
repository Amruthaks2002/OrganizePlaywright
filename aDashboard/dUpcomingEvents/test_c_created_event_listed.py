import datetime

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, open_upcoming, upcoming_count, section, create_event,
                                    delete_event, unique_tag, ui_date, today, QA_EVENT_PREFIX)


def test_created_event_listed():
    """DB-024: an event created for tomorrow appears under Upcoming Events with its description, date
    and location, raises the count by one, and disappears again once deleted."""
    title = f"{QA_EVENT_PREFIX} {unique_tag()}"
    tomorrow = today() + datetime.timedelta(days=1)
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        before = upcoming_count(page)
        try:
            create_event(page, title, tomorrow, location="QA Room 7", description="Dashboard upcoming check")
            open_dashboard(page)
            assert upcoming_count(page) == before + 1
            open_upcoming(page)
            # the smallest block holding both the title and the location is the event card
            card = section(page, "Upcoming Events").locator("div").filter(
                has=page.locator("h4", has_text=title)).filter(has_text="QA Room 7").last
            expect(card).to_contain_text("Dashboard upcoming check")
            expect(card).to_contain_text(ui_date(tomorrow))
            expect(card).to_contain_text("QA Room 7")
        finally:
            delete_event(page, title)

        open_dashboard(page)
        assert upcoming_count(page) == before
        open_upcoming(page)
        expect(section(page, "Upcoming Events").get_by_text(title)).to_have_count(0)
        browser.close()
