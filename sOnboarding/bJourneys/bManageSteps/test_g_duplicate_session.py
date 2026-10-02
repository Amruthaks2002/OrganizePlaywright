from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, add_step, main_content, add_step_dialog, vue_select,
    open_steps, step_titles, delete_journeys, SESSIONS,
)


def test_duplicate_session():
    """MS-007: adding a session that's already a step of the journey doesn't add it twice."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            journey_id = create_journey(page, name)
            add_step(page, SESSIONS[0])

            main_content(page).get_by_role("button", name="Add Step").first.click()
            dialog = add_step_dialog(page)
            vue_select(page, dialog, "Select a session", SESSIONS[0])
            dialog.get_by_role("button", name="Add Step").click()
            page.wait_for_timeout(2500)

            open_steps(page, journey_id)
            assert step_titles(page) == [SESSIONS[0]], step_titles(page)
        finally:
            delete_journeys(page, name)

        browser.close()
