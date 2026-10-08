from playwright.sync_api import sync_playwright
from utils.app_usage_helper import open_browser_as, expect_forbidden, SIDEBAR_LINK, APP_USAGE_URL, ACTIVITIES_URL


def test_team_lead_blocked():
    """PM-003: a team lead has no App Usage menu item and gets 403 Forbidden on App Usage and App Activity."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "team-lead")

        assert page.get_by_test_id(SIDEBAR_LINK).count() == 0
        for url in [APP_USAGE_URL, ACTIVITIES_URL]:
            expect_forbidden(page, url)

        browser.close()
