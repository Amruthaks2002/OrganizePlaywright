import re
from playwright.sync_api import sync_playwright
from utils.onboarding_helper import open_browser, open_journeys, main_content, journey_stats


def test_counters_match_cards():
    """OJ-003: Total Journeys, Active and Total Steps match the journey cards on the page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_journeys(page)

        links = main_content(page).get_by_role("link", name="Manage Steps")
        cards = [links.nth(i).locator("xpath=ancestor::div[.//a[normalize-space()='Manage Steps']]"
                                       "[count(.//a[normalize-space()='Manage Steps']) = 1][last()]").inner_text()
                 for i in range(links.count())]
        active = sum(1 for text in cards if re.search(r"^Active$", text, re.M))
        steps = sum(int(re.search(r"^(\d+)\s*\n\s*steps?$", text, re.M).group(1)) for text in cards)

        assert journey_stats(page) == (len(cards), active, steps), (journey_stats(page), len(cards), active, steps)

        browser.close()
