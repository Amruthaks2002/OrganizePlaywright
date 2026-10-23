from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_steps, step_cards, step_titles, modal, SAMPLE_JOURNEY_ID


def test_cancel_delete_step():
    """MS-012: Delete step asks for confirmation, and Cancel keeps the step."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_steps(page, SAMPLE_JOURNEY_ID)
        before = step_titles(page)

        step_cards(page).first.get_by_role("button", name="Delete step").click()
        dialog = modal(page, "Delete Step")
        expect(dialog.get_by_text("Are you sure you want to delete this step?")).to_be_visible()
        dialog.get_by_role("button", name="Cancel").click()
        expect(dialog).to_be_hidden()

        open_steps(page, SAMPLE_JOURNEY_ID)
        assert step_titles(page) == before, step_titles(page)

        browser.close()
