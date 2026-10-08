import json
import os
import re
from datetime import date, timedelta
from urllib.parse import urlencode

from playwright.sync_api import Page, expect
from utils.learning_helper import BASE_URL, open_browser, main_content, modal, expect_toast, settle  # noqa: F401  (re-exported for the tests)
from utils.onboarding_helper import open_browser_as, unique_tag  # noqa: F401  (re-exported for the tests)

HOURS_URL = f"{BASE_URL}/hours"
LOGS_URL = f"{HOURS_URL}/logs"
CHART_URL = f"{HOURS_URL}/chart-data"
EXPORT_URL = f"{HOURS_URL}/compensatory-summary/export"
PERFORMANCE_URL = f"{BASE_URL}/performance"

PROJECT = "project Beta"
ADMIN_ID, ADMIN_NAME = 7, "Admin User"
EMPLOYEE_ID, EMPLOYEE_NAME = 13, "Ajith PT"  # the employee quick-login user
QA_PREFIX = "QA WS"
TABS = ["Chart View", "Regular Hours", "Comp Hours"]
ACTIVE_TAB_CLASS = "bg-blue-600"
PER_PAGE = 15

LOGGED = "Working hours logged successfully."
UPDATED = "Time log updated successfully."
DELETED = "Working hours deleted successfully."
APPROVED = "Compensatory work request approved."
REJECTED = "Compensatory work request rejected."
EXPORT_STARTED = "Compensatory summary export has been started. You will be notified when it is ready."
APPROVED_NOT_DELETABLE = "Cannot delete an approved compensatory entry."
DAILY_CAP = 14
DAILY_CAP_ERROR = f"Cannot log more than {DAILY_CAP} hours in a single day."
LEAVE_DAY_ERROR = "Logging hours is not allowed"  # '...You are on pending leave on this day. Logging hours is not allowed.'
EMPTY_TITLE = "No time logs found"
NO_DESCRIPTION = "–"
BADGES = {"pending": "⏳ Pending", "approved": "✓ Approved", "rejected": "✕ Rejected"}


# ---------- dates ----------

def today():
    return date.today()


def first_of_month(day=None):
    return (day or today()).replace(day=1)


def last_weekend_day(weekends=(6, 7)):
    """The most recent weekend day before today (ISO weekdays, like the page's `weekends` prop)."""
    day = today() - timedelta(days=1)
    while day.isoweekday() not in weekends:
        day -= timedelta(days=1)
    return day


def last_weekday(weekends=(6, 7)):
    """Today if it's a working day, otherwise the most recent one before it."""
    day = today()
    while day.isoweekday() in weekends:
        day -= timedelta(days=1)
    return day


def fmt(day):
    """How the table shows a date: '7 Oct, 2026'."""
    return f"{day.day} {day.strftime('%b')}, {day.year}"


def unique_desc(label=""):
    return f"{QA_PREFIX} {label} {unique_tag()}".replace("  ", " ")


# ---------- navigation ----------

def heading(page: Page):
    return main_content(page).get_by_role("heading", name="Work Summary", exact=True)


def open_hours(page: Page):
    """Full page load of Work Summary (Chart View)."""
    page.goto(HOURS_URL)
    settle(page)
    expect(heading(page)).to_be_visible()


def open_from_sidebar(page: Page):
    if not page.get_by_test_id("sidebar-child-work-summary").is_visible():
        page.get_by_test_id("sidebar-parent-work management").click()
    page.get_by_test_id("sidebar-child-work-summary").click()
    page.wait_for_url(HOURS_URL)
    expect(heading(page)).to_be_visible()


def page_props(page: Page):
    """The Inertia props of the last full page load."""
    return json.loads(page.locator("[data-page]").first.get_attribute("data-page"))["props"]


def wait_for_logs(page: Page, action):
    """Runs an action that makes the table refetch /hours/logs and returns that response's JSON."""
    with page.expect_response(lambda r: r.url.startswith(LOGS_URL), timeout=15000) as response:
        action()
    page.wait_for_timeout(300)  # let Vue re-render the table
    return response.value.json()


def wait_for_chart(page: Page, action):
    with page.expect_response(lambda r: r.url.startswith(CHART_URL), timeout=15000) as response:
        action()
    page.wait_for_timeout(500)  # let the chart redraw
    return response.value.json()


def tab_button(page: Page, name):
    return main_content(page).get_by_role("button", name=name, exact=True)


def open_tab(page: Page, name):
    """Switches to Regular Hours / Comp Hours and returns the logs JSON the table was built from."""
    return wait_for_logs(page, lambda: tab_button(page, name).click())


