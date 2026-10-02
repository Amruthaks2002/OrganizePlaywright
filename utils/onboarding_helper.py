import os
import random
import re
import uuid
from urllib.parse import quote

from playwright.sync_api import Page, expect
from utils.learning_helper import (  # noqa: F401  (re-exported for the tests)
    BASE_URL, open_browser, main_content, expect_toast, settle, goto,
)

DIRECTORY_URL = f"{BASE_URL}/hr/onboarding"
FIELD_CONFIG_URL = f"{DIRECTORY_URL}/field-config"
JOURNEYS_URL = f"{DIRECTORY_URL}/journeys"
PROGRESS_URL = f"{DIRECTORY_URL}/progress"
ANALYTICS_URL = f"{DIRECTORY_URL}/analytics"

ONBOARDING_PAGES = [DIRECTORY_URL, FIELD_CONFIG_URL, JOURNEYS_URL, PROGRESS_URL, ANALYTICS_URL]
SIDEBAR_CHILDREN = {"directory": DIRECTORY_URL, "journeys": JOURNEYS_URL,
                    "journey-progress": PROGRESS_URL, "ocr-analytics": ANALYTICS_URL}

def protected_urls():
    """Every onboarding page, including the per-candidate / per-journey / per-employee ones."""
    return ONBOARDING_PAGES + [f"{DIRECTORY_URL}/{SUBMITTED_CANDIDATE_ID}",
                               f"{DIRECTORY_URL}/{SUBMITTED_CANDIDATE_ID}/history",
                               f"{JOURNEYS_URL}/{SAMPLE_JOURNEY_ID}",
                               f"{DIRECTORY_URL}/users/{COMPLETED_USER_ID}/onboarding-progress"]


QA_CANDIDATE_PREFIX = "QA Candidate"
QA_JOURNEY_PREFIX = "QA Journey"
DIRECTORY_EMPTY = "No onboarding sessions found"
STATUS_TABS = {"In Progress": "in_progress", "Submitted (Needs Review)": "submitted",
               "Needs Correction": "needs_correction", "Approved": "approved"}
STATUS_BADGES = {"in_progress": "In Progress", "submitted": "Submitted",
                 "needs_correction": "Needs Correction", "approved": "Approved"}

# a submitted candidate with uploaded documents, used only for read-only checks
SUBMITTED_CANDIDATE_ID = 82
# an employee who has finished their journey, and one who hasn't started it
COMPLETED_USER_ID = 277
COMPLETED_USER = "Anjana Anil"
IN_PROGRESS_USER_ID = 276
IN_PROGRESS_USER = "sdvssd"
# a journey with 3 steps (2 required), used only for read-only checks
SAMPLE_JOURNEY_ID = 4
SAMPLE_JOURNEY = "First Day Forward"

# the review page counters and the Basic Information fields a new candidate starts with
NEW_CANDIDATE_PENDING = 34
OPTIONAL_FIELD = "ESI Card ID"
PROTECTED_FIELD = "Years of Experience"


def unique_tag():
    # random suffix so tests running in parallel never pick the same name
    return uuid.uuid4().hex[:8]


def unique_phone():
    return "9" + "".join(random.choice("0123456789") for _ in range(9))


def login_as(page: Page, role):
    """Signs in through the login page's Development Quick Login links (no password needed).
    role: admin, hr, project-manager, team-lead or employee."""
    page.goto(BASE_URL)
    page.get_by_test_id(f"dev-login-link-{role}").click()
    page.wait_for_url("**/dashboard**")
    settle(page)


def open_browser_as(p, role):
    browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
    page = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
    login_as(page, role)
    return browser, page


def expect_forbidden(page: Page, url):
    response = page.goto(url)
    assert response.status == 403, f"{url}: expected 403, got {response.status}"
    expect(page).to_have_title(re.compile("Forbidden"))


def open_onboarding_submenu(page: Page, child):
    # the Onboarding group is already expanded when we're on one of its pages
    if not page.get_by_test_id(f"sidebar-child-{child}").is_visible():
        page.get_by_test_id("sidebar-parent-onboarding").click()
    page.get_by_test_id(f"sidebar-child-{child}").click()
    page.wait_for_url(SIDEBAR_CHILDREN[child])
    settle(page)


def modal(page: Page, text):
    # dialogs render several copies in the DOM, so use the last visible one
    return page.locator("div.fixed.inset-0:visible").filter(has_text=text).last


