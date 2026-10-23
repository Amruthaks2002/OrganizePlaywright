import datetime
import os
import re
import time
from urllib.parse import quote

from playwright.sync_api import Page, expect
from utils.learning_helper import BASE_URL, main_content, expect_toast, settle, goto  # noqa: F401
from utils.onboarding_helper import unique_tag  # noqa: F401

DASHBOARD_URL = f"{BASE_URL}/dashboard"
PROJECTS_URL = f"{BASE_URL}/projects"
MANAGE_EVENTS_URL = f"{BASE_URL}/manage/events"

# every dashboard dialog renders inside one of these
MODAL = "div[class*=modal-surface]:visible"

QA_NOTE_PREFIX = "QA Dash Note"
QA_PROJECT_PREFIX = "QA Dash Project"
QA_TASK_PREFIX = "QA Task"  # task cards cut titles off after ~20 characters
QA_EVENT_PREFIX = "QA Dash Event"

ADMIN = {"name": "Admin User", "email": "admin@example.com", "designation": "System Administrator"}
EMPLOYEE = {"name": "Ajith PT", "email": "ajith@iocod.com", "designation": "Software Engineer",
            "manager": "Team Lead User"}

TASK_FILTERS = ["All Tasks", "To Do", "In Progress", "Completed", "Past Due", "Due Today", "Upcoming"]
TASK_STATUSES = ["To Do", "In Progress", "Completed"]

# chip label -> the calendar-event-<type> class its events carry
CALENDAR_CHIPS = {"LEAVES": "leave", "WORK MODE": "work_mode", "HOLIDAYS": "holiday",
                  "BIRTHDAYS": "birthday", "ANNIVERSARIES": "anniversary", "NOTES": "note"}
LEGEND = ["Leave", "Work Mode", "Holiday", "Birthday", "Anniversary", "Note"]
# event type -> the label at the top of its detail popup
EVENT_POPUP_LABELS = {"leave": "LEAVE REQUEST", "work_mode": "WORK MODE", "holiday": "HOLIDAY",
                      "birthday": "BIRTHDAY", "anniversary": "WORK ANNIVERSARY"}


def login_as(page: Page, role):
    """Signs in through the login page's Development Quick Login links (no password needed).

    Waits for the HTML rather than every asset ("load"): under parallel runs one asset on the login
    page can take more than 30s, while the links are usable long before that."""
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
    page.get_by_test_id(f"dev-login-link-{role}").click()
    page.wait_for_url("**/dashboard**", wait_until="domcontentloaded", timeout=60000)
    settle(page)


def open_browser_as(p, role):
    browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    login_as(page, role)
    return browser, page


def today():
    return datetime.date.today()


def ui_date(d):
    # the dashboard shows dates as "6 Oct, 2026"
    return f"{d.day} {d.strftime('%b')}, {d.year}"


def month_label_text(d):
    return d.strftime("%B %Y")


def modal(page: Page, text=None):
    dialogs = page.locator(MODAL)
    return (dialogs.filter(has_text=text) if text else dialogs).last


def open_dashboard(page: Page):
    goto(page, DASHBOARD_URL)
    expect(main_content(page).get_by_role("heading", name="Calendar")).to_be_visible()


def number(text):
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0


# ---------- collapsible sections ----------

def section_header(page: Page, title):
    return main_content(page).locator("button").filter(
        has=page.locator("h3", has_text=re.compile(rf"^\s*{title}\s*$")))


def section(page: Page, title):
    return section_header(page, title).locator("xpath=..")


def section_body(page: Page, title):
    return section(page, title).locator("xpath=./div[contains(@class,'overflow-hidden')]")


def expand(page: Page, title, marker):
    """Opens a dashboard section unless it is already open; marker is text only shown when open."""
    body = section(page, title)
    if not body.get_by_text(marker).first.is_visible():
        section_header(page, title).click()
    expect(body.get_by_text(marker).first).to_be_visible()
    return body


