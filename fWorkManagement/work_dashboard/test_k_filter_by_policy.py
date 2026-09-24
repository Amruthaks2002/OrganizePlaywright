import re
from playwright.sync_api import sync_playwright
from utils.login_helper import login

def get_total_results(main):
    text = main.get_by_text("Showing", exact=False).inner_text()
    match = re.search(r"of (\d+) results", text)
    return int(match.group(1))

def test_filter_by_policy():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-work management").click()
        page.get_by_test_id("sidebar-child-work-dashboard").click()
        main = page.get_by_test_id("main-content")
        page.wait_for_timeout(1000)

        total_before = get_total_results(main)

        policy_filter = main.locator("select").nth(1)
        policy_filter.select_option(label="Morning")
        page.wait_for_timeout(1000)

        total_after = get_total_results(main)
        assert total_after < total_before, (
            f"Expected filtering by Policy to reduce the result count "
            f"(before={total_before}, after={total_after})"
        )

        browser.close()
