from datetime import datetime
from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, page_props, recent_activity_items, APP_USAGE_URL,
                                    ACTIVITY_TYPES, PLATFORMS, STATUSES, RELATIVE_TIME, sentence_part)


def test_entries_newest_first():
    """RA-001: Recent activity lists events newest first; each shows who, what, platform · version, the
    version status and when (exact time on hover)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, APP_USAGE_URL)
        data = page_props(page)["recentActivity"]
        items = recent_activity_items(page)
        assert items and len(items) == len(data), (len(items), len(data))

        for item, event in zip(items, data):
            assert item["name"] == event["user"]["name"], item
            assert item["action"] == sentence_part(ACTIVITY_TYPES[event["action"]]), item
            assert item["platform"] == PLATFORMS[event["platform"]], item
            assert item["version"] == event["app_version"], item
            assert item["status"] == STATUSES[event["status"]], item
            assert RELATIVE_TIME.search(item["time"]), item
            when = datetime.fromisoformat(item["datetime"]).astimezone()
            assert item["title"] == f"{when.day} {when:%b}, {when.year}, {when:%I:%M %p}", item

        times = [datetime.fromisoformat(i["datetime"]) for i in items]
        assert times == sorted(times, reverse=True), times

        browser.close()