def vue_select(page: Page, scope, placeholder, option):
    # the placeholder disappears once something is picked, so placeholder=None means the scope's only picker
    (scope.locator("input.vs__search").first if placeholder is None else scope.get_by_placeholder(placeholder)).click()
    page.locator("li[role=option]:visible").filter(has_text=re.compile(rf"^\s*{re.escape(option)}\s*$")).first.click()


def vue_select_options(page: Page, scope, placeholder):
    scope.get_by_placeholder(placeholder).click()
    options = page.locator("li[role=option]:visible")
    expect(options.first).to_be_visible()
    texts = [t.strip() for t in options.all_inner_texts()]
    page.keyboard.press("Escape")
    return texts


# ---------- directory ----------

def directory_url(search="", status=""):
    return f"{DIRECTORY_URL}?search={quote(search)}&status={status}"


def open_directory(page: Page, search="", status=""):
    goto(page, directory_url(search, status) if search or status else DIRECTORY_URL)
    expect(main_content(page).get_by_role("heading", name="Employee Onboarding Directory")).to_be_visible()


def search_box(page: Page):
    return main_content(page).get_by_placeholder("Search by candidate name, phone number or personal email...")


def candidate_rows(page: Page):
    return main_content(page).locator("tbody tr").filter(has=page.get_by_role("link", name="Review Profile"))


def candidate_row(page: Page, name):
    return candidate_rows(page).filter(has=page.get_by_text(name, exact=True))


def directory_empty_state(page: Page):
    return main_content(page).get_by_text(DIRECTORY_EMPTY)


def status_tab(page: Page, name):
    return main_content(page).get_by_role("button", name=name, exact=True)


def row_statuses(page: Page):
    statuses = set()
    for text in candidate_rows(page).all_inner_texts():
        statuses.update(s for s in STATUS_BADGES.values() if re.search(rf"\t{s}\t|\n{s}\n|\t{s}\n", text))
    return statuses


def candidate_dialog(page: Page, title="Add New Onboarding Candidate"):
    return modal(page, title)


def open_add_candidate(page: Page):
    main_content(page).get_by_role("button", name="Add Candidate").click()
    dialog = candidate_dialog(page)
    expect(dialog).to_be_visible()
    return dialog


def fill_candidate_form(dialog, name=None, email=None, phone=None, esic=None):
    if name is not None:
        dialog.get_by_placeholder("John Doe").fill(name)
    if email is not None:
        dialog.get_by_placeholder("john.doe@example.com").fill(email)
    if phone is not None:
        dialog.get_by_placeholder("10-digit number").fill(phone)
    if esic is not None:
        dialog.locator("input[type=checkbox]").set_checked(esic)


def new_candidate_data(tag=None):
    tag = tag or unique_tag()
    return {"name": f"{QA_CANDIDATE_PREFIX} {tag}", "email": f"qa.candidate.{tag}@example.com",
            "phone": unique_phone()}


def create_candidate(page: Page, name, email, phone, esic=False):
    """Adds a candidate through the Add Candidate dialog and returns its id.

    Saving currently also shows "Onboarding invitation template not found." and keeps the
    dialog open even though the candidate is created (see OD-022), so this closes the dialog
    itself and finds the new row by searching."""
    open_directory(page)
    dialog = open_add_candidate(page)
    fill_candidate_form(dialog, name, email, phone, esic)
    dialog.get_by_role("button", name="Save Candidate").click()
    page.wait_for_timeout(2500)
    if dialog.is_visible():
        dialog.get_by_role("button", name="Cancel").click()
    return candidate_id(page, name)


def candidate_id(page: Page, name):
    open_directory(page, search=name)
    row = candidate_row(page, name)
    expect(row).to_have_count(1)
    return int(row.get_by_role("link", name="Review Profile").get_attribute("href").rstrip("/").split("/")[-1])


def delete_dialog(page: Page, title="Delete Onboarding"):
    return modal(page, title)


def delete_candidates(page: Page, text):
    """Deletes every candidate whose row contains `text` (used as test cleanup)."""
    open_directory(page, search=text)
    rows = candidate_rows(page).filter(has_text=text)
    for _ in range(10):
        if rows.count() == 0:
            break
        rows.first.get_by_role("button", name="Delete").click()
        delete_dialog(page).get_by_role("button", name="Delete", exact=True).click()
        expect_toast(page, "Onboarding record deleted successfully.")
        open_directory(page, search=text)
    expect(rows).to_have_count(0)


# ---------- field config ----------

def open_field_config(page: Page):
    goto(page, FIELD_CONFIG_URL)
    expect(main_content(page).get_by_role("heading", name="Onboarding Field Configuration")).to_be_visible()


