from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_steps, step_cards, step_titles, modal, vue_select, SAMPLE_JOURNEY, SAMPLE_JOURNEY_ID,
)


def test_edit_step_prefilled_and_cancel():
    """MS-009: Edit step opens with the step's session selected, and Cancel keeps the step unchanged."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_steps(page, SAMPLE_JOURNEY_ID)
        before = step_titles(page)

        step_cards(page).nth(1).get_by_role("button", name="Edit step").click()
        dialog = modal(page, "Edit Step for")
        expect(dialog.get_by_role("heading", name=f"Edit Step for {SAMPLE_JOURNEY}")).to_be_visible()
        expect(dialog.locator(".vs__selected")).to_have_text(before[1])
        expect(dialog.get_by_role("button", name="Save Changes")).to_be_visible()

        vue_select(page, dialog, None, "onb2")
        dialog.get_by_role("button", name="Cancel").click()
        expect(dialog).to_be_hidden()

        open_steps(page, SAMPLE_JOURNEY_ID)
        assert step_titles(page) == before, step_titles(page)

        browser.close()
