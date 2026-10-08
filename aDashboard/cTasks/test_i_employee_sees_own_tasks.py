from playwright.sync_api import sync_playwright
from utils.dashboard_helper import (open_browser_as, login_as, open_dashboard, open_tasks, task_titles, task_header_counts,
                                    create_project, add_task, delete_project, unique_tag, ADMIN, EMPLOYEE,
                                    QA_PROJECT_PREFIX, QA_TASK_PREFIX)


def test_employee_sees_own_tasks():
    """DB-020: an employee's Tasks section lists the tasks assigned to them and not other people's."""
    tag = unique_tag()
    project = f"{QA_PROJECT_PREFIX} {tag}"
    mine, theirs = f"{QA_TASK_PREFIX} {unique_tag()}", f"{QA_TASK_PREFIX} {unique_tag()}"
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            project_id = create_project(page, project)
            add_task(page, project_id, mine, "for the employee", assignee=EMPLOYEE["name"])
            add_task(page, project_id, theirs, "for the admin", assignee=ADMIN["name"])

            employee = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
            login_as(employee, "employee")
            open_tasks(employee)
            titles = task_titles(employee)
            assert mine in titles, f"employee's task missing from {titles}"
            assert theirs not in titles, f"admin's task shown to the employee: {titles}"
            assert task_header_counts(employee)[0] == len(titles)

            open_dashboard(page)
            open_tasks(page)
            assert mine not in task_titles(page), "employee's task shown on the admin's dashboard"
        finally:
            delete_project(page, project)
            browser.close()
