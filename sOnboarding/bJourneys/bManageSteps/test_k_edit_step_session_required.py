from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_steps, step_cards, modal, SAMPLE_JOURNEY_ID


def test_edit_step_session_required():
    """MS-011: a step's session can be swapped but not removed - Edit step has no Clear option,
    so the step can't be saved without a session."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_steps(page, SAMPLE_JOURNEY_ID)

        step_cards(page).first.get_by_role("button", name="Edit step").click()
        dialog = modal(page, "Edit Step for")
        expect(dialog.locator(".vs__selected")).to_have_count(1)
        expect(dialog.get_by_role("button", name="Clear Selected")).to_be_hidden()

        dialog.get_by_role("button", name="Cancel").click()

        browser.close()
