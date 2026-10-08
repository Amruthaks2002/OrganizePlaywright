import re
from playwright.sync_api import sync_playwright
from utils.app_usage_helper import open_browser, load, kpi, all_installs, APP_USAGE_URL


def test_app_users_count():
    """AU-010: the "N of M employees use the app" count equals the number of different people with an install."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        people = {i["user"]["id"] for i in all_installs(page)}

        load(page, APP_USAGE_URL)
        subtitle = kpi(page, "On the latest version")[1]
        app_users = int(re.match(r"(\d+) of", subtitle).group(1))
        assert app_users == len(people), (subtitle, len(people))

        browser.close()
