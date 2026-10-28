import pytest
from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import open_ai_as, open_ai_as_employee, textarea, AI_URL


@pytest.mark.parametrize("role", ["employee", "hr", "team-lead", "project-manager"])
def test_all_roles_can_open(role):
    """AI-002: Employee, HR, Team Lead and Project Manager all have the AI Assistant menu item and can open /ai."""
    with sync_playwright() as p:
        # the employee side uses the dedicated AI test account
        browser, page = open_ai_as_employee(p) if role == "employee" else open_ai_as(p, role)

        assert page.url == AI_URL
        expect(textarea(page)).to_be_editable()

        browser.close()
