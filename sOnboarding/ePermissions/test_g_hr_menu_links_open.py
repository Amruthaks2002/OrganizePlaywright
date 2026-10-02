from playwright.sync_api import sync_playwright
from utils.onboarding_helper import open_browser_as, SIDEBAR_CHILDREN


def test_hr_menu_links_open():
    """PM-007: every Onboarding menu link HR is shown opens for HR.

    Known bug: HR's menu has Directory and Journeys, but both pages return 403 Forbidden for HR
    (only Journey Progress opens). Either the links should be hidden or HR should be allowed in.
    This test fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "hr")
        page.get_by_test_id("sidebar-parent-onboarding").click()

        shown = [child for child in SIDEBAR_CHILDREN if page.get_by_test_id(f"sidebar-child-{child}").is_visible()]
        assert shown, "HR should see at least one Onboarding link"
        forbidden = []
        for child in shown:
            response = page.goto(SIDEBAR_CHILDREN[child])
            if response.status == 403:
                forbidden.append(child)
        assert not forbidden, f"HR's Onboarding menu links to pages HR can't open: {forbidden}"

        browser.close()
