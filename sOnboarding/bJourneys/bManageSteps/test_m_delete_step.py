from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, add_step, open_steps, step_cards, step_titles, modal,
    expect_toast, main_content, delete_journeys, SESSIONS,
)


def test_delete_step():
    """MS-013: confirming Delete step removes it and updates the counts."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            journey_id = create_journey(page, name)
            for session in SESSIONS:
                add_step(page, session)

            open_steps(page, journey_id)
            step_cards(page).first.get_by_role("button", name="Delete step").click()
            modal(page, "Delete Step").get_by_role("button", name="Delete", exact=True).click()
            expect_toast(page, "Step deleted successfully.")

            open_steps(page, journey_id)
            assert step_titles(page) == SESSIONS[1:], step_titles(page)
            expect(main_content(page).get_by_text("1 step", exact=True)).to_be_visible()
        finally:
            delete_journeys(page, name)

        browser.close()
