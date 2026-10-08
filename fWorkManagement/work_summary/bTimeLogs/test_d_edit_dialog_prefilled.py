from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import (open_browser, open_hours, open_tab, page_props, log_hours, open_edit, unique_desc,
                                       cleanup_logs, last_weekday, PROJECT)


def test_edit_dialog_prefilled():
    """WS-019: Edit Time Log opens with the log's values filled in, and the project is locked."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        desc = unique_desc("prefilled")
        day = last_weekday()
        try:
            open_hours(page)
            project_id = next(proj["id"] for proj in page_props(page)["assignableProjects"] if proj["name"] == PROJECT)
            log_hours(page, desc, hours=5, work_date=day)
            open_tab(page, "Regular Hours")

            dialog = open_edit(page, desc)
            project = dialog.locator("select")
            expect(project).to_be_disabled()
            expect(project).to_have_value(str(project_id))
            expect(dialog.get_by_text("Project cannot be changed after creation")).to_be_visible()
            expect(dialog.locator("input[type=date]")).to_have_value(day.isoformat())
            assert float(dialog.locator("input[type=number]").input_value()) == 5
            expect(dialog.locator("textarea")).to_have_value(desc)
            expect(dialog.get_by_role("button", name="Update")).to_be_enabled()
        finally:
            cleanup_logs(page, desc)
            browser.close()
