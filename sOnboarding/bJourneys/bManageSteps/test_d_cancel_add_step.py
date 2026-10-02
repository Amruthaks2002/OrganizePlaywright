from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, main_content, add_step_dialog, vue_select, open_steps,
    step_cards, delete_journeys, SESSIONS,
)


def test_cancel_add_step():
    """MS-004: Cancel closes Add Step without adding the step."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            journey_id = create_journey(page, name)
            main_content(page).get_by_role("button", name="Add Step").first.click()
            dialog = add_step_dialog(page)
            vue_select(page, dialog, "Select a session", SESSIONS[0])
            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()

            open_steps(page, journey_id)
            expect(main_content(page).get_by_text("0 steps")).to_be_visible()
            expect(step_cards(page)).to_have_count(0)
        finally:
            delete_journeys(page, name)

        browser.close()
