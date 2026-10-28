from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, open_ai_as, main_content, EMPLOYEE_NAME


def test_greeting_per_user():
    """AI-007: Each user is greeted with their own name - the employee never sees the admin's name, and vice versa."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)
        employee_text = main_content(page).inner_text()
        browser.close()

        browser, page = open_ai_as(p, "admin")
        admin_text = main_content(page).inner_text()
        browser.close()

    assert f"Hi {EMPLOYEE_NAME} !" in employee_text
    assert "Admin User" not in employee_text
    assert "Hi Admin User !" in admin_text
    assert f"Hi {EMPLOYEE_NAME} !" not in admin_text
