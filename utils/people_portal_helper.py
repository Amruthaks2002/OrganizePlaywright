import re
import uuid
from urllib.parse import quote

from playwright.sync_api import Page, expect
from utils.learning_helper import (  # noqa: F401  (re-exported for the tests)
    BASE_URL, open_browser, main_content, expect_toast, settle, goto,
)
from utils.onboarding_helper import open_browser_as  # noqa: F401
from utils.asset_helper import bulk_post  # noqa: F401

PORTAL_URL = f"{BASE_URL}/admin/people-portal"
BULK_ASSIGN = "/admin/people-portal/bulk-assign"
BULK_DELETE = "/admin/people-portal/bulk-delete"

QA_QUERY_PREFIX = "QA Query"
QUERY_TYPE = "Other queries"
# Ajith PT (the employee quick-login user) raises the QA queries, so he's never offered as their assignee
CREATOR = "Ajith PT"
CREATOR_ID = 13
ASSIGNEE = "Fasil KK"
SECOND_ASSIGNEE = "HR Manager"
FASNA_ID = 172  # Fasna KK, an eligible assignee for "Other queries"


def unique_prefix():
    # random suffix so tests running in parallel never search up each other's queries
    return f"{QA_QUERY_PREFIX} {uuid.uuid4().hex[:6]}"


# ---------- list ----------

def portal_url(search=""):
    return f"{PORTAL_URL}?search={quote(search)}" if search else PORTAL_URL


def open_portal(page: Page, search=""):
    goto(page, portal_url(search))
    expect(main_content(page).get_by_role("heading", name="People Portal Control Center")).to_be_visible()


def query_rows(page: Page):
    return main_content(page).locator("tbody tr").filter(has=page.locator("input[type=checkbox]"))


def query_row(page: Page, subject):
    # the request cell's text runs the subject straight into the type ("QA Query ab12cd 1Other
    # queries"), so only make sure no further digit follows ("... 1" must not match "... 10")
    return query_rows(page).filter(has_text=re.compile(rf"{re.escape(subject)}(?!\d)"))


def row_box(row):
    return row.locator("input[type=checkbox]")


def row_id(row):
    return int(row.locator("td").nth(1).inner_text().strip())


def row_assignee(row):
    return row.locator("td").nth(6)


def row_status(row):
    return row.locator("td").nth(4)


def select_all_box(page: Page):
    return main_content(page).locator("thead input[type=checkbox]")


def checked_rows(page: Page):
    return main_content(page).locator("tbody input[type=checkbox]:checked")


def select_rows(page: Page, *subjects):
    for subject in subjects:
        row_box(query_row(page, subject)).check()
    expect_selected(page, len(subjects))


def select_all(page: Page, count):
    select_all_box(page).check()
    expect_selected(page, count)


# ---------- selection dock ----------

def dock(page: Page):
    return page.get_by_role("toolbar")


def dock_clear(page: Page):
    return page.get_by_test_id("selection-dock-clear")


def dock_assign(page: Page):
    return dock(page).get_by_role("button", name="Assign", exact=True)


def dock_delete(page: Page, count=None):
    number = r"\d+" if count is None else str(count)
    return dock(page).get_by_role("button", name=re.compile(rf"^\s*Delete \({number}\)\s*$"))


def expect_selected(page: Page, count):
    # only checks the number: the singular label is currently misspelt (see PB-001)
    expect(dock(page)).to_be_visible()
    expect(dock(page)).to_contain_text(re.compile(rf"^\s*{count}\s*quer"))


# ---------- bulk assign ----------

def assign_dialog(page: Page):
    return page.locator("div.fixed.inset-0:visible").filter(has_text="Bulk Assign Queries").last


def open_assign(page: Page):
    dock_assign(page).click()
    dialog = assign_dialog(page)
    expect(dialog).to_be_visible()
    return dialog


def assignee_chips(dialog):
    # one toggle button per eligible assignee, between the "Available Assignees" label and the search box
    return dialog.locator("div.flex.flex-wrap > button")


def assignee_chip(dialog, name):
    return assignee_chips(dialog).filter(has_text=re.compile(rf"^\s*{re.escape(name)}\s*$"))


def chip_selected(chip):
    return "bg-cyan-600" in (chip.get_attribute("class") or "")


def selected_count(dialog):
    """(picked, eligible) from the "Available Assignees (1/6 selected)" label."""
    match = re.search(r"\((\d+)/(\d+) selected\)", dialog.inner_text())
    return int(match.group(1)), int(match.group(2))


def assignee_search(dialog):
    return dialog.get_by_placeholder("Search eligible assignees...")


def distribute_button(dialog):
    return dialog.get_by_role("button", name="Distribute Queries")


def bulk_assign(page: Page, *assignees):
    """Opens Assign for the current selection, picks `assignees` and distributes."""
    dialog = open_assign(page)
    for name in assignees:
        assignee_chip(dialog, name).click()
    distribute_button(dialog).click()
    expect_toast(page, "Bulk assignment completed.")
    expect(dialog).to_be_hidden()


# ---------- bulk delete ----------

def delete_dialog(page: Page):
    # titled "Delete Query" for one query and "Delete Queries" for several
    return page.get_by_role("alertdialog").filter(has_text=re.compile(r"Delete Quer(y|ies)")).last


def open_delete(page: Page, count=None):
    dock_delete(page, count).click()
    dialog = delete_dialog(page)
    expect(dialog).to_be_visible()
    return dialog


def confirm_delete(page: Page, count):
    dialog = open_delete(page, count)
    dialog.get_by_role("button", name="Delete", exact=True).click()
    expect_toast(page, f"{count} {'query' if count == 1 else 'queries'} deleted.")
    expect(dialog).to_be_hidden()


# ---------- create / cleanup ----------

def create_query(page: Page, subject, priority="High"):
    """Raises a query from the + Create Query dialog (run as the employee)."""
    goto(page, PORTAL_URL)
    page.get_by_role("button", name="+ Create Query").click()
    dialog = page.locator(".fixed.inset-0.z-50")
    dialog.wait_for()
    dialog.locator(".vs__dropdown-toggle").click()
    dialog.locator("input.vs__search").fill(QUERY_TYPE)
    page.locator(f"li:has-text('{QUERY_TYPE}')").click()
    dialog.get_by_text(priority, exact=True).click()
    dialog.get_by_placeholder("Subject").fill(subject)
    dialog.get_by_placeholder("Describe the case").fill("Raised by the bulk select tests.")
    dialog.get_by_role("button", name="Create Query").click()
    expect_toast(page, "Query created successfully.")


def create_queries(p, prefix, count=2, role="employee"):
    """Raises `prefix 1`, `prefix 2`, ... as `role` (the employee by default) and returns their subjects."""
    browser, page = open_browser_as(p, role)
    subjects = [f"{prefix} {i}" for i in range(1, count + 1)]
    try:
        for subject in subjects:
            create_query(page, subject)
    finally:
        browser.close()
    return subjects


def delete_queries(page: Page, prefix):
    """Bulk-deletes every query matching `prefix` as admin (used as test cleanup)."""
    open_portal(page, search=prefix)
    count = query_rows(page).filter(has_text=prefix).count()
    if count == 0:
        return
    select_all(page, count)
    confirm_delete(page, count)
    open_portal(page, search=prefix)
    expect(query_rows(page).filter(has_text=prefix)).to_have_count(0)
