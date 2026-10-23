import json
import os
import time
from urllib.parse import unquote

from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import login_as
from utils.work_summary_helper import (BASE_URL, open_hours, page_props, settle, main_content, log_comp_hours,
                                       find_logs, cleanup_unapproved, unique_desc, COMP_SEARCH_DAYS)

NOTIFICATIONS_URL = f"{BASE_URL}/notifications"
TITLE = "New Compensatory Work Request"
NOTIFICATION_TYPE = "compensatory_work_submitted"

PROJECT_ID, PROJECT = 219, "Project QA Automation"  # PM malik, assigned to QA Team (lead Anjana Anil)
CHARLOTTE_ID, CHARLOTTE_NAME = 303, "Charlotte"     # reports to Team Lead User
CHARLOTTE = ("charlotte@iocod.com", "password")
MALIK = ("malik@iocod.com", "password")
ANJANA = ("anjana@iocod.com", "password")
DILNA = ("dilna@iocod.com", "password")

# who signs in how: a quick-login role, or (email, password)
RECIPIENTS = {  # (user id, login)
    "Team Lead User": (114, "team-lead"),   # Charlotte's reporting manager
    "HR Manager": (112, "hr"),
    "Admin User": (7, "admin"),
    "malik": (283, MALIK),                  # the project's PM
    "Anjana Anil": (277, ANJANA),           # lead of the project's team
}
NOT_RECIPIENTS = {
    "Anish Mohan K": (22, "project-manager"),  # a PM with no part in the project
    # leads Team LMS, which Charlotte is in but the project isn't assigned to (and manages WorkSphere)
    "dilna": (285, DILNA),
    "employee quick login": (None, "employee"),  # whoever it is today (Ajith PT, later Akshay Surendran)
}
WAIT_SECONDS = 30


def sign_in(browser, login):
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    if isinstance(login, str):
        login_as(page, login)
    else:
        email, password = login
        page.goto(BASE_URL)
        page.fill("#email", email)
        page.fill("#password", password)
        page.click("[data-testid='sign-in-button']")
        page.wait_for_url("**/dashboard**")
        # the sign-in is an Inertia visit, so the page's data-page still holds the login page's props
        page.reload()
        settle(page)
    return page


def signed_in_user(page):
    return page_props(page)["auth"]["user"]


def comp_notifications(page, log_id, since):
    """The signed-in user's comp request notifications for time log `log_id`, from the /notifications pages
    (newest first, so it stops at the first page older than `since`). Reading them this way leaves them unread."""
    version = json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["version"] or ""
    found, page_no = [], 1
    while True:
        data = page.request.get(f"{NOTIFICATIONS_URL}?page={page_no}",
                                headers={"X-Inertia": "true", "X-Inertia-Version": version}).json()["props"]["notifications"]
        found += [n for n in data["data"] if n["data"].get("time_log_id") == log_id]
        if not data["data"] or data["data"][-1]["created_at"] < since or page_no >= data["last_page"]:
            return found
        page_no += 1


def wait_for_notifications(page, log_id, since):
    """Notifications may be sent from a queue, so give them a moment to arrive."""
    deadline = time.time() + WAIT_SECONDS
    while True:
        found = comp_notifications(page, log_id, since)
        if found or time.time() > deadline:
            return found
        page.wait_for_timeout(2000)


def mark_read(page, notification_id):
    token = next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN")
    response = page.request.post(f"{NOTIFICATIONS_URL}/{notification_id}/read", headers={"X-XSRF-TOKEN": unquote(token)})
    assert response.ok, f"could not mark notification {notification_id} as read: {response.status}"


