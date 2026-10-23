import re
from datetime import datetime
from playwright.sync_api import sync_playwright
from utils.app_usage_helper import (open_browser, load, page_props, main_content, install_rows, installs_count,
                                    APP_USAGE_URL, INSTALL_COLUMNS, PLATFORMS, STATUSES, RELATIVE_TIME)


def local(iso):
    return datetime.fromisoformat(iso).astimezone()


def test_table_columns_and_rows():
    """AI-001: the Installs table has the right columns, each row shows the user, platform, version + build,
    status, device, install date and last used (exact time on hover), most recently used first."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        load(page, APP_USAGE_URL)
        installs = page_props(page)["installs"]
        main = main_content(page)

        headers = [h.strip().lower() for h in main.locator("table thead th").all_inner_texts()]
        assert headers == [c.lower() for c in INSTALL_COLUMNS], headers

        rows = install_rows(page)
        assert installs_count(page) == installs["total"]
        assert len(rows) == len(installs["data"]) == min(installs["total"], installs["per_page"])

        for row, data in zip(rows, installs["data"]):
            assert row["name"] == data["user"]["name"] and row["email"] == data["user"]["email"], row
            assert re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", row["email"]), row
            assert row["platform"] == PLATFORMS[data["platform"]], row
            build = f"+{data['build_number']}" if data["build_number"] else ""
            assert row["version"] == f"{data['app_version']}{build}", row
            assert row["status"] == STATUSES[data["status"]], row
            assert row["device"] == [data["device_model"] or "—", data["os_version"] or "—"], row

            installed = local(data["first_seen_at"])
            assert row["installed"] == f"{installed.day} {installed:%b}, {installed.year}", row
            last_seen = local(data["last_seen_at"])
            assert row["last_used_title"] == f"{last_seen.day} {last_seen:%b}, {last_seen.year}, {last_seen:%I:%M %p}", row
            assert RELATIVE_TIME.search(row["last_used"]), row

        last_used = [local(d["last_seen_at"]) for d in installs["data"]]
        assert last_used == sorted(last_used, reverse=True), last_used

        browser.close()
