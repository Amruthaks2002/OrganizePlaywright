from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_steps, main_content, add_step_dialog, step_cards, SAMPLE_JOURNEY_ID


def test_session_required():
    """MS-006: Add Step without a session shows "The project session id field is required." and adds nothing."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_steps(page, SAMPLE_JOURNEY_ID)

        main_content(page).get_by_role("button", name="Add Step").click()
        dialog = add_step_dialog(page)
        dialog.get_by_role("button", name="Add Step").click()
        expect(dialog.get_by_text("The project session id field is required.")).to_be_visible()

        dialog.get_by_role("button", name="Cancel").click()
        open_steps(page, SAMPLE_JOURNEY_ID)
        expect(step_cards(page)).to_have_count(3)

        browser.close()
