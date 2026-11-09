import json
import os

from playwright.sync_api import Page, sync_playwright
from utils.learning_helper import BASE_URL, goto, settle


DAVID_EMAIL = "david@iocod.com"


def page_props(page: Page):
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page: Page, url):
    goto(page, url)
    return page_props(page)


def open_david(browser):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    page.goto(BASE_URL)
    page.fill("#email", DAVID_EMAIL)
    page.fill("#password", "password")
    page.get_by_test_id("sign-in-button").click()
    page.wait_for_url("**/dashboard**")
    settle(page)
    return page


def test_download_own_payslip():
    """PR-264: David can download his own payslip as a PDF."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        david = open_david(browser)
        mine = props_at(david, f"{BASE_URL}/payroll/my/payslips")["payslips"]
        assert mine, "David has no payslips"

        response = david.request.get(f"{BASE_URL}/payroll/payslips/{mine[0]['id']}/download")
        assert response.status == 200 and response.body().startswith(b"%PDF")

        browser.close()
