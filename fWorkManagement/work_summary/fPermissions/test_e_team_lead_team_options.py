from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser_as, open_hours, page_props, team_select


def test_team_lead_team_options():
    """WS-044: a team lead can filter by employee, but the Team picker only offers their own teams."""
    with sync_playwright() as p:
        admin_browser, admin = open_browser_as(p, "admin")
        open_hours(admin)
        all_teams = [t["name"] for t in page_props(admin)["teams"]]
        admin_browser.close()

        browser, page = open_browser_as(p, "team-lead")
        open_hours(page)
        props = page_props(page)
        own_teams = [t["name"] for t in props["teams"]]
        assert props["canViewAll"] is False and props["canApprove"] is True, props
        assert own_teams and set(own_teams) < set(all_teams), (own_teams, all_teams)

        options = [o.strip() for o in team_select(page).locator("option").all_inner_texts()]
        assert options == ["All Teams"] + own_teams, options

        browser.close()
