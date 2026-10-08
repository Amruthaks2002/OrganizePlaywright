from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser_as, open_hours, open_tab, export_button, EXPORT_URL


def test_export_restricted():
    """WS-045: only roles that can see everyone's hours get Export - employee, team lead and project manager
    have no Export button and the export endpoint refuses them (403); HR has it."""
    with sync_playwright() as p:
        for role in ["employee", "team-lead", "project-manager"]:
            browser, page = open_browser_as(p, role)
            open_hours(page)
            open_tab(page, "Comp Hours")
            expect(export_button(page)).to_have_count(0)
            status = page.request.get(f"{EXPORT_URL}?team_id=", max_redirects=0).status
            assert status == 403, (role, status)
            browser.close()

        browser, page = open_browser_as(p, "hr")
        open_hours(page)
        open_tab(page, "Comp Hours")
        expect(export_button(page)).to_be_visible()
        browser.close()