# ---------- attendance ----------

def open_attendance(page: Page):
    return expand(page, "Attendance", "Total Employees")


def attendance_stat(page: Page, label):
    value = section(page, "Attendance").locator("p", has_text=re.compile(rf"^\s*{label}\s*$")).locator(
        "xpath=following-sibling::p[1]")
    expect(value).to_be_visible()
    return int(value.inner_text().strip())


def attendance_text(page: Page):
    return section(page, "Attendance").inner_text()


def absent_badge(page: Page):
    # the header badge reads "N Absent", or "All Present" when nobody is
    text = section_header(page, "Attendance").inner_text()
    match = re.search(r"(\d+) Absent", text)
    assert match or "All Present" in text, f"no absent badge in {text!r}"
    return int(match.group(1)) if match else 0


def attendance_panel(page: Page, label):
    """The 'Absent Today' or 'Work Mode Requests' column of the open Attendance section."""
    heading = section(page, "Attendance").locator("h4").filter(has_text=re.compile(rf"^\s*{label}\s*$"))
    return heading.locator("xpath=ancestor::div[2]")


def panel_count(page: Page, label):
    return int(re.search(rf"{label}\s*\n\s*(\d+)", attendance_panel(page, label).inner_text()).group(1))


def absent_today_count(page: Page):
    return panel_count(page, "Absent Today")


def person_buttons(page: Page, label="Absent Today"):
    return attendance_panel(page, label).get_by_role("button", name=re.compile(r"^View .*'s profile$"))


def absentee_buttons(page: Page):
    return person_buttons(page, "Absent Today")


def person_row(button, marker):
    # the avatar button sits in a row that also carries the name, designation and leave / work mode type
    return button.locator(f"xpath=ancestor::*[contains(normalize-space(.), '{marker}')][1]")


def absentee_row(button):
    return person_row(button, "LEAVE")


def absentee_name(button):
    return re.match(r"^View (.*)'s profile$", button.get_attribute("aria-label")).group(1)


def any_person(page: Page):
    """The first person listed under Absent Today, else under Work Mode Requests, with the status
    their popover should show; (None, None) when both lists are empty."""
    if absentee_buttons(page).count():
        return absentee_buttons(page).first, "On leave today"
    if person_buttons(page, "Work Mode Requests").count():
        return person_buttons(page, "Work Mode Requests").first, "WFH today"
    return None, None


def profile_popover(page: Page):
    return page.get_by_role("button", name="View full profile").locator(
        "xpath=ancestor::div[contains(@class,'max-w-sm')][1]")


# ---------- tasks ----------

def open_tasks(page: Page):
    return expand(page, "Tasks", "Task Filter")


def task_header_counts(page: Page):
    text = section_header(page, "Tasks").inner_text()
    total = int(re.search(r"\((\d+)\)", text).group(1))
    todo = int(re.search(r"(\d+)\s*To do", text).group(1))
    in_progress = int(re.search(r"(\d+)\s*In Progress", text).group(1))
    return total, todo, in_progress


def task_cards(page: Page):
    return section(page, "Tasks").locator("div.group.cursor-pointer")


