import re
import uuid

from playwright.sync_api import Page, expect
from utils.learning_helper import (  # noqa: F401  (re-exported for the tests)
    BASE_URL, open_browser, main_content, expect_toast, settle, goto,
)

POLICIES_URL = f"{BASE_URL}/leave-policies"
TEST_POLICY_PREFIX = "QA Policy"
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def unique_policy_name():
    # random suffix so tests running in parallel never pick the same name
    return f"{TEST_POLICY_PREFIX} {uuid.uuid4().hex[:8]}"


def open_leave_policies(page: Page):
    # the Leave Management group is already expanded when we're on one of its pages
    if not page.get_by_test_id("sidebar-child-leave-policies").is_visible():
        page.get_by_test_id("sidebar-parent-leave management").click()
    page.get_by_test_id("sidebar-child-leave-policies").click()
    page.wait_for_url("**/leave-policies")
    settle(page)
    expect(policy_cards(page).first).to_be_visible()


# ---------- policy list (left column) ----------

def policy_list(page: Page):
    return main_content(page).locator("div[class*='lg:w-72']")


def policy_cards(page: Page):
    return policy_list(page).locator("button.rounded-xl")


def policy_card(page: Page, name):
    return policy_cards(page).filter(has=page.get_by_text(name, exact=True))


def card_name(card):
    return card.locator("span.truncate")


def card_status(card):
    return card.locator("span.rounded-full")


def card_meta(card):
    # second row: optional region, then the employee count
    return card.locator("> div").nth(1)


def card_employee_count(card):
    return int(card_meta(card).locator("span").last.inner_text().strip())


def policy_names(page: Page):
    return [n.strip() for n in policy_list(page).locator("button.rounded-xl span.truncate").all_inner_texts()]


def is_test_policy(name):
    # policies created (and deleted) by other tests that may be running at the same time
    return name.startswith(TEST_POLICY_PREFIX)


def existing_policy_names(page: Page):
    return [n for n in policy_names(page) if not is_test_policy(n)]


def select_policy(page: Page, name):
    policy_card(page, name).click()
    expect(detail_name(page)).to_have_text(name)


# ---------- detail panel (right column) ----------

def detail_header(page: Page):
    return main_content(page).locator("div.p-5").filter(has=page.locator("h2"))


def detail_name(page: Page):
    return detail_header(page).locator("h2")


def detail_badges(page: Page):
    # status badge first, then region (if set)
    return detail_header(page).locator("h2 ~ span")


def detail_description(page: Page):
    return detail_header(page).locator("p")


def employees_section(page: Page):
    return main_content(page).locator("div.p-5").filter(has=page.get_by_text("Employees", exact=True))


def employees_count(page: Page):
    return int(employees_section(page).get_by_text("Employees", exact=True)
               .locator("xpath=following-sibling::span[1]").inner_text().strip())


def employee_names(page: Page):
    return [n.strip() for n in employees_section(page).locator("div.space-y-2 > div span.truncate").all_inner_texts()]


def items_section(page: Page, title):
    """'Leave Types' or 'Work Modes' block of the selected policy."""
    return main_content(page).get_by_text(title, exact=True).locator("xpath=../..")


def items_count(page: Page, title):
    return int(main_content(page).get_by_text(title, exact=True)
               .locator("xpath=following-sibling::span[1]").inner_text().strip())


def item_rows(page: Page, title):
    return items_section(page, title).locator("div.space-y-2 > div")


def item_names(page: Page, title):
    return [r.locator("span").first.inner_text().strip() for r in item_rows(page, title).all()]


# ---------- modals ----------

def dialog(page: Page, heading):
    return page.locator("div.modal-surface").filter(has=page.get_by_text(heading, exact=True)).last


def policy_form(page: Page, heading="Create Policy"):
    return dialog(page, heading).locator("form")


def close_x(modal):
    # the small X next to the modal heading
    return modal.locator("h3 + button")


def open_create_form(page: Page):
    main_content(page).get_by_role("button", name="Create Policy").click()
    form = policy_form(page, "Create Policy")
    expect(form).to_be_visible()
    return form


def open_edit_form(page: Page, name):
    select_policy(page, name)
    detail_header(page).get_by_role("button", name="Edit", exact=True).click()
    form = policy_form(page, "Edit Leave Policy")
    expect(form).to_be_visible()
    return form


def name_input(form):
    return form.get_by_placeholder("e.g. Standard Policy")


def region_input(form):
    return form.get_by_placeholder("e.g. Global, APAC")


