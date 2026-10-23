from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, add_step, open_steps, step_titles, step_cards, main_content,
    delete_journeys, SESSIONS,
)


def test_add_step():
    """MS-005: adding a project session adds it as a required step and updates the counts."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            journey_id = create_journey(page, name)
            add_step(page, SESSIONS[0])

            open_steps(page, journey_id)
            assert step_titles(page) == [SESSIONS[0]], step_titles(page)
            expect(main_content(page).get_by_text("1 step", exact=True)).to_be_visible()
            expect(main_content(page).get_by_text("1 required", exact=True)).to_be_visible()
            expect(step_cards(page).first.get_by_text("Required", exact=True)).to_be_visible()
        finally:
            delete_journeys(page, name)

        browser.close()