def field_rows(page: Page):
    return main_content(page).locator("tbody tr").filter(has=page.get_by_role("switch"))


def field_row(page: Page, name):
    return field_rows(page).filter(has=page.get_by_text(name, exact=True))


def field_switch(page: Page, name):
    return field_row(page, name).get_by_role("switch")


def field_counts(page: Page):
    """(mandatory, optional, protected) from the summary cards."""
    text = main_content(page).inner_text()
    match = re.search(r"(\d+)\s*Mandatory\s*(\d+)\s*Optional\s*(\d+)\s*Protected", text)
    return tuple(int(n) for n in match.groups())


def counts_from_switches(page: Page):
    """(mandatory, optional, protected) worked out from the switches themselves (protected fields
    are mandatory too, so mandatory + optional is every field)."""
    switches = field_rows(page).get_by_role("switch")
    mandatory = switches.and_(page.locator("[aria-checked=true]")).count()
    return mandatory, switches.count() - mandatory, field_rows(page).filter(has_text="Protected").count()


def set_field_mandatory(page: Page, name, mandatory):
    """Turns a field's Mandatory switch on/off (no-op when it's already there)."""
    open_field_config(page)
    switch = field_switch(page, name)
    if (switch.get_attribute("aria-checked") == "true") != mandatory:
        switch.click()
        expect_toast(page, "Configuration updated successfully.")
        expect(switch).to_have_attribute("aria-checked", "true" if mandatory else "false")


def mandatory_fields(page: Page):
    """Snapshot of every field's Mandatory switch, so a test can put them all back."""
    open_field_config(page)
    return {row.locator("td").first.inner_text().strip(): row.get_by_role("switch").get_attribute("aria-checked") == "true"
            for row in field_rows(page).all()}


def restore_mandatory_fields(page: Page, snapshot):
    current = mandatory_fields(page)
    for name, mandatory in snapshot.items():
        if current.get(name) != mandatory:
            set_field_mandatory(page, name, mandatory)


# ---------- review profile ----------

def review_url(candidate_id):
    return f"{DIRECTORY_URL}/{candidate_id}"


def history_url(candidate_id):
    return f"{review_url(candidate_id)}/history"


def open_review(page: Page, candidate_id):
    goto(page, review_url(candidate_id))
    expect(main_content(page).get_by_text(re.compile(r"^\s*Onboarding Review\s*$", re.I))).to_be_visible()


def review_counters(page: Page):
    """(approved, requires correction, pending) from the review page header."""
    text = main_content(page).inner_text()
    match = re.search(r"APPROVED\s*(\d+)\s*REQUIRES CORRECTION\s*(\d+)\s*PENDING\s*(\d+)", text)
    return tuple(int(n) for n in match.groups())


def global_status(page: Page):
    return re.search(r"GLOBAL STATUS\s*\n\s*(.+)", main_content(page).inner_text()).group(1).strip()


def open_section(page: Page, name):
    nav_button(page, name).click()
    expect(current_section(page).locator("h3")).to_have_text(re.compile(rf"^{re.escape(name)}$", re.I))


def current_section(page: Page):
    return main_content(page).locator("main section").first


def review_row(page: Page, label):
    # one field per row: label (+ value / note) on the left, status badge and actions on the right
    return main_content(page).locator("main section div.divide-y > div").filter(
        has=page.locator("p", has_text=re.compile(rf"^{re.escape(label)}"))).first


def row_status(row):
    return row.locator("span.uppercase").last


def section_approve_selected(page: Page):
    return current_section(page).get_by_role("button", name=re.compile("Approve Selected", re.I))


def approve_selected_dialog(page: Page):
    return modal(page, "Approve Selected Items")


def approve_selected(page: Page, button):
    """Clicks an Approve Selected button and confirms the dialog."""
    button.click()
    dialog = approve_selected_dialog(page)
    expect(dialog.get_by_text("This will approve all selected fields and documents.")).to_be_visible()
    dialog.get_by_role("button", name="Approve Selected", exact=True).click()
    expect_toast(page, "Selected items bulk approved successfully.")
    expect(dialog).to_be_hidden()


def nav_button(page: Page, name):
    return main_content(page).get_by_role("button", name=re.compile(rf"^{re.escape(name)}", re.I))


def cross_check_panel(page: Page):
    # Preview File opens the document beside the section, under a "Cross Check" heading
    return main_content(page).locator("p", has_text=re.compile(r"^\s*Cross Check\s*$", re.I)).locator(
        "xpath=ancestor::div[.//img][1]")


