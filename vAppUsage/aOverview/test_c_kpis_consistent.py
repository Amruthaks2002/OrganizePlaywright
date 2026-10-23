from datetime import datetime, timedelta, timezone
from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, page_props, kpi, platform_breakdown, all_installs,
                                    APP_USAGE_URL, ACTIVE_DAYS)


def test_kpis_consistent():
    """AU-003: the cards agree with each other and with the chart, the Platforms card and the installs."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        installs = all_installs(page)
        load(page, APP_USAGE_URL)
        trend = page_props(page)["trend"]

        today = int(kpi(page, "Active today")[0])
        week, month_text = kpi(page, "Active this week")
        month = int(month_text.split()[0])
        in_use = int(kpi(page, "Installs in use")[0])

        assert today <= int(week) <= month, (today, week, month)
        assert today == trend[-1]["active_users"], (today, trend[-1])
        assert sum(count for count, _ in platform_breakdown(page).values()) == in_use

        # "An install is in use if it was opened in the last 30 days."
        cutoff = datetime.now(timezone.utc) - timedelta(days=ACTIVE_DAYS)
        opened_recently = [i for i in installs if datetime.fromisoformat(i["last_seen_at"]) >= cutoff]
        assert len(opened_recently) == in_use, (len(opened_recently), in_use)

        browser.close()
