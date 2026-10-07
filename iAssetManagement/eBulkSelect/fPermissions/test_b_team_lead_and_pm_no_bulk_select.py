from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import open_browser_as, open_assets, main_content, dock


def test_team_lead_and_pm_no_bulk_select():
    """BS-030: team leads and project managers get the "assigned to you" view with no checkboxes
    and no dock."""
    with sync_playwright() as p:
        for role in ["team-lead", "project-manager"]:
            browser, page = open_browser_as(p, role)
            open_assets(page)
            main = main_content(page)
            expect(main.get_by_text("Hardware currently assigned to you.")).to_be_visible()
            expect(main.locator("input[type=checkbox]")).to_have_count(0)
            expect(dock(page)).to_have_count(0)
            browser.close()
