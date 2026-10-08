from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser_as, open_from_sidebar, main_content


def test_sidebar_entry_all_roles():
    """WS-047: every role reaches Work Summary from Work Management in the sidebar; only roles that see
    everyone's hours get the 'Review and manage' subtitle."""
    subtitles = {"admin": "Review and manage employee hours and compensatory time.",
                 "hr": "Review and manage employee hours and compensatory time.",
                 "team-lead": "Log hours and track compensation.",
                 "project-manager": "Log hours and track compensation.",
                 "employee": "Log hours and track compensation."}
    with sync_playwright() as p:
        for role, subtitle in subtitles.items():
            browser, page = open_browser_as(p, role)
            open_from_sidebar(page)
            expect(main_content(page)).to_contain_text(subtitle)
            browser.close()
