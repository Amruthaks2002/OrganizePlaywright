from datetime import timedelta
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, pick_employee, selected_employee, team_select,
                                       from_date, to_date, clear_button, wait_for_logs, page_props, first_of_month,
                                       today, EMPLOYEE_NAME)


def test_clear_filters():
    """WS-025: Clear only appears once an employee or team is picked, and puts every filter (employee, team,
    dates) back to its default."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        team = page_props(page)["teams"][0]
        open_tab(page, "Regular Hours")
        expect(clear_button(page)).to_have_count(0)

        # picking an employee and a team together is WS-030, so try each on its own
        for pick in [lambda: pick_employee(page, EMPLOYEE_NAME),
                     lambda: team_select(page).select_option(str(team["id"]))]:
            wait_for_logs(page, lambda: from_date(page).fill((today() - timedelta(days=60)).isoformat()))
            expect(clear_button(page)).to_have_count(0)  # a date change alone doesn't offer Clear
            wait_for_logs(page, pick)
            expect(clear_button(page)).to_be_visible()

            wait_for_logs(page, lambda: clear_button(page).click())
            expect(team_select(page)).to_have_value("")
            expect(selected_employee(page)).to_have_count(0)
            expect(from_date(page)).to_have_value(first_of_month().isoformat())
            expect(to_date(page)).to_have_value(today().isoformat())
            expect(clear_button(page)).to_have_count(0)

        browser.close()
