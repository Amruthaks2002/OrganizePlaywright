from datetime import datetime
from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, recent_activity_items, activity_rows, activity_time,
                                    sentence_part, APP_USAGE_URL, ACTIVITIES_URL)


def test_matches_activity_log():
    """RA-004: Recent activity shows the same, latest events as the top of the App Activity page."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, APP_USAGE_URL)
        items = recent_activity_items(page)

        load(page, ACTIVITIES_URL)
        rows = activity_rows(page)
        # the App Activity page defaults to the last 30 days, so only compare what both can show
        oldest_row = activity_time(rows[-1]["time"]) if rows else datetime.max
        items = [i for i in items
                 if datetime.fromisoformat(i["datetime"]).astimezone().replace(tzinfo=None) >= oldest_row]
        assert items, "no recent activity in the last 30 days"

        for item, row in zip(items, rows):
            assert item["name"] == row["name"], (item, row)
            assert item["action"] == sentence_part(row["activity"]), (item, row)
            assert item["platform"] == row["platform"] and item["version"] == row["version"], (item, row)
            when = datetime.fromisoformat(item["datetime"]).astimezone().replace(tzinfo=None)
            assert when == activity_time(row["time"]), (item, row)

        browser.close()
