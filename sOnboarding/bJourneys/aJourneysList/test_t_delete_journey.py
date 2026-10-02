from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, open_journeys, journey_card, modal, expect_toast,
    main_content, delete_journeys,
)


def test_delete_journey():
    """OJ-020: confirming Delete removes the journey."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            create_journey(page, name)
            open_journeys(page)
            journey_card(page, name).get_by_role("button", name="Delete").click()
            modal(page, "Delete Journey").get_by_role("button", name="Delete", exact=True).click()
            expect_toast(page, "Onboarding journey deleted successfully.")

            open_journeys(page)
            expect(main_content(page).get_by_text(name, exact=True)).to_have_count(0)
        finally:
            delete_journeys(page, name)

        browser.close()
