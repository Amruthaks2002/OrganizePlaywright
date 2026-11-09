import json
import os
import re

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


def test_sensitive_fields_masked():
    """PR-266: on David's own payslip, any bank account number is masked (****1234) - never shown in full."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        david = open_david(browser)
        mine = props_at(david, f"{BASE_URL}/payroll/my/payslips")["payslips"]
        assert mine, "David has no payslips"

        goto(david, f"{BASE_URL}/payroll/payslips/{mine[0]['id']}")
        assert not re.search(r"\b\d{9,18}\b", david.locator("main").inner_text()), "a full account number is shown"

        browser.close()