def approve_field(page: Page, label):
    review_row(page, label).get_by_title("Approve").click()
    expect_toast(page, "Field review updated successfully.")
    expect(row_status(review_row(page, label))).to_have_text(re.compile("approved", re.I))


def reject_dialog(page: Page):
    return modal(page, "SUBMIT REJECTION")


def reject_field(page: Page, label, note):
    review_row(page, label).get_by_title("Reject").click()
    dialog = reject_dialog(page)
    dialog.locator("textarea").fill(note)
    dialog.get_by_role("button", name="SUBMIT REJECTION").click()
    expect(dialog).to_be_hidden()
    expect(row_status(review_row(page, label))).to_have_text(re.compile("rejected", re.I))


def edit_field_value(page: Page, label, value):
    row = review_row(page, label)
    row.get_by_title("Edit Value").click()
    row.locator("input[type=text]").fill(value)
    row.get_by_role("button", name="Save", exact=True).click()


def save_field_value(page: Page, label, value):
    """Edits a field and waits until the change is saved."""
    edit_field_value(page, label, value)
    expect_toast(page, "Field updated successfully.")
    expect(review_row(page, label).locator("input[type=text]")).to_have_count(0)


# ---------- audit trail ----------

def open_history(page: Page, candidate_id):
    goto(page, history_url(candidate_id))
    expect(main_content(page).get_by_role("heading", name="Audit Trail History")).to_be_visible()


def history_entries(page: Page):
    # every log entry has its own previous / new value table
    return main_content(page).locator("table")