def task_card(page: Page, name):
    return task_cards(page).filter(has=page.locator("h4", has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")))


def task_titles(page: Page):
    return [t.strip() for t in task_cards(page).locator("h4").all_inner_texts()]


def card_status(card):
    text = card.inner_text()
    for status in TASK_STATUSES:
        if re.search(rf"(^|\n)\s*{status}\s*(\n|$)", text):
            return status
    raise AssertionError(f"no status on task card: {text!r}")


def task_filter_button(page: Page):
    return section(page, "Tasks").locator("div.relative > button").first


def task_filter_options(page: Page):
    task_filter_button(page).click()
    menu = section(page, "Tasks").locator("div.relative").first.locator("xpath=./*[2]")
    expect(menu).to_be_visible()
    return menu


def choose_task_filter(page: Page, name):
    menu = task_filter_options(page)
    menu.get_by_text(name, exact=True).click()
    expect(task_filter_button(page)).to_contain_text(name)
    page.wait_for_timeout(800)


def open_task_details(page: Page, name):
    task_card(page, name).locator("h4").click()
    dialog = modal(page, "Task Details Overview")
    expect(dialog).to_be_visible()
    return dialog


def task_detail(dialog, label):
    return dialog.get_by_text(f"{label}:", exact=True).locator("xpath=following-sibling::*[1]").inner_text().strip()


# ---------- QA projects / tasks (created for the task tests, deleted afterwards) ----------

def create_project(page: Page, name, end_date=None):
    """Creates a project on the core development team and returns its id."""
    end_date = end_date or today() + datetime.timedelta(days=30)
    goto(page, PROJECTS_URL)
    main_content(page).get_by_role("button", name="Create Project").click()
    dialog = modal(page, "Create New Project")
    dialog.locator("#name").fill(name)
    dialog.locator("#project_manager_id").select_option(label=ADMIN["name"])
    dialog.locator("label").filter(has_text=re.compile(r"^\s*core development team\s*$")).click()
    dialog.locator("#end_date").fill(end_date.isoformat())
    dialog.get_by_role("button", name="Create Project").click()
    expect(dialog).to_be_hidden(timeout=10000)
    return project_id(page, name)


def project_id(page: Page, name):
    goto(page, f"{PROJECTS_URL}?search={quote(name)}")
    link = main_content(page).locator("h3 a").filter(has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))
    expect(link).to_have_count(1)
    return int(link.get_attribute("href").rstrip("/").split("/")[-1])


def add_task(page: Page, project, name, description="", due=None, status=None, assignee=None):
    assignee = assignee or ADMIN["name"]
    goto(page, f"{PROJECTS_URL}/{project}")
    main_content(page).get_by_role("button", name="Add Task").click()
    dialog = modal(page, "Create Task")
    dialog.locator("#name").fill(name)
    if description:
        dialog.locator("#description").fill(description)
    if due:
        dialog.locator("#due_date").fill(due.isoformat())
    if status:
        dialog.locator("#status").select_option(status)
    dialog.locator("div.vs__dropdown-toggle").first.click()
    dialog.locator("input.vs__search").first.fill(assignee)
    page.locator("li[role=option]:visible").filter(has_text=assignee).first.click()
    dialog.get_by_role("button", name="Create", exact=True).click()
    expect(dialog).to_be_hidden(timeout=10000)


def delete_project(page: Page, name, exact=True):
    """Deletes every project with this name (its tasks go with it); exact=False deletes every project
    whose name starts with it. Safe to call when none exist."""
    pattern = re.compile(rf"^\s*{re.escape(name)}" + (r"\s*$" if exact else ""))
    url = f"{PROJECTS_URL}?search={quote(name)}"
    goto(page, url)
    main = main_content(page)
    title = page.locator("h3 a").filter(has_text=pattern)
    for _ in range(20):
        if not title.count():
            return
        card = main.locator("div.rounded-2xl").filter(has=title.first).last
        card.locator("button.border-red-300").click()
        dialog = modal(page, "Are you sure you want to delete the project")
        dialog.get_by_role("button", name="Delete").click()
        expect_toast(page, "Project deleted successfully.")
        goto(page, url)


# ---------- upcoming events ----------

def upcoming_count(page: Page):
    return number(section_header(page, "Upcoming Events").locator("span").first.inner_text())


def open_upcoming(page: Page):
    header = section_header(page, "Upcoming Events")
    body = section(page, "Upcoming Events")
    if not body.locator("xpath=./div").nth(0).is_visible():
        header.click()
    page.wait_for_timeout(800)
    return body


def upcoming_toggle(page: Page):
    # the chevron at the right of the header; clicking the header text would hit the View All link
    return section_header(page, "Upcoming Events").locator("svg").last


def create_event(page: Page, title, event_date, location="QA Room", description="Created by dashboard tests."):
    goto(page, MANAGE_EVENTS_URL)
    page.get_by_role("button", name="Create Event", exact=True).click()
    page.locator("#title").fill(title)
    page.locator("#category").select_option(label="Workshops")
    page.locator("#event_date").fill(event_date.isoformat())
    page.locator("#location").fill(location)
    page.locator("#description").fill(description)
    page.get_by_role("button", name="Create Event", exact=True).last.click()
    expect_toast(page, re.compile("Event created successfully", re.I))


def delete_event(page: Page, title):
    """Deletes every event with this title. Safe to call when none exist."""
    goto(page, MANAGE_EVENTS_URL)
    page.get_by_label("Search").fill(title)
    page.wait_for_timeout(1500)
    settle(page)  # the list re-renders when the search lands, which would drop a tick made earlier
    names = page.get_by_text(title, exact=True)
    if not names.count():
        return
    for name in names.all():
        box = name.locator("xpath=ancestor::div[contains(@class,'rounded-3xl')][1]").locator("input[type=checkbox]")
        box.check(force=True)
        expect(box).to_be_checked()
    # the bulk button was renamed from "Delete Selected" to "Delete"; accept either
    main_content(page).get_by_role("button", name=re.compile(r"^\s*Delete( Selected)?\s*$")).first.click()
    page.get_by_role("button", name="Delete", exact=True).last.click()  # the confirmation dialog
    expect_toast(page, re.compile(r"Successfully deleted \d+ event\(s\)", re.I))


# ---------- calendar ----------

def month_label(page: Page):
    return main_content(page).locator("button.min-w-\\[160px\\]")


def next_month(page: Page):
    month_label(page).locator("xpath=following-sibling::button[1]").click()
    page.wait_for_timeout(1000)


def prev_month(page: Page):
    month_label(page).locator("xpath=preceding-sibling::button[1]").click()
    page.wait_for_timeout(1000)


def go_to_month(page: Page, d):
    """Steps the calendar from whatever month it shows to the month containing d."""
    shown = datetime.datetime.strptime(month_label(page).inner_text().strip(), "%B %Y").date()
    steps = (d.year - shown.year) * 12 + d.month - shown.month
    for _ in range(abs(steps)):
        next_month(page) if steps > 0 else prev_month(page)
    expect(month_label(page)).to_have_text(month_label_text(d))


def chip(page: Page, label):
    return main_content(page).get_by_role("button", name=re.compile(rf"^\s*{label}\b", re.I))


def chip_count(page: Page, label):
    return number(chip(page, label).inner_text().replace(label, ""))


def choose_chip(page: Page, label):
    chip(page, label).click()
    page.wait_for_timeout(1200)


def celebrations_toggle(page: Page):
    return main_content(page).get_by_role("button", name=re.compile(r"^\s*(On|Off)\s*$"))


def day_cell(page: Page, d):
    return main_content(page).locator(f"td.fc-day[data-date='{d.isoformat()}']")


def month_cells(page: Page):
    # days that belong to the shown month (the grid also shows a few days of the months around it)
    return main_content(page).locator("td.fc-daygrid-day:not(.fc-day-other)")


def calendar_events(scope, kind=None):
    selector = f"a.fc-event.calendar-event-{kind}" if kind else "a.fc-event"
    return scope.locator(selector)


def shown_events(page: Page, kind=None):
    """Events in the shown month that are on screen (excludes the ones folded under '+N more')."""
    return [e for e in calendar_events(month_cells(page), kind).all() if e.is_visible()]


def month_event_total(page: Page):
    """Every event in the shown month: those on screen plus the ones folded under '+N more'."""
    cells = month_cells(page)
    more = sum(number(t) for t in cells.locator("a.fc-more-link").all_inner_texts())
    return len(shown_events(page)) + more


def event_types(page: Page):
    """The calendar-event-<type> of every event in the shown month, including folded ones."""
    return month_cells(page).locator("a.fc-event").evaluate_all(
        "els => els.map(e => [...e.classList].find(c => c.startsWith('calendar-event-')).replace('calendar-event-', ''))")


def find_month_with(page: Page, kind, months=6):
    """Moves forward from the shown month until one has an event of this type; returns that event."""
    for _ in range(months):
        events = shown_events(page, kind)
        if events:
            return events[0]
        next_month(page)
    return None


def event_date(event):
    return datetime.date.fromisoformat(event.locator("xpath=ancestor::td[@data-date][1]").get_attribute("data-date"))


# ---------- notes ----------

def note_text(label="note"):
    return f"{QA_NOTE_PREFIX} {label} {unique_tag()}"


def note_day():
    # a day other than today, so the legacy add/edit/delete tests (which work on today) are unaffected
    return today() + datetime.timedelta(days=2)


def open_day(page: Page, d):
    go_to_month(page, d)
    day_cell(page, d).locator("a.fc-daygrid-day-number").click()
    dialog = modal(page, "Add Note")
    expect(dialog).to_be_visible()
    return dialog


def add_note(page: Page, d, text):
    dialog = open_day(page, d)
    dialog.locator("#note").fill(text)
    dialog.get_by_role("button", name="Save").click()
    expect_toast(page, re.compile("note added successfully", re.I))
    expect(dialog).to_be_hidden()


def note_event(page: Page, d, text):
    return calendar_events(day_cell(page, d), "note").filter(has_text=text)


def open_note(page: Page, d, text):
    go_to_month(page, d)
    # with every kind shown, a day that already has two leaves / work mode entries folds the note
    # under '+N more', where it can't be clicked
    choose_chip(page, "NOTES")
    note_event(page, d, text).first.click()
    dialog = modal(page, "Edit Note")
    expect(dialog).to_be_visible()
    return dialog


def delete_note(page: Page, d, text):
    dialog = open_note(page, d, text)
    dialog.get_by_role("button", name="Delete").click()
    confirm = modal(page, "Delete Note")
    confirm.get_by_role("button", name="Delete").click()
    expect_toast(page, re.compile("Note deleted successfully", re.I))


def cleanup_notes(page: Page, d, text):
    """Deletes every note on day d containing text. Safe to call when none exist."""
    open_dashboard(page)
    go_to_month(page, d)
    choose_chip(page, "NOTES")  # only notes, so ours are not folded under '+N more' behind other events
    for _ in range(10):
        if not note_event(page, d, text).count():
            return
        event = note_event(page, d, text).first
        if not event.is_visible():
            day_cell(page, d).locator("a.fc-more-link").click()
            modal(page, "Events").get_by_text(text).first.click()
        else:
            event.click()
        modal(page, "Edit Note").get_by_role("button", name="Delete").click()
        modal(page, "Delete Note").get_by_role("button", name="Delete").click()
        expect_toast(page, re.compile("Note deleted successfully", re.I))
        page.wait_for_timeout(1000)


# ---------- parallel runs ----------

def retry_if_data_changed(check, attempts=3):
    """Runs check() up to `attempts` times and returns its result.

    For read-only checks that compare two reads of company-wide data (attendance totals, calendar
    leaves / work mode). Tests in other modules run at the same time and can add a leave or a user
    between the two reads; a real mismatch fails every attempt."""
    for attempt in range(attempts):
        try:
            return check()
        except AssertionError:
            if attempt == attempts - 1:
                raise
            time.sleep(5)  # give the other tests' change time to finish before reading again


def day_notes(page: Page, d):
    """The text of every note on day d (shown or folded under '+N more')."""
    return [t.strip() for t in calendar_events(day_cell(page, d), "note").evaluate_all(
        "els => els.map(e => e.textContent)")]
