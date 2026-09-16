from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time


def get_pagination_nav(page):
    return page.locator("nav").last


def test_audit_logs_pagination():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-logs").click()
        audit_log_link = page.get_by_test_id("sidebar-child-audit-log")
        audit_log_link.wait_for(state="visible")
        audit_log_link.click()
        page.get_by_text("Track all system changes and user activities").wait_for(state="visible")
        time.sleep(1)

        # Previous control is disabled (rendered as a span, not a link) on page 1
        nav = get_pagination_nav(page)
        prev_control = nav.locator(":scope > *").first
        assert prev_control.evaluate("e => e.tagName") == "SPAN"

        first_id_page1 = page.locator("table tbody tr").first.locator("td").first.text_content()

        # clicking a specific page number navigates to that page and highlights it as active
        nav.get_by_role("link", name="3", exact=True).click()
        time.sleep(1)
        first_id_page3 = page.locator("table tbody tr").first.locator("td").first.text_content()
        assert first_id_page3 != first_id_page1

        nav = get_pagination_nav(page)
        active_page_link = nav.get_by_role("link", name="3", exact=True)
        assert "bg-indigo-600" in (active_page_link.get_attribute("class") or "")

        # Previous is now enabled (a real link) since we are past page 1
        prev_control = nav.locator(":scope > *").first
        assert prev_control.evaluate("e => e.tagName") == "A"

        # Previous navigates back a page
        prev_control.click()
        time.sleep(1)
        first_id_page2 = page.locator("table tbody tr").first.locator("td").first.text_content()
        assert first_id_page2 != first_id_page3
        assert first_id_page2 != first_id_page1

        # Next navigates forward a page, back to the same data as page 3
        nav = get_pagination_nav(page)
        next_control = nav.locator(":scope > *").last
        assert next_control.evaluate("e => e.tagName") == "A"
        next_control.click()
        time.sleep(1)
        first_id_back_to_page3 = page.locator("table tbody tr").first.locator("td").first.text_content()
        assert first_id_back_to_page3 == first_id_page3

        browser.close()
