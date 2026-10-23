from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, logs_api, log_hours, rows, delete_log_api,
                                       last_weekday, fmt, NO_DESCRIPTION, PROJECT, ADMIN_ID, ADMIN_NAME)

HOURS = 7


def test_no_description():
    """WS-017: the description is optional - the log is saved and its row shows '–' with no View button."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        day = last_weekday()
        new_ids = []
        try:
            open_hours(page)
            before = {log["id"] for log in logs_api(page, start=day, end=day)["timeLogs"]["data"]}
            log_hours(page, "", hours=HOURS, work_date=day)
            new_ids = [log["id"] for log in logs_api(page, start=day, end=day)["timeLogs"]["data"]
                       if log["id"] not in before]
            assert len(new_ids) == 1, new_ids
            log = next(log for log in logs_api(page, start=day, end=day)["timeLogs"]["data"] if log["id"] == new_ids[0])
            assert log["description"] is None and log["user_id"] == ADMIN_ID, log

            open_tab(page, "Regular Hours")
            row = rows(page).filter(has_text=ADMIN_NAME).filter(has_text=fmt(day)).filter(has_text=f"{HOURS}.00") \
                .filter(has_text=PROJECT).first
            expect(row).to_be_visible()
            expect(row.locator("td").last.locator("span").first).to_have_text(NO_DESCRIPTION)
            expect(row.get_by_role("button", name="View")).to_have_count(0)
        finally:
            for log_id in new_ids:
                delete_log_api(page, log_id)
            browser.close()
