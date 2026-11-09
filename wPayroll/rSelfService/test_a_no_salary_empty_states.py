import json
import os

import pytest
from playwright.sync_api import Page, expect, sync_playwright
from utils.learning_helper import BASE_URL, goto, settle


def page_props(page: Page):
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def props_at(page: Page, url):
    goto(page, url)
    return page_props(page)


def dev_login(page: Page, role):
    page.goto(BASE_URL)
    page.get_by_test_id(f"dev-login-link-{role}").click()
    page.wait_for_url(lambda url: "/dashboard" in url or "/payroll" in url)
    settle(page)


def open_role(browser, role):
    """A page signed in through the Development Quick Login (admin, hr, project-manager, team-lead, employee)."""
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    dev_login(page, role)
    return page


def test_no_salary_empty_states():
    """PR-260 / PR-261: an employee without a salary (the quick-login employee) sees "No salary structure on file" on
    My Salary and "No payslips yet" on My Payslips."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        employee = open_role(browser, "employee")
        if props_at(employee, f"{BASE_URL}/payroll/my/salary")["salary"]:
            pytest.skip("the quick-login employee now has a salary")

        expect(employee.locator("main")).to_contain_text("No salary structure on file")
        props = props_at(employee, f"{BASE_URL}/payroll/my/payslips")
        assert not props["payslips"]
        expect(employee.locator("main")).to_contain_text("No payslips yet")

        browser.close()