def is_active_tab(page: Page, name):
    return ACTIVE_TAB_CLASS in (tab_button(page, name).get_attribute("class") or "")


# ---------- filters ----------

def employee_search(page: Page):
    return main_content(page).locator("input[placeholder*='Search employee']")


def pick_employee(page: Page, name):
    search = employee_search(page)
    search.click()
    # type it like a user would: a single fill() sometimes leaves the list unfiltered
    search.press_sequentially(name, delay=40)
    option = page.locator("#vs1__listbox").get_by_role("option", name=name, exact=True)
    expect(option).to_be_visible()
    option.click()


def selected_employee(page: Page):
    # vue-select shows the picked employee as a .vs__selected chip
    return main_content(page).locator(".vs__selected")


def team_select(page: Page):
    # the Team picker is always the first select in the filter bar
    return main_content(page).locator("select").first


def status_select(page: Page):
    # only on Comp Hours, after the Team picker
    return main_content(page).locator("select").nth(1)


def from_date(page: Page):
    return main_content(page).locator("input[type=date]").nth(0)


def to_date(page: Page):
    return main_content(page).locator("input[type=date]").nth(1)


def clear_button(page: Page):
    return main_content(page).get_by_role("button", name="Clear", exact=True)


def export_button(page: Page):
    return main_content(page).get_by_role("button", name="Export", exact=True)


def show_from(page: Page, day):
    """Moves the From date back far enough for `day` to be in range (no-op if it already is)."""
    if day < first_of_month():
        wait_for_logs(page, lambda: from_date(page).fill(day.isoformat()))


# ---------- table ----------

def rows(page: Page):
    return main_content(page).locator("table tbody tr")


def row(page: Page, desc):
    # the description cell truncates long text, so match on the start of it
    return rows(page).filter(has_text=desc[:15])


def data_rows(page: Page):
    """Table rows, without the empty-state row."""
    return [tr for tr in rows(page).all() if tr.locator("td").count() > 1]


def row_cells(tr):
    return [c.strip() for c in tr.locator("td").all_inner_texts()]


def badge(tr):
    return tr.locator("span.rounded-full").last.inner_text().strip()


def edit_button(tr):
    return tr.locator("button[title=Edit]")


def delete_button(tr):
    # the delete button is the bordered red one at the end of the description cell
    return tr.locator("td").last.locator("button.border-red-300")


def approve_button(tr):
    return tr.locator("button[title=Approve]")


def reject_button(tr):
    return tr.locator("button[title=Reject]")


def footer_text(page: Page):
    return " ".join(main_content(page).get_by_text(re.compile(r"Showing \d+ to \d+ of \d+ results")).inner_text().split())


def pager_button(page: Page, name):
    return main_content(page).locator("nav").get_by_text(name, exact=True)


# ---------- dialogs ----------

def log_dialog(page: Page):
    return page.locator("div.fixed.inset-0:visible").filter(has_text="Log Working Hours").first


def edit_dialog(page: Page):
    return modal(page, "Edit Time Log")


def delete_dialog(page: Page):
    return modal(page, "Delete Work Log")


def confirm_dialog(page: Page):
    return page.get_by_test_id("confirm-dialog").last


def open_log_dialog(page: Page, server_validation=False):
    main_content(page).get_by_role("button", name="Log Hours").click()
    dialog = log_dialog(page)
    expect(dialog).to_be_visible()
    page.wait_for_timeout(300)  # let the modal's enter transition settle
    if server_validation:
        # skip the browser's required/max checks so the request reaches the server rules
        dialog.locator("form").evaluate("f => f.noValidate = true")
    return dialog


def fill_log(dialog, project=PROJECT, work_date=None, hours="2", desc=""):
    if project is not None:
        dialog.locator("select").select_option(label=project)
    if work_date is not None:
        dialog.locator("input[type=date]").fill(work_date.isoformat() if isinstance(work_date, date) else work_date)
    if hours is not None:
        dialog.locator("input[type=number]").fill(str(hours))
    dialog.locator("textarea").fill(desc)


def submit_log(dialog):
    dialog.get_by_role("button", name="Log Hours").click()


def log_hours(page: Page, desc, hours=2, work_date=None, project=PROJECT):
    """Logs hours through the Log Hours dialog (work date defaults to today)."""
    dialog = open_log_dialog(page)
    fill_log(dialog, project, work_date, hours, desc)
    submit_log(dialog)
    expect_toast(page, LOGGED)
    expect(log_dialog(page)).to_have_count(0)


