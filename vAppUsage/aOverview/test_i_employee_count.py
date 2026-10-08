import re
from playwright.sync_api import sync_playwright
from utils.app_usage_helper import open_browser, load, kpi, users_total, APP_USAGE_URL


def test_employee_count():
    """AU-009: the "of M employees" total equals the number of active users on the Users page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        active_users = users_total(page, "?is_active=1")

        load(page, APP_USAGE_URL)
        subtitle = kpi(page, "On the latest version")[1]
        employees = int(re.search(r"of (\d+) employees", subtitle).group(1))
        assert employees == active_users, (subtitle, active_users)

        browser.close()
