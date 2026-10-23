import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as


def test_notifications_dropdown():
    """DB-051: the notifications button opens a Notifications panel with 'View all notifications'
    (which opens /notifications). With unread notifications the button shows their count and the
    panel offers 'Mark all as read'; with none it shows no count and says "You're all caught up!".

    Opening /notifications marks everything as read, so which state the panel is in depends on
    what happened before this test. Mark all as read itself is never clicked."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        button = page.get_by_test_id("notification-button")
        unread = button.inner_text().strip()
        assert re.fullmatch(r"\d*", unread), f"badge shows {unread!r}"
        button.click()

        panel = page.locator("div:visible").filter(has=page.get_by_text("Notifications", exact=True)).filter(
            has=page.get_by_text("View all notifications")).last
        expect(panel).to_be_visible()
        if unread:
            expect(panel.get_by_text("Mark all as read")).to_be_visible()
        else:
            expect(panel.get_by_text("You're all caught up!")).to_be_visible()
        panel.get_by_text("View all notifications").click()
        expect(page).to_have_url(re.compile(r"/notifications$"))
        browser.close()
