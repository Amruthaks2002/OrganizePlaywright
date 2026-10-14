from playwright.sync_api import sync_playwright
from utils.app_releases_helper import (open_browser, page_props, reload_props, current_releases, restore_releases,
                                       publish, expect_toast, unique_tag, admin_name, values, card_values,
                                       published_text, history_rows, visible_row, expected_row, current_ids)


def test_publish_with_messages():
    """AR-013: publishing an Android release with both messages adds a new Current row at the top of History, updates
    the card, and the previous Android release loses its Current badge and Edit button.
    Keeps Android's latest / minimum so no real install is affected; the snapshot is restored afterwards."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        before = page_props(page)
        old = before["current"]["android"]
        tag = unique_tag()
        expected = {"latest_version": old["latest_version"], "min_version": old["min_version"],
                    "optional_message": f"AR-013 optional {tag}", "mandatory_message": f"AR-013 mandatory {tag}"}
        try:
            publish(page, "android", **expected)
            expect_toast(page, f"Android release {old['latest_version']} published.")

            after = reload_props(page)
            new = after["current"]["android"]
            assert new["id"] != old["id"], new
            assert values(new) == expected, new
            assert new["created_by"] == admin_name(page), new
            assert after["history"]["total"] == before["history"]["total"] + 1

            assert card_values(page, "android") == {
                "latest": expected["latest_version"], "min": expected["min_version"],
                "published": f"Published {published_text(new['created_at'])} by {new['created_by']}"}

            rows = history_rows(page)
            ids = [r["id"] for r in after["history"]["data"]]
            assert ids[0] == new["id"], ids
            assert visible_row(rows[0]) == expected_row(new, current_ids(after)), rows[0]
            assert "Current" in rows[0]["badges"] and rows[0]["has_edit"], rows[0]
            previous = rows[ids.index(old["id"])]
            assert "Current" not in previous["badges"] and not previous["has_edit"], previous
        finally:
            restore_releases(page, snapshot)

        browser.close()
