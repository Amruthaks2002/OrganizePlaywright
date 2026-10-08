from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, open_tasks, task_card, card_status,
                                    open_task_details, expect_toast, create_project, add_task, delete_project,
                                    unique_tag, QA_PROJECT_PREFIX, QA_TASK_PREFIX)


def test_start_from_details():
    """DB-019: Start Task inside the task details dialog also moves the task to In Progress."""
    tag = unique_tag()
    project, task = f"{QA_PROJECT_PREFIX} {tag}", f"{QA_TASK_PREFIX} {unique_tag()}"
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            project_id = create_project(page, project)
            add_task(page, project_id, task, "start me from the dialog")
            open_dashboard(page)
            open_tasks(page)

            dialog = open_task_details(page, task)
            dialog.get_by_role("button", name="Start Task").click()
            expect_toast(page, "Task status updated.")
            if dialog.is_visible():
                dialog.get_by_role("button", name="Close").click()
            expect(task_card(page, task).get_by_role("button", name="Complete")).to_be_visible()
            assert card_status(task_card(page, task)) == "In Progress"
        finally:
            delete_project(page, project)
            browser.close()
