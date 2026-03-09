from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time
import re


def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_filtersbal():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        login(page)
        page.get_by_test_id("sidebar-navlink-audit logs").click()
        expect(page).to_have_url(re.compile(r".*/audits*"))


        page.locator("select").nth(1).select_option(label="Created")
        time.sleep(1)
        expect(page.locator("tbody")).to_contain_text("created")

        page.locator("select").nth(1).select_option(label="Updated")
        time.sleep(1)
        expect(page.locator("tbody")).to_contain_text("updated")

        page.locator("select").nth(1).select_option(label="Deleted")
        time.sleep(1)
        expect(page.locator("tbody")).to_contain_text("deleted")

        page.get_by_role("button", name =  "Reset All" ).click()

        time.sleep(2)

        search_input=page.get_by_placeholder("Search by user...")
        search_input.fill("admin")
        page.locator("li:has-text('Admin User')").click()
        time.sleep(3)

        users = page.locator("tbody tr td:nth-child(4) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "Admin User", f"Unexpected user found: {text}"

        page.get_by_role("link", name="2").click()
        time.sleep(4)
        users = page.locator("tbody tr td:nth-child(4) span")
        count = users.count()
        for i in range(count):
            text = users.nth(i).text_content().strip()
            assert text == "Admin User", f"Unexpected user found: {text}"

