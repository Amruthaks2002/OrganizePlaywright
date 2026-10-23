import re
import uuid
from datetime import date, timedelta
from urllib.parse import quote, unquote

from playwright.sync_api import Page, expect
from utils.learning_helper import (  # noqa: F401  (re-exported for the tests)
    BASE_URL, open_browser, main_content, modal, expect_toast, settle, goto,
)
from utils.onboarding_helper import login_as, open_browser_as  # noqa: F401

ASSETS_URL = f"{BASE_URL}/assets"
CREATE_URL = f"{ASSETS_URL}/create"

QA_ASSET_PREFIX = "QA Bulk"
EMPTY_LIST = "No assets match these filters."
# Ajith PT is the employee quick-login user; the HR / team lead users aren't offered as assignees
EMPLOYEE = "Ajith PT"
TRANSFER_TO = "Abdul Hafeelu"
LOCATION = "Cyber Park"
# a date after anything a test assigns on, so cleanup can always check assets back in
FAR_FUTURE = "2031-01-01"

BULK_ACTIONS = ["Check In", "Check Out", "Transfer", "Delete"]
BULK_ENDPOINTS = ["/assets/bulk/check-in", "/assets/bulk/check-out", "/assets/bulk/transfer", "/assets/bulk/delete"]


def unique_prefix():
    # random suffix so tests running in parallel never search up each other's assets
    return f"{QA_ASSET_PREFIX} {uuid.uuid4().hex[:6]}"


def iso(days_from_today=0):
    return (date.today() + timedelta(days=days_from_today)).isoformat()


# ---------- list ----------

def assets_url(search="", archived=False, page_no=None):
    params = []
    if archived:
        params.append("include_archived=1")
    if search:
        params.append(f"search={quote(search)}")
    if page_no:
        params.append(f"page={page_no}")
    return ASSETS_URL + ("?" + "&".join(params) if params else "")


def open_assets(page: Page, search="", archived=False, page_no=None):
    goto(page, assets_url(search, archived, page_no))
    expect(main_content(page).get_by_role("heading", name="Assets", exact=True)).to_be_visible()


def asset_rows(page: Page):
    return main_content(page).locator("tbody tr").filter(has=page.locator("input[type=checkbox]"))


def asset_row(page: Page, name):
    # the name cell also holds the category ("Laptop"), so match the name as a whole word
    return asset_rows(page).filter(has_text=re.compile(rf"{re.escape(name)}\b"))


def row_checkbox(row):
    return row.locator("input[type=checkbox]")


def row_tag(row):
    return row.locator("td").nth(1).inner_text().strip()


def row_holder(row):
    return row.locator("td").nth(4)


def row_status(row):
    return row.locator("td").nth(3)


def select_all_box(page: Page):
    return main_content(page).get_by_label("Select all assets on this page")


def select_all(page: Page, count):
    """Ticks the header checkbox and waits for the dock to report `count` assets."""
    select_all_box(page).check()
    expect_selected(page, count)


def select_rows(page: Page, *names):
    for name in names:
        row_checkbox(asset_row(page, name)).check()
    expect_selected(page, len(names))


def checked_rows(page: Page):
    return main_content(page).locator("tbody input[type=checkbox]:checked")


def search_box(page: Page):
    return main_content(page).get_by_placeholder("Search tag, serial, name, invoice…")


# ---------- selection dock ----------

def dock(page: Page):
    # the floating bar at the bottom: count, label, the four actions and Clear
    return page.get_by_test_id("selection-dock-clear").locator("xpath=..")


def dock_clear(page: Page):
    return page.get_by_test_id("selection-dock-clear")


def dock_button(page: Page, action, count=None):
    """action: Check In / Check Out / Transfer / Delete. The label carries how many of the
    selected assets the action applies to, e.g. 'Check Out (2)'."""
    number = r"\d+" if count is None else str(count)
    return dock(page).get_by_role("button", name=re.compile(rf"^\s*{action} \({number}\)\s*$"))


def expect_selected(page: Page, count):
    label = "asset selected" if count == 1 else "assets selected"
    expect(dock(page)).to_contain_text(re.compile(rf"^\s*{count}\s*{label}"))


def expect_dock_counts(page: Page, check_in, check_out, transfer, delete):
    """Checks each action's count, and that an action is disabled exactly when its count is 0."""
    for action, count in zip(BULK_ACTIONS, (check_in, check_out, transfer, delete)):
        button = dock_button(page, action, count)
        expect(button).to_be_visible()
        if count:
            expect(button).to_be_enabled()
        else:
            expect(button).to_be_disabled()


# ---------- bulk dialogs ----------

def bulk_dialog(page: Page, action, count=None):
    # dialog titles read "Check Out 2 Assets", "Transfer 2 Assets", ... (shown upper-case)
    if action == "Delete":
        return modal(page, "Delete Asset")
    number = r"\d+" if count is None else str(count)
    return modal(page, re.compile(rf"{action} {number} Assets", re.I))


def open_bulk(page: Page, action, count=None):
    """Clicks a dock action whose label shows `count` (any count when None) and returns its dialog."""
    dock_button(page, action, count).click()
    dialog = bulk_dialog(page, action, count)
    expect(dialog).to_be_visible()
    return dialog


def submit(dialog, action):
    dialog.get_by_role("button", name=action, exact=True).click()