def wait_for_history(page: Page, candidate_id, count, timeout=30):
    """Audit entries are written in the background a few seconds after the change, so keep
    reloading the history until `count` entries are there."""
    for _ in range(timeout // 3):
        open_history(page, candidate_id)
        if history_entries(page).count() >= count:
            break
        page.wait_for_timeout(3000)
    expect(history_entries(page)).to_have_count(count)


def history_search(page: Page):
    return main_content(page).get_by_placeholder("Search by user, action, or document name...")


def history_filter(page: Page, label):
    """label: 'All Logs' (entity type) or 'All Actions' (action type) select."""
    return main_content(page).locator("select").filter(has=page.locator("option", has_text=label))


# ---------- journeys ----------

def journey_url(journey_id):
    return f"{JOURNEYS_URL}/{journey_id}"


def open_journeys(page: Page):
    goto(page, JOURNEYS_URL)
    expect(main_content(page).get_by_role("heading", name="Onboarding Journeys")).to_be_visible()


def journey_card(page: Page, name):
    # the smallest block holding the journey name and its own Manage Steps link
    return main_content(page).get_by_text(name, exact=True).locator(
        "xpath=ancestor::div[.//a[normalize-space()='Manage Steps']][1]")


def journey_stats(page: Page):
    """(total, active, total steps) from the summary cards."""
    text = main_content(page).inner_text()
    match = re.search(r"Total Journeys\s*(\d+)\s*Active\s*(\d+)\s*Total Steps\s*(\d+)", text)
    return tuple(int(n) for n in match.groups())


def journey_dialog(page: Page, title="Create Onboarding Journey"):
    return modal(page, title)


def open_create_journey(page: Page):
    main_content(page).get_by_role("button", name="Create Journey").click()
    dialog = journey_dialog(page)
    expect(dialog).to_be_visible()
    return dialog


def active_switch(dialog):
    # the Active toggle is a plain button next to the "Active" label; on = indigo
    return dialog.locator("div.flex.items-center.gap-3", has_text="Active").locator("button").first


def is_active_on(dialog):
    return "bg-indigo-600" in (active_switch(dialog).get_attribute("class") or "")


def fill_journey_form(page: Page, dialog, name=None, designation=None, description=None, active=None):
    if name is not None:
        dialog.get_by_placeholder("e.g., Software Engineer Onboarding").fill(name)
    if designation is not None:
        vue_select(page, dialog, "Select Designation", designation)
    if description is not None:
        dialog.get_by_placeholder("Briefly describe the purpose of this journey...").fill(description)
    if active is not None and is_active_on(dialog) != active:
        active_switch(dialog).click()


def unique_journey_name():
    return f"{QA_JOURNEY_PREFIX} {unique_tag()}"


def create_journey(page: Page, name, designation=None, description=None, active=None):
    """Creates a journey and returns its id (the app redirects to its Manage Steps page)."""
    open_journeys(page)
    dialog = open_create_journey(page)
    fill_journey_form(page, dialog, name, designation, description, active)
    dialog.get_by_role("button", name="Create Journey").click()
    expect_toast(page, "Onboarding journey created successfully.")
    page.wait_for_url(re.compile(r"/journeys/\d+$"))
    settle(page)
    return int(page.url.rstrip("/").split("/")[-1])


def delete_journeys(page: Page, name):
    """Deletes every journey called `name` (used as test cleanup)."""
    open_journeys(page)
    names = main_content(page).get_by_text(name, exact=True)
    for _ in range(10):
        if names.count() == 0:
            break
        journey_card(page, name).first.get_by_role("button", name="Delete").click()
        modal(page, "Delete Journey").get_by_role("button", name="Delete", exact=True).click()
        expect_toast(page, "Onboarding journey deleted successfully.")
        open_journeys(page)
    expect(names).to_have_count(0)


# ---------- manage steps ----------

def open_steps(page: Page, journey_id):
    goto(page, journey_url(journey_id))
    expect(main_content(page).get_by_role("link", name="Back to Journeys")).to_be_visible()


def step_titles(page: Page):
    """Step titles in order."""
    buttons = main_content(page).get_by_role("button", name="Delete step")
    titles = []
    for i in range(buttons.count()):
        card = buttons.nth(i).locator("xpath=ancestor::div[.//h3 or .//h4][1]")
        titles.append(card.locator("h3, h4").first.inner_text().strip())
    return titles


SESSIONS = ["Engineering Foundations", "Materials Only"]


def step_cards(page: Page):
    # one card per step, holding its number, title, Required badge, description and the four actions
    return main_content(page).get_by_role("button", name="Delete step").locator("xpath=ancestor::div[.//h3 or .//h4][1]")


def add_step_dialog(page: Page):
    return modal(page, "Add Step to")


def add_step(page: Page, session):
    main_content(page).get_by_role("button", name="Add Step").first.click()
    dialog = add_step_dialog(page)
    vue_select(page, dialog, "Select a session", session)
    dialog.get_by_role("button", name="Add Step").click()
    expect_toast(page, "Step added successfully.")
    expect(dialog).to_be_hidden()


# ---------- journey progress ----------

def progress_url(search="", role="", journey="", status=""):
    return f"{PROGRESS_URL}?journey={quote(journey)}&role={role}&search={quote(search)}&status={status}"


def open_progress(page: Page, url=PROGRESS_URL):
    goto(page, url)
    expect(main_content(page).get_by_role("heading", name="Employee Journey Progress")).to_be_visible()


def progress_rows(page: Page):
    return main_content(page).locator("tbody tr").filter(has=page.get_by_role("link", name="View Journey Progress"))


def progress_row(page: Page, name):
    return progress_rows(page).filter(has=page.get_by_text(name, exact=True))


def progress_search(page: Page):
    return main_content(page).get_by_placeholder("Search employee...")


def progress_values(page: Page):
    """[(percent, done, total, status)] for every row on the page."""
    values = []
    for text in progress_rows(page).all_inner_texts():
        match = re.search(r"(\d+)%\s*(\d+) / (\d+) steps completed\s*(IN PROGRESS|COMPLETED)", text, re.I)
        assert match, text
        values.append((int(match.group(1)), int(match.group(2)), int(match.group(3)), match.group(4).upper()))
    return values


def user_progress_url(user_id):
    return f"{DIRECTORY_URL}/users/{user_id}/onboarding-progress"


def open_user_progress(page: Page, user_id):
    goto(page, user_progress_url(user_id))
    expect(main_content(page).get_by_role("heading", name="Onboarding Progress")).to_be_visible()


def roadmap_steps(page: Page):
    return main_content(page).get_by_role("button", name="Quiz Performance")


# ---------- OCR analytics ----------

def open_analytics(page: Page):
    goto(page, ANALYTICS_URL)
    expect(main_content(page).get_by_role("heading", name="Onboarding Document Analytics")).to_be_visible()


def analytics_card(page: Page, heading):
    return main_content(page).locator("h2", has_text=heading).locator("xpath=ancestor::div[contains(@class,'rounded')][1]")


def analytics_table(page: Page, heading):
    return analytics_card(page, heading).locator("table")


def kpi_value(page: Page, label):
    return main_content(page).locator("p", has_text=re.compile(rf"^{re.escape(label)}$")).locator(
        "xpath=following-sibling::p[1]").inner_text().strip()
