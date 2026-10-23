import datetime

from playwright.sync_api import sync_playwright
from utils.dashboard_helper import (open_browser_as, open_dashboard, open_tasks, choose_task_filter, task_cards,
                                    task_titles, card_status, open_task_details, task_detail, create_project, add_task,
                                    delete_project, unique_tag, today, QA_PROJECT_PREFIX, QA_TASK_PREFIX)


def test_due_date_filters():
    """DB-015: Due Today shows only tasks due today, Upcoming only tasks due later, and Past Due only
    unfinished tasks whose deadline has passed."""
    tag = unique_tag()
    project = f"{QA_PROJECT_PREFIX} {tag}"
    due_today, upcoming = f"{QA_TASK_PREFIX} {unique_tag()}", f"{QA_TASK_PREFIX} {unique_tag()}"
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            project_id = create_project(page, project)
            add_task(page, project_id, due_today, "due today", due=today())
            add_task(page, project_id, upcoming, "due in five days", due=today() + datetime.timedelta(days=5))
            open_dashboard(page)
            open_tasks(page)

            choose_task_filter(page, "Due Today")
            titles = task_titles(page)
            assert due_today in titles and upcoming not in titles, f"Due Today shows {titles}"

            choose_task_filter(page, "Upcoming")
            titles = task_titles(page)
            assert upcoming in titles and due_today not in titles, f"Upcoming shows {titles}"

            choose_task_filter(page, "Past Due")
            titles = task_titles(page)
            assert due_today not in titles and upcoming not in titles, f"Past Due shows {titles}"
            for title, card in zip(titles, task_cards(page).all()):
                assert card_status(card) != "Completed", f"completed task {title!r} listed as Past Due"
                dialog = open_task_details(page, title)
                deadline = datetime.datetime.strptime(task_detail(dialog, "Deadline"), "%d %b, %Y").date()
                assert deadline < today(), f"{title!r} is due {deadline}, not past due"
                dialog.get_by_role("button", name="Close").click()
        finally:
            delete_project(page, project)
            browser.close()
