from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import open_browser, open_hours, page_props, open_log_dialog, today


def test_dialog_defaults():
    """WS-009: the Log Hours dialog opens with today's date, no project picked, empty hours/description,
    and lists exactly the projects the user can log against."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_hours(page)
        projects = [proj["name"] for proj in page_props(page)["assignableProjects"]]

        dialog = open_log_dialog(page)
        expect(dialog).to_contain_text("Record your work and tasks")
        project = dialog.locator("select")
        expect(project).to_have_value("")
        options = project.locator("option").all_inner_texts()
        assert options[0].strip() == "-- Select a project --", options
        assert [o.strip() for o in options[1:]] == projects, (options, projects)
        expect(dialog.locator("input[type=date]")).to_have_value(today().isoformat())
        expect(dialog.locator("input[type=number]")).to_have_value("")
        expect(dialog.locator("input[type=number]")).to_have_attribute("max", "24")
        expect(dialog.locator("textarea")).to_have_value("")
        expect(dialog.locator("textarea")).to_have_attribute("placeholder", "What did you work on?")

        browser.close()
