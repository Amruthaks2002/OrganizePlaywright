import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, open_progress, main_content, vue_select, vue_select_options, progress_rows, settle,
    open_journeys, SAMPLE_JOURNEY,
)

JOURNEY = "The Success Route"


def test_journey_filter():
    """JP-007: the journey filter offers the onboarding journeys and shows only employees on the chosen one."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_progress(page)
        main = main_content(page)

        options = vue_select_options(page, main, "All Journeys")
        for journey in [JOURNEY, SAMPLE_JOURNEY, "Employe onboarding"]:
            assert journey in options, options

        vue_select(page, main, "All Journeys", JOURNEY)
        expect(page).to_have_url(re.compile(r"journey=\d+|journey=The"))
        settle(page)
        rows = progress_rows(page)
        expect(rows.first).to_be_visible()
        for text in rows.all_inner_texts():
            assert JOURNEY in text, text

        browser.close()
