from playwright.sync_api import sync_playwright
from utils.app_usage_helper import open_browser, load, page_props, all_kpis, APP_USAGE_URL


def test_kpi_cards():
    """AU-002: each summary card shows the right number and subtitle."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, APP_USAGE_URL)
        s = page_props(page)["summary"]
        kpis = all_kpis(page)

        assert kpis["Active today"] == (str(s["daily_active"]), "users opened the app today"), kpis
        assert kpis["Active this week"] == (str(s["weekly_active"]), f"{s['monthly_active']} in the last 30 days"), kpis
        assert kpis["Installs in use"] == (
            str(s["active_installs"]),
            f"{s['android_installs']} Android · {s['ios_installs']} iOS · {s['new_installs']} new"), kpis
        value, subtitle = kpis["On the latest version"]
        if s["active_installs"]:
            assert value == f"{int(s['on_latest'] * 100 / s['active_installs'] + 0.5)}%", (value, s)
        assert subtitle == f"{s['app_users']} of {s['employees']} employees use the app", subtitle

        browser.close()
