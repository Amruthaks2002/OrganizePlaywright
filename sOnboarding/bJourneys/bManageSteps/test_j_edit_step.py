from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, add_step, open_steps, step_cards, step_titles, modal,
    vue_select, delete_journeys, SESSIONS,
)


def test_edit_step():
    """MS-010: Save Changes switches the step to another session."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            journey_id = create_journey(page, name)
            add_step(page, SESSIONS[0])

            step_cards(page).first.get_by_role("button", name="Edit step").click()
            dialog = modal(page, "Edit Step for")
            vue_select(page, dialog, None, SESSIONS[1])
            dialog.get_by_role("button", name="Save Changes").click()
            expect(dialog).to_be_hidden()

            open_steps(page, journey_id)
            assert step_titles(page) == [SESSIONS[1]], step_titles(page)
        finally:
            delete_journeys(page, name)

        browser.close()
