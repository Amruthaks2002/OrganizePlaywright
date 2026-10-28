from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as_employee, main_content, EMPLOYEE_NAME


def test_greeting_shows_user_name():
    """AI-005: The welcome greeting is filled with the signed-in employee's name and no {{placeholder}} is left raw."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        expect(main_content(page).get_by_text(f"Hi {EMPLOYEE_NAME} !")).to_be_visible()
        assert "{{" not in main_content(page).inner_text()

        browser.close()
