from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, pick_employee, selected_employee, team_select,
                                       team_members, wait_for_logs, page_props, LOGS_URL, EMPLOYEE_ID, EMPLOYEE_NAME)


def test_employee_and_team_together():
    """WS-030: picking a team after an employee (one of that team's members) keeps both filters.

    Known bug: choosing the second filter wipes both - the Team picker snaps back to All Teams, the employee
    is cleared and the table reloads unfiltered. Same the other way round (team first, then employee).
    This test fails until that's fixed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        team = next(t for t in page_props(page)["teams"] if EMPLOYEE_ID in team_members(page, t["id"]))
        open_tab(page, "Regular Hours")

        wait_for_logs(page, lambda: pick_employee(page, EMPLOYEE_NAME))
        with page.expect_request(lambda r: r.url.startswith(LOGS_URL)) as request:
            wait_for_logs(page, lambda: team_select(page).select_option(str(team["id"])))

        expect(team_select(page)).to_have_value(str(team["id"]))
        expect(selected_employee(page)).to_have_text(EMPLOYEE_NAME)
        query = parse_qs(urlparse(request.value.url).query)
        assert query.get("hours[team]") == [str(team["id"])], query
        assert query.get("hours[employee_id]") == [str(EMPLOYEE_ID)], query

        browser.close()
