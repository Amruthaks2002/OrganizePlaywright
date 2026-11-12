"""ML-026: A mail's own styles don't change the rest of the app.

Steps:
1. Open Mail Logs and note the font of the page and the sidebar.
2. Open the newest mail.
3. Check the font of the page and the sidebar again (outside the mail body).

Expected: only the mail body uses the mail's styles; the sidebar and the page keep the app's font.

Known bug: the mail HTML (with a global "* { font-family: 'Red Hat Display' !important }" rule) is inserted straight
into the page, so the whole app, sidebar included, switches font while a mail is open. This test fails until that's
fixed.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/mail-logs"
EMPTY_MESSAGE = "No mail has been sent yet."


def wait_for_list(page):
    page.get_by_role("heading", name="Mail Logs").wait_for(state="visible")
    time.sleep(1)


def open_mail_logs(page):
    """Logs in as admin and opens Logs > Mail Log from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-mail-log")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    wait_for_list(page)


def fonts(page):
    return {
        "page": page.evaluate("getComputedStyle(document.body).fontFamily"),
        "sidebar": page.get_by_test_id("sidebar-navigation").evaluate("e => getComputedStyle(e).fontFamily"),
    }


def test_ml_026_email_css_contained():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_mail_logs(page)
        before = fonts(page)

        page.locator("table tbody tr").first.locator("td").nth(1).get_by_role("link").click()
        page.get_by_role("link", name="← Back to Mail Activity Logs").wait_for(state="visible")
        time.sleep(1)
        after = fonts(page)
        changed = {key: (before[key], after[key]) for key in before if before[key] != after[key]}
        assert not changed, f"the mail changed the app's font: {changed}"

        browser.close()
