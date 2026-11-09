import json
import os

from playwright.sync_api import sync_playwright
from utils.learning_helper import BASE_URL, settle


DAVID_EMAIL = "david@iocod.com"


def open_david(browser):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    page.goto(BASE_URL)
    page.fill("#email", DAVID_EMAIL)
    page.fill("#password", "password")
    page.get_by_test_id("sign-in-button").click()
    page.wait_for_url("**/dashboard**")
    settle(page)
    return page


def test_admin_routes_not_exposed():
    """PR-011: an employee's page data doesn't list the admin Payroll routes (pay runs, salaries, settings...).
    Known bug: the Ziggy route list sent to every page includes all of them. This test fails until that's fixed."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        david = open_david(browser)

        page = json.loads(david.locator("[data-page]").first.get_attribute("data-page"))
        routes = page["props"].get("ziggy", {}).get("routes", {})
        exposed = sorted(n for n in routes if n.startswith("payroll.") and not n.startswith(("payroll.my.", "payroll.security.")))
        assert not exposed, f"{len(exposed)} admin payroll routes exposed, e.g. {exposed[:5]}"

        browser.close()


# ====================================================================================================
# TEST CASES
#
# Test Case: test_admin_routes_not_exposed
# Test Description:
#   PR-011: an employee's page data doesn't list the admin Payroll routes (pay runs, salaries, settings...). Known
#   bug: the Ziggy route list sent to every page includes all of them. This test fails until that's fixed.
# Test Steps:
#   1. Open a browser and sign in as David (employee).
#   2. Read the route list (Ziggy) from the page data sent to the browser.
#   3. Pick out the Payroll routes other than the employee's own (payroll.my.*) and the security routes
#      (payroll.security.*).
#   4. Confirm there are none; the failure message gives the count and some examples.
