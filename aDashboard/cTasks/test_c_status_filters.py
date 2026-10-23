from playwright.sync_api import sync_playwright
from utils.dashboard_helper import (open_browser_as, open_tasks, choose_task_filter, task_cards, card_status,
                                    TASK_STATUSES)


def test_status_filters():
    """DB-014: the To Do, In Progress and Completed filters each show only (and all) tasks with that status."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        open_tasks(page)
        all_statuses = [card_status(c) for c in task_cards(page).all()]

        for status in TASK_STATUSES:
            choose_task_filter(page, status)
            shown = [card_status(c) for c in task_cards(page).all()]
            assert set(shown) <= {status}, f"{status} filter shows {shown}"
            assert len(shown) == all_statuses.count(status), \
                f"{status} filter shows {len(shown)} tasks, All Tasks has {all_statuses.count(status)}"
        browser.close()