def log_hours_on_free_weekday(page: Page, desc, hours=2, weekends=(6, 7), days=21):
    """Logs regular hours on the most recent working day the signed-in user is allowed to, and returns
    that day. The server refuses days they're on leave or that would go over the daily cap, which shared
    test users often hit, and hours on a holiday become a comp request instead, so all of those are skipped."""
    day = today()
    for _ in range(days):
        if day.isoweekday() not in weekends:
            dialog = open_log_dialog(page)
            fill_log(dialog, work_date=day, hours=hours, desc=desc)
            # after the POST the page reloads its props, errors included
            with page.expect_response(lambda r: r.url == HOURS_URL and r.request.method == "GET"):
                submit_log(dialog)
            page.wait_for_timeout(300)
            if log_dialog(page).count():
                expect(dialog.get_by_text(LEAVE_DAY_ERROR).or_(dialog.get_by_text(DAILY_CAP_ERROR))).to_be_visible()
                dialog.get_by_role("button", name="Cancel").click()
                expect(log_dialog(page)).to_have_count(0)
            else:
                [log] = find_logs(page, desc)
                if not log["is_weekend_or_holiday"]:
                    return day
                delete_log_api(page, log["id"])  # a holiday
        day -= timedelta(days=1)
    raise AssertionError(f"no working day in the last {days} days where hours can be logged")


def field_error(dialog, message):
    return dialog.get_by_text(message, exact=True)


def open_edit(page: Page, desc):
    edit_button(row(page, desc)).click()
    dialog = edit_dialog(page)
    expect(dialog).to_be_visible()
    page.wait_for_timeout(300)
    return dialog


def delete_in_ui(page: Page, desc):
    delete_button(row(page, desc)).click()
    delete_dialog(page).get_by_role("button", name="Delete").click()
    expect_toast(page, DELETED)


# ---------- server data / cleanup ----------

def _xsrf(page: Page):
    token = next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN")
    from urllib.parse import unquote
    return unquote(token)


def logs_api(page: Page, comp_filter="regular", status="all", start=None, end=None, page_no=1, **extra):
    params = {"hours[comp_filter]": comp_filter, "hours[comp_status]": status,
              "hours[date_from]": (start or first_of_month()).isoformat(),
              "hours[date_to]": (end or today()).isoformat(), "page": page_no}
    params.update({f"hours[{k}]": v for k, v in extra.items()})
    return page.request.get(f"{LOGS_URL}?{urlencode(params)}").json()


def find_logs(page: Page, desc, days=45, **extra):
    """Every log (regular or comp, any page) the signed-in user can see whose description is `desc`.
    `extra` narrows the search like the page's filters (e.g. employee_id=13)."""
    found = []
    start = today() - timedelta(days=days)
    for comp_filter in ("regular", "compensatory"):
        page_no, last = 1, 1
        while page_no <= last:
            data = logs_api(page, comp_filter, start=start, page_no=page_no, **extra)["timeLogs"]
            found += [log for log in data["data"] if log["description"] == desc]
            last = data["last_page"]
            page_no += 1
    return found


def delete_log_api(page: Page, log_id):
    """DELETE /hours/{id} the way the page sends it and returns the status. The server redirects back (302)
    whether or not it deleted the log - a refusal only shows up as the flash error on the next page load."""
    return page.request.delete(f"{HOURS_URL}/{log_id}", headers={"X-XSRF-TOKEN": _xsrf(page)}, max_redirects=0).status


def update_log_api(page: Page, log, **changes):
    body = {"id": log["id"], "project_id": log["project_id"], "work_date": log["work_date"],
            "hours_worked": log["hours_worked"], "description": log["description"], **changes}
    return page.request.put(f"{HOURS_URL}/{log['id']}", data=body,
                            headers={"X-XSRF-TOKEN": _xsrf(page)}, max_redirects=0).status


def cleanup_logs(page: Page, desc):
    """Deletes the test's own logs (used in finally). Rejected logs have no delete button, so this goes
    through the server like the page's delete does. Needs a page signed in as someone allowed to delete
    them (an admin for other people's rejected logs)."""
    for log in find_logs(page, desc):
        delete_log_api(page, log["id"])
    assert not find_logs(page, desc), f"could not clean up '{desc}'"


def chart_data(page: Page, **params):
    params.setdefault("date_from", first_of_month().isoformat())
    params.setdefault("date_to", today().isoformat())
    return page.request.get(f"{CHART_URL}?{urlencode(params)}").json()


def team_members(page: Page, team_id):
    return {u["id"]: u["name"] for u in chart_data(page, team=team_id)["teamWeeklyHours"]}


