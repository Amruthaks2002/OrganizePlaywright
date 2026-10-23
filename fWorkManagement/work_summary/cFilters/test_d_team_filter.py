from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, page_props, team_members, team_select,
                                       wait_for_logs, log_hours, row, data_rows, row_cells, unique_desc, cleanup_logs,
                                       ADMIN_ID)


def test_team_filter():
    """WS-024: the Team filter only shows logs of that team's members - Admin's log is listed under a team
    Admin belongs to and hidden under one Admin isn't in."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("team")
        try:
            open_hours(page)
            members = {t["id"]: team_members(page, t["id"]) for t in page_props(page)["teams"]}
            names = {t["id"]: t["name"] for t in page_props(page)["teams"]}
            own_team = next(t for t, m in members.items() if ADMIN_ID in m)
            other_team = next(t for t, m in members.items() if ADMIN_ID not in m)

            log_hours(page, desc)
            open_tab(page, "Regular Hours")

            data = wait_for_logs(page, lambda: team_select(page).select_option(str(own_team)))
            expect(row(page, desc)).to_have_count(1)
            assert {log["user_id"] for log in data["timeLogs"]["data"]} <= set(members[own_team]), names[own_team]
            assert {row_cells(tr)[0] for tr in data_rows(page)} <= set(members[own_team].values())

            data = wait_for_logs(page, lambda: team_select(page).select_option(str(other_team)))
            expect(row(page, desc)).to_have_count(0)
            assert {log["user_id"] for log in data["timeLogs"]["data"]} <= set(members[other_team]), names[other_team]
        finally:
            cleanup_logs(page, desc)
            browser.close()