def test_comp_request_notifications():
    """WS-050: when an employee (Charlotte) logs compensatory hours on a project, a 'New Compensatory Work
    Request' notification goes to exactly these five people, once each: her reporting manager, HR, the admin,
    the project's manager (malik) and the lead of the team the project is assigned to (Anjana). Each of them
    sees it on their Notifications page. PMs and team leads with no part in the project, other employees and
    Charlotte herself get nothing.

    Notifications are matched on their time_log_id, so earlier runs for the same date don't count. Notifications
    can't be deleted, so cleanup marks this run's ones as read (leaving everyone's unread count as it was) and deletes
    the comp entry; nothing is ever approved."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        sessions = {}  # name -> signed-in page
        desc = unique_desc("comp notify")
        log_id, since, received = None, None, {}
        try:
            charlotte = sign_in(browser, CHARLOTTE)
            assert signed_in_user(charlotte)["id"] == CHARLOTTE_ID
            for name, (user_id, login) in {**RECIPIENTS, **NOT_RECIPIENTS}.items():
                sessions[name] = sign_in(browser, login)
                me = signed_in_user(sessions[name])
                assert user_id in (None, me["id"]), f"{name}: signed in as {me['name']} (id {me['id']})"
                assert user_id or me["id"] not in [CHARLOTTE_ID] + [uid for uid, _ in RECIPIENTS.values()], \
                    f"{name} is {me['name']}, who should be notified"
            admin = sessions["Admin User"]

            # 1. Charlotte logs compensatory hours on the project
            open_hours(charlotte)
            since = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - 5))
            weekends = page_props(charlotte)["weekends"]
            day = log_comp_hours(charlotte, desc, 3, PROJECT, weekends)
            [log] = find_logs(admin, desc, days=COMP_SEARCH_DAYS, employee_id=CHARLOTTE_ID)
            log_id = log["id"]
            assert log["comp_off_status"] == "pending" and log["project_id"] == PROJECT_ID, log
            # the setup the recipient list depends on
            assert log["user"]["parent_id"] == RECIPIENTS["Team Lead User"][0], log["user"]
            assert log["project"]["project_manager_id"] == RECIPIENTS["malik"][0], log["project"]
            message = f"Comp-off request from {CHARLOTTE_NAME} for {day.strftime('%b %d, %Y')}"

            # 2 + 5. each intended recipient gets exactly one notification
            for name in RECIPIENTS:
                received[name] = wait_for_notifications(sessions[name], log_id, since)
            counts = {name: len(found) for name, found in received.items()}
            assert counts == {name: 1 for name in RECIPIENTS}, f"notifications for time log {log_id}: {counts}"
            for name, [notification] in received.items():
                assert notification["data"]["type"] == NOTIFICATION_TYPE, (name, notification)
                assert (notification["data"]["title"], notification["data"]["message"]) == (TITLE, message), \
                    (name, notification)
                assert notification["read_at"] is None, (name, notification)

            # 3. and sees it on their Notifications page
            for name in RECIPIENTS:
                page = sessions[name]
                page.goto(NOTIFICATIONS_URL)
                settle(page)
                card = main_content(page).locator("div").filter(has_text=TITLE).filter(has_text=message).last
                expect(card, f"{name} doesn't see the notification").to_be_visible()

            # 4. nobody else is notified (all five have theirs by now, so the others would too)
            others = {name: len(comp_notifications(sessions[name], log_id, since)) for name in NOT_RECIPIENTS}
            others[CHARLOTTE_NAME] = len(comp_notifications(charlotte, log_id, since))
            assert others == {name: 0 for name in others}, f"notified but shouldn't be, for time log {log_id}: {others}"
        finally:
            if log_id:
                for name, page in sessions.items():
                    for notification in received.get(name) or comp_notifications(page, log_id, since):
                        mark_read(page, notification["id"])
            if "Admin User" in sessions:
                admin = sessions["Admin User"]
                cleanup_unapproved(admin, desc, CHARLOTTE_ID)
                assert not find_logs(admin, desc, days=COMP_SEARCH_DAYS, employee_id=CHARLOTTE_ID), \
                    f"could not clean up '{desc}'"
            browser.close()
