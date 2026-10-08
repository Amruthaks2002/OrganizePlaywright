from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, open_upcoming, upcoming_toggle, upcoming_count, section


def test_expand_collapse_and_empty_state():
    """DB-022: Upcoming Events opens and closes from its chevron; the header count matches the event
    cards, and with none it shows 'NO UPCOMING EVENTS'."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        body = section(page, "Upcoming Events")
        count = upcoming_count(page)
        open_upcoming(page)

        empty = body.get_by_text("No upcoming events", exact=False)
        cards = body.locator("h4")
        if count == 0:
            expect(empty).to_be_visible()
        else:
            expect(cards).to_have_count(count)
            expect(empty).to_have_count(0)

        upcoming_toggle(page).click()
        page.wait_for_timeout(800)
        expect(empty if count == 0 else cards.first).to_be_hidden()
        browser.close()