def description_input(form):
    return form.get_by_placeholder("Optional description...")


def active_toggle(form):
    return form.locator("label").filter(has_text=re.compile(r"^\s*Active\s*$")).locator("input")


def set_active(form, active):
    toggle = active_toggle(form)
    if toggle.is_checked() != active:
        form.locator("label").filter(has_text=re.compile(r"^\s*Active\s*$")).click()
    expect(toggle).to_be_checked(checked=active)


def weekend_checkbox(form, day):
    return form.get_by_label(day, exact=True)


def set_weekends(form, days):
    for day in WEEKDAYS:
        weekend_checkbox(form, day).set_checked(day in days)


def checked_weekends(form):
    return [day for day in WEEKDAYS if weekend_checkbox(form, day).is_checked()]


def copy_column(form, title):
    """'Copy Leave Type' or 'Copy Work Mode' column of the policy form."""
    return form.locator("div.w-1\\/2").filter(has=form.page.get_by_text(title, exact=True))


def copy_source(form, title):
    return copy_column(form, title).locator("select")


def copy_items(form, title):
    return copy_column(form, title).locator("label:has(input[type=checkbox])")


def copy_item(form, title, item):
    return copy_items(form, title).filter(has=form.page.get_by_text(item, exact=True))


def copy_item_names(form, title):
    return [i.locator("span").first.inner_text().strip() for i in copy_items(form, title).all()]


def copy_counter(form, title):
    return copy_column(form, title).get_by_text(re.compile(r"\d+ / \d+ selected"))


def copy_note(form, title):
    return copy_column(form, title).get_by_text("will be copied to this policy")


def fill_policy_form(form, name=None, region=None, description=None, active=None, weekends=None,
                     copy_from=None, leave_types=(), work_modes=()):
    if name is not None:
        name_input(form).fill(name)
    if region is not None:
        region_input(form).fill(region)
    if description is not None:
        description_input(form).fill(description)
    if active is not None:
        set_active(form, active)
    if weekends is not None:
        set_weekends(form, weekends)
    if copy_from:
        copy_source(form, "Copy Leave Type").select_option(label=copy_from)
        copy_source(form, "Copy Work Mode").select_option(label=copy_from)
    for item in leave_types:
        copy_item(form, "Copy Leave Type", item).locator("input").check()
    for item in work_modes:
        copy_item(form, "Copy Work Mode", item).locator("input").check()


def create_policy(page: Page, name, **fields):
    """Creates a policy through the Create Policy form and waits for the success toast."""
    form = open_create_form(page)
    fill_policy_form(form, name=name, **fields)
    form.get_by_role("button", name="Create Policy").click()
    expect_toast(page, "Leave policy created successfully.")
    expect(form).to_be_hidden()
    # the list refreshes in the background after a save and re-renders any form
    # opened meanwhile, so start the test from a freshly loaded page
    goto(page, POLICIES_URL)
    expect(policy_card(page, name)).to_have_count(1)


def delete_dialog(page: Page):
    return dialog(page, "Delete Leave Policy")


def delete_policy(page: Page, name):
    """Deletes every policy with this name (used as test cleanup)."""
    goto(page, POLICIES_URL)
    expect(policy_cards(page).first).to_be_visible()
    while policy_card(page, name).count() > 0:
        select_policy(page, name)
        detail_header(page).get_by_role("button", name="Delete", exact=True).click()
        delete_dialog(page).get_by_role("button", name="Delete", exact=True).click()
        expect_toast(page, "Leave policy deleted successfully.")
        goto(page, POLICIES_URL)
        expect(policy_cards(page).first).to_be_visible()
    expect(policy_card(page, name)).to_have_count(0)


def policy_with_employees(page: Page, minimum=1):
    """Name of an existing policy with at least `minimum` employees."""
    for card in policy_cards(page).all():
        if card_employee_count(card) >= minimum:
            return card_name(card).inner_text().strip()
    raise AssertionError(f"no leave policy with at least {minimum} employees")


def employees_dialog(page: Page):
    return page.locator("div.modal-surface").filter(has=page.get_by_placeholder("Search employees..."))


def employees_dialog_rows(page: Page):
    return employees_dialog(page).locator("div.space-y-1 > div")


def employees_dialog_names(page: Page):
    return [n.strip() for n in employees_dialog_rows(page).locator("p.truncate").all_inner_texts()]


def profile_card(page: Page, name):
    return page.get_by_role("dialog", name=f"{name} profile card")
