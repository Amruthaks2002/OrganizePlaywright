from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, add_step, open_steps, step_titles, step_cards, expect_toast,
    delete_journeys, SESSIONS,
)


def test_reorder_steps():
    """MS-008: Move down / Move up reorder the steps, and the order is saved."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            journey_id = create_journey(page, name)
            for session in SESSIONS:
                add_step(page, session)
            open_steps(page, journey_id)
            assert step_titles(page) == SESSIONS, step_titles(page)

            step_cards(page).first.get_by_role("button", name="Move down").click()
            expect_toast(page, "Steps reordered successfully.")
            open_steps(page, journey_id)
            assert step_titles(page) == SESSIONS[::-1], step_titles(page)

            step_cards(page).last.get_by_role("button", name="Move up").click()
            expect_toast(page, "Steps reordered successfully.")
            open_steps(page, journey_id)
            assert step_titles(page) == SESSIONS, step_titles(page)
        finally:
            delete_journeys(page, name)

        browser.close()
