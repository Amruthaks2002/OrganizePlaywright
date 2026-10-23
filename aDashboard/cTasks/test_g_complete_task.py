from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, open_tasks, task_card, card_status,
                                    task_header_counts, expect_toast, create_project, add_task, delete_project,
                                    unique_tag, QA_PROJECT_PREFIX, QA_TASK_PREFIX)


def test_complete_task():
    """DB-018: Complete moves an In Progress task to Completed and drops the In Progress count."""
    tag = unique_tag()
    project, task = f"{QA_PROJECT_PREFIX} {tag}", f"{QA_TASK_PREFIX} {unique_tag()}"
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            project_id = create_project(page, project)
            add_task(page, project_id, task, "complete me", status="in_progress")
            open_dashboard(page)
            open_tasks(page)
            total, todo, in_progress = task_header_counts(page)
            card = task_card(page, task)
            assert card_status(card) == "In Progress"

            card.get_by_role("button", name="Complete").click()
            expect_toast(page, "Task status updated.")
            expect(card.get_by_role("button")).to_have_count(0)
            assert card_status(card) == "Completed"
            assert task_header_counts(page) == (total, todo, in_progress - 1)
        finally:
            delete_project(page, project)
            browser.close()