def user_week_hours(chart, user_id, day):
    """Hours the chart has for a user in the week containing `day` (users in several teams appear once per team)."""
    for user in chart["teamWeeklyHours"]:
        if user["id"] == user_id:
            for week in user["weekly_hours"]:
                if week["start_date"] <= day.isoformat() <= week["end_date"]:
                    return week["hours"]
    return None


# ---------- comp summary cards ----------

def summary_card(page: Page, title):
    return main_content(page).locator("div.rounded-2xl").filter(has_text=title).last


def card_number(card, label=None):
    """The big number on a summary card ('54 Hrs' -> 54.0), or the one under `label` on two-value cards."""
    scope = card.locator("p", has_text=label).locator("xpath=following-sibling::p[1]") if label else card.locator("p.text-2xl")
    return float(re.match(r"[\d.]+", scope.first.inner_text().strip()).group(0))


# ---------- comp-off conversion (dedicated throwaway user) ----------
# Approving comp hours can't be undone and permanently adds to the employee's comp-off balance, so the
# conversion test runs against a user set aside for it, whose balance is allowed to grow on every run.
COMP_USER_ENV = ("WS_COMP_USER_EMAIL", "WS_COMP_USER_PASSWORD")
HOURS_PER_HALF_DAY = 4
COMP_SEARCH_DAYS = 200


def comp_user_credentials():
    email, password = (os.environ.get(name) for name in COMP_USER_ENV)
    return (email, password) if email and password else None


def open_browser_with_login(p, email, password):
    browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    page.goto(BASE_URL)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("[data-testid='sign-in-button']")
    page.wait_for_url("**/dashboard**")
    settle(page)
    return browser, page


def comp_balance(page: Page, user_id):
    """(comp-off leave balance in days, approved hours not yet converted) for a user, as the Comp Hours
    summary cards get them (Leave Balance / Convertible Balance)."""
    data = logs_api(page, "compensatory", employee_id=user_id)
    return float(data["compOffBalance"]), float(data["remainingCompOffHours"])


def expected_after_approval(balance, leftover, hours):
    """Approved hours are added to the unconverted ones and turned into leave in 4-hour half days; whatever
    is left under 4 hours waits for the next approval (seen on QC: 2 left + 3 approved -> +0.5 day, 1 left)."""
    total = leftover + hours
    return balance + (total // HOURS_PER_HALF_DAY) * 0.5, total % HOURS_PER_HALF_DAY


def log_comp_hours(page: Page, desc, hours, project, weekends, days=COMP_SEARCH_DAYS):
    """Logs `hours` on the most recent weekend day that still has room under the daily cap and isn't
    refused (e.g. a leave day), and returns that day. Approved entries can never be deleted, so earlier
    runs keep filling up the recent weekends."""
    day = today() - timedelta(days=1)
    for _ in range(days):
        if day.isoweekday() in weekends:
            logged = sum(float(log["hours_worked"])
                         for comp_filter in ("regular", "compensatory")
                         for log in logs_api(page, comp_filter, start=day, end=day)["timeLogs"]["data"])
            if logged + hours <= DAILY_CAP:
                dialog = open_log_dialog(page)
                fill_log(dialog, project=project, work_date=day, hours=hours, desc=desc)
                with page.expect_response(lambda r: r.url == HOURS_URL and r.request.method == "GET"):
                    submit_log(dialog)
                page.wait_for_timeout(300)
                if log_dialog(page).count() == 0:
                    return day
                dialog.get_by_role("button", name="Cancel").click()
                expect(log_dialog(page)).to_have_count(0)
        day -= timedelta(days=1)
    raise AssertionError(f"no weekend day in the last {days} days with room for {hours} more hours")


def approve_in_ui(page: Page, desc, day, employee_name):
    """Approves a pending comp entry from the admin's Comp Hours tab."""
    open_hours(page)
    open_tab(page, "Comp Hours")
    wait_for_logs(page, lambda: from_date(page).fill(day.isoformat()))
    wait_for_logs(page, lambda: pick_employee(page, employee_name))
    wait_for_logs(page, lambda: status_select(page).select_option("pending"))
    r = row(page, desc)
    expect(r).to_have_count(1)
    approve_button(r).click()
    confirm_dialog(page).get_by_test_id("confirm-dialog-confirm").click()
    expect_toast(page, APPROVED)
    expect(page.get_by_test_id("confirm-dialog")).to_have_count(0)


def cleanup_unapproved(page: Page, desc, user_id):
    """Deletes whatever a failed run left pending or rejected; approved entries stay for good."""
    for log in find_logs(page, desc, days=COMP_SEARCH_DAYS, employee_id=user_id):
        if log["comp_off_status"] != "approved":
            delete_log_api(page, log["id"])
