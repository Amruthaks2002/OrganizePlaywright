import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_journey, unique_journey_name, open_journeys, journey_card, journey_dialog,
    fill_journey_form, delete_journeys,
)


def set_active(page, name, active):
    open_journeys(page)
    journey_card(page, name).get_by_role("button", name="Edit").click()
    dialog = journey_dialog(page, "Edit Onboarding Journey")
    fill_journey_form(page, dialog, active=active)
    dialog.get_by_role("button", name="Update Journey").click()
    expect(dialog).to_be_hidden()
    open_journeys(page)


def test_deactivate_and_activate():
    """OJ-017: switching Active off in Edit marks the journey Inactive, and switching it on makes it Active again."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_journey_name()
        try:
            create_journey(page, name)

            set_active(page, name, False)
            expect(journey_card(page, name).get_by_text("Inactive", exact=True)).to_be_visible()

            set_active(page, name, True)
            expect(journey_card(page, name).get_by_text(re.compile(r"^Active$"))).to_be_visible()
            expect(journey_card(page, name).get_by_text("Inactive", exact=True)).to_have_count(0)
        finally:
            delete_journeys(page, name)

        browser.close()
