import datetime

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, open_tasks, open_task_details, task_detail,
                                    create_project, add_task, delete_project, unique_tag, today, ADMIN,
                                    QA_PROJECT_PREFIX, QA_TASK_PREFIX)


def test_task_details():
    """DB-016: clicking a task opens Task Details Overview with its description, assigner, status,
    deadline and project; Close and the X both dismiss it."""
    tag = unique_tag()
    project, task = f"{QA_PROJECT_PREFIX} {tag}", f"{QA_TASK_PREFIX} {unique_tag()}"
    due = today() + datetime.timedelta(days=3)
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            project_id = create_project(page, project)
            add_task(page, project_id, task, "details description", due=due)
            open_dashboard(page)
            open_tasks(page)

            dialog = open_task_details(page, task)
            expect(dialog.get_by_text(task, exact=True)).to_be_visible()
            assert task_detail(dialog, "Description") == "details description"
            assert task_detail(dialog, "Assigned By") == ADMIN["name"]
            assert task_detail(dialog, "Status") == "To Do"
            assert task_detail(dialog, "Deadline") == due.strftime("%-d %b, %Y")
            assert task_detail(dialog, "Project") == project
            expect(dialog.get_by_role("button", name="Start Task")).to_be_visible()
            dialog.get_by_role("button", name="Close").click()
            expect(dialog).to_be_hidden()

            dialog = open_task_details(page, task)
            dialog.locator("button").first.click()  # the X in the corner
            expect(dialog).to_be_hidden()
        finally:
            delete_project(page, project)
            browser.close()
