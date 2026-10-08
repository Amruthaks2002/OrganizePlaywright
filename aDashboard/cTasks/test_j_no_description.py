from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, open_tasks, task_card, create_project, add_task,
                                    delete_project, unique_tag, QA_PROJECT_PREFIX, QA_TASK_PREFIX)


def test_no_description():
    """DB-021: a task saved without a description shows 'No description available' on its card."""
    tag = unique_tag()
    project, task = f"{QA_PROJECT_PREFIX} {tag}", f"{QA_TASK_PREFIX} {unique_tag()}"
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            project_id = create_project(page, project)
            add_task(page, project_id, task)
            open_dashboard(page)
            open_tasks(page)
            expect(task_card(page, task).get_by_text("No description available")).to_be_visible()
        finally:
            delete_project(page, project)
            browser.close()
