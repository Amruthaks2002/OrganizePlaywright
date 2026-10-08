from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import open_browser_as, open_tasks, task_filter_button, task_filter_options, TASK_FILTERS


def test_filter_options():
    """DB-013: the Task Filter defaults to All Tasks and lists All Tasks, To Do, In Progress, Completed,
    Past Due, Due Today and Upcoming."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        open_tasks(page)
        expect(task_filter_button(page)).to_have_text("All Tasks")
        menu = task_filter_options(page)
        options = [o.strip() for o in menu.locator("xpath=./*").all_inner_texts()]
        assert options == TASK_FILTERS, f"options {options}"
        browser.close()
