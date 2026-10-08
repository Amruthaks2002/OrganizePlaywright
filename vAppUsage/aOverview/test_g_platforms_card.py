from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, open_app_usage, platform_breakdown, filter_installs,
                                    install_rows, kpi, PLATFORMS, ACTIVE_DAYS)


def test_platforms_card():
    """AU-007: the Platforms card counts installs in use per platform, with percentages that add up to 100%."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_app_usage(page)
        breakdown = platform_breakdown(page)
        assert list(breakdown) == list(PLATFORMS.values()), breakdown

        total = sum(count for count, _ in breakdown.values())
        assert total == int(kpi(page, "Installs in use")[0])
        for label, (count, percent) in breakdown.items():
            expected = int(count * 100 / total + 0.5) if total else 0
            assert percent == f"{expected}%", (label, count, percent)

        # each count matches that platform's installs opened in the last 30 days
        cutoff = datetime.now() - timedelta(days=ACTIVE_DAYS)
        for value, label in PLATFORMS.items():
            filter_installs(page, platform=value)
            in_use = [r for r in install_rows(page)
                      if datetime.strptime(r["last_used_title"], "%d %b, %Y, %I:%M %p") >= cutoff]
            assert len(in_use) == breakdown[label][0], (label, len(in_use), breakdown[label])

        browser.close()