def pick_option(page: Page, dialog, text, index=0):
    """Types into the dialog's index-th vue-select (employee, status or location) and picks `text`."""
    search = dialog.locator("input.vs__search").nth(index)
    search.click()
    search.press_sequentially(text, delay=30)
    page.locator("li[role=option]:visible").filter(has_text=text).first.click()


def date_inputs(dialog):
    # Check Out / Transfer: [assigned or transferred on, expected return]; Check In: [return date]
    return dialog.locator("input[type=date]")


def fill_assignment(page: Page, dialog, employee=None, on=None, expected_return=None, notes=None):
    """Fills the Check Out / Transfer form."""
    if employee is not None:
        pick_option(page, dialog, employee)
    if on is not None:
        date_inputs(dialog).nth(0).fill(on)
    if expected_return is not None:
        date_inputs(dialog).nth(1).fill(expected_return)
    if notes is not None:
        dialog.locator("textarea").fill(notes)


def fill_check_in(page: Page, dialog, returned_on=None, status=None, location=None, notes=None):
    if returned_on is not None:
        date_inputs(dialog).first.fill(returned_on)
    if status is not None:
        pick_option(page, dialog, status, 0)
    if location is not None:
        pick_option(page, dialog, location, 1)
    if notes is not None:
        dialog.locator("textarea").fill(notes)


def bulk_check_out(page: Page, prefix, count, employee=EMPLOYEE, on=None):
    """Selects every asset matching `prefix` and checks them all out to `employee`."""
    open_assets(page, search=prefix)
    select_all(page, count)
    dialog = open_bulk(page, "Check Out", count)
    fill_assignment(page, dialog, employee, on=on)
    submit(dialog, "Check Out")
    expect_toast(page, f"{count} asset{'s' if count > 1 else ''} checked out.")
    expect(dialog).to_be_hidden()


# ---------- single-asset actions (used to set up a stale selection in another tab) ----------

def single_check_out(page: Page, prefix, name, employee=EMPLOYEE):
    open_assets(page, search=prefix)
    asset_row(page, name).get_by_role("button", name="Check Out").click()
    dialog = modal(page, "Check Out Asset")
    expect(dialog).to_be_visible()
    pick_option(page, dialog, employee)
    submit(dialog, "Check Out")
    expect_toast(page, f"Asset checked out to {employee}.")


# ---------- create / cleanup ----------

def create_asset(page: Page, name, status=None):
    """Creates an asset with the first model in the list and returns its id."""
    goto(page, CREATE_URL)
    main = main_content(page)
    # the form pre-fills the next tag in sequence, which parallel tests would all grab at once
    main.locator("#asset_tag").fill(f"QA-{uuid.uuid4().hex[:8].upper()}")
    main.locator("#name").fill(name)
    main.locator("#asset_model_id").click()
    page.locator("li[role=option]:visible").first.click()
    if status is not None:
        main.locator("#asset_status_id").click()
        page.locator("li[role=option]:visible").filter(has_text=re.compile(rf"^\s*{re.escape(status)}\s*$")).first.click()
    main.get_by_role("button", name="Create Asset").click()
    page.wait_for_url(re.compile(r"/assets/\d+$"))
    settle(page)
    return int(page.url.rstrip("/").split("/")[-1])


def create_assets(page: Page, prefix, count=2):
    """Creates `prefix 1`, `prefix 2`, ... and returns their names."""
    names = [f"{prefix} {i}" for i in range(1, count + 1)]
    for name in names:
        create_asset(page, name)
    return names


def delete_assets(page: Page, prefix):
    """Checks in and deletes every asset matching `prefix` (used as test cleanup). Archived ones
    are included, and the check-in date is far enough ahead for assets assigned in the future."""
    open_assets(page, search=prefix, archived=True)
    count = asset_rows(page).count()
    if count == 0:
        return
    select_all(page, count)
    check_in = dock_button(page, "Check In")
    assigned = int(re.search(r"\((\d+)\)", check_in.inner_text()).group(1))
    if assigned:
        dialog = open_bulk(page, "Check In", assigned)
        fill_check_in(page, dialog, returned_on=FAR_FUTURE)
        submit(dialog, "Check In")
        expect_toast(page, "checked in.")
        open_assets(page, search=prefix, archived=True)
        select_all(page, count)
    dialog = open_bulk(page, "Delete", count)
    dialog.get_by_role("button", name="Delete", exact=True).click()
    expect_toast(page, f"{count} asset{'s' if count > 1 else ''} deleted.")
    open_assets(page, search=prefix, archived=True)
    expect(asset_rows(page)).to_have_count(0)


# ---------- detail page ----------

def asset_url(asset_id):
    return f"{ASSETS_URL}/{asset_id}"


def open_asset(page: Page, asset_id):
    goto(page, asset_url(asset_id))
    expect(main_content(page).get_by_text("Assignment History")).to_be_visible()


def row_id(row):
    return int(row_checkbox(row).get_attribute("value"))


def assignment_history(page: Page):
    return main_content(page).get_by_text("Assignment History").locator("xpath=ancestor::div[.//table][1]").locator("table")


# ---------- direct requests ----------

def bulk_post(page: Page, path, data):
    """POSTs to a bulk endpoint with the page's session, the way the app's own requests do.
    Returns (status, json-or-None)."""
    xsrf = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    response = page.request.post(f"{BASE_URL}{path}", data=data, max_redirects=0, headers={
        "X-XSRF-TOKEN": xsrf, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
    try:
        return response.status, response.json()
    except Exception:
        return response.status, None
