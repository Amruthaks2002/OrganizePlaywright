from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_steps, main_content, add_step_dialog, vue_select_options, SAMPLE_JOURNEY, SAMPLE_JOURNEY_ID,
    SESSIONS,
)


def test_add_step_dialog():
    """MS-003: Add Step opens a dialog for the journey with a required Project Session picker
    listing the project sessions."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_steps(page, SAMPLE_JOURNEY_ID)

        main_content(page).get_by_role("button", name="Add Step").click()
        dialog = add_step_dialog(page)
        expect(dialog.get_by_role("heading", name=f"Add Step to {SAMPLE_JOURNEY}")).to_be_visible()
        expect(dialog.get_by_text("Project Session *")).to_be_visible()
        options = vue_select_options(page, dialog, "Select a session")
        for session in SESSIONS:
            assert session in options, options
        expect(dialog.get_by_role("button", name="Cancel")).to_be_visible()
        expect(dialog.get_by_role("button", name="Add Step")).to_be_visible()

        dialog.get_by_role("button", name="Cancel").click()

        browser.close()
