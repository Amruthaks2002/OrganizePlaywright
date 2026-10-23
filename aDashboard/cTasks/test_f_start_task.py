from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, open_tasks, task_card, card_status,
                                    task_header_counts, expect_toast, create_project, add_task, delete_project,
                                    unique_tag, QA_PROJECT_PREFIX, QA_TASK_PREFIX)


def test_start_task():
    """DB-017: Start Task moves a To Do task to In Progress and updates the header counters."""
    tag = unique_tag()
    project, task = f"{QA_PROJECT_PREFIX} {tag}", f"{QA_TASK_PREFIX} {unique_tag()}"
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            project_id = create_project(page, project)
            add_task(page, project_id, task, "start me")
            open_dashboard(page)
            open_tasks(page)
            total, todo, in_progress = task_header_counts(page)
            card = task_card(page, task)
            assert card_status(card) == "To Do"

            card.get_by_role("button", name="Start Task").click()
            expect_toast(page, "Task status updated.")
            expect(card.get_by_role("button", name="Complete")).to_be_visible()
            assert card_status(card) == "In Progress"
            assert task_header_counts(page) == (total, todo - 1, in_progress + 1)
        finally:
            delete_project(page, project)
            browser.close()
