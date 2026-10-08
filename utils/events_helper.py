import json
import re
import uuid
from datetime import date, timedelta
from urllib.parse import quote

from playwright.sync_api import Page, expect
from utils.learning_helper import (  # noqa: F401  (re-exported for the tests)
    BASE_URL, open_browser, main_content, expect_toast, settle, goto,
)
from utils.onboarding_helper import open_browser_as  # noqa: F401
from utils.asset_helper import bulk_post  # noqa: F401

EVENTS_URL = f"{BASE_URL}/manage/events"
BULK_DELETE = "/manage/events/bulk-delete"

QA_EVENT_PREFIX = "QA Event"
EMPTY_LIST = "No events scheduled yet."
CATEGORIES = {"Celebrations": "1", "Competitions": "2", "Workshops": "3", "Knowledge Session": "4",
              "Fun activities": "5", "Wellness": "6"}
PAGE_SIZE = 6


def unique_prefix():
    # random suffix so tests running in parallel never search up each other's events
    return f"{QA_EVENT_PREFIX} {uuid.uuid4().hex[:6]}"


# ---------- list ----------

def events_url(search="", status="", page_no=None):
    # empty dates switch off the default "next two months" range, so every matching event shows
    url = f"{EVENTS_URL}?search={quote(search)}&start_date=&end_date=&status={status}&event_category_id="
    return url + (f"&page={page_no}" if page_no else "")


def open_events(page: Page, search="", status="", page_no=None):
    goto(page, events_url(search, status, page_no))
    expect(main_content(page).get_by_role("heading", name="Events Manager")).to_be_visible()


def card_boxes(page: Page):
    # each event card has a big checkbox in its top-left corner
    return main_content(page).locator("input[type=checkbox].w-6")


def event_cards(page: Page):
    return card_boxes(page).locator("xpath=ancestor::div[.//h3][1]")


def event_card(page: Page, title):
    return event_cards(page).filter(has=page.locator("h3", has_text=re.compile(rf"^\s*{re.escape(title)}\s*$")))


def card_box(page: Page, title):
    return event_card(page, title).locator("input[type=checkbox].w-6")


def card_titles(page: Page):
    return [t.strip() for t in event_cards(page).locator("h3").all_inner_texts()]


def checked_cards(page: Page):
    return main_content(page).locator("input[type=checkbox].w-6:checked")


def select_all_box(page: Page):
    return main_content(page).get_by_text("Select All", exact=True).locator("xpath=..").locator("input[type=checkbox]")


def select_cards(page: Page, *titles):
    for title in titles:
        card_box(page, title).check()
    expect_selected(page, len(titles))


def go_to_page(page: Page, number):
    # the pager renders a hidden mobile copy too, so click the visible numbered link
    main_content(page).locator(f"a[href*='page={number}']:visible", has_text=str(number)).first.click()
    page.wait_for_url(re.compile(rf"[?&]page={number}\b"))
    settle(page)


# ---------- selection dock ----------

def dock(page: Page):
    return page.get_by_role("toolbar")


def dock_clear(page: Page):
    return page.get_by_test_id("selection-dock-clear")


def dock_delete(page: Page):
    return dock(page).get_by_role("button", name="Delete", exact=True)


def expect_selected(page: Page, count):
    label = "event selected" if count == 1 else "events selected"
    expect(dock(page)).to_be_visible()
    expect(dock(page)).to_contain_text(re.compile(rf"^\s*{count}\s*{label}"))


# ---------- bulk delete ----------

def delete_dialog(page: Page):
    return page.locator("div.fixed.inset-0:visible").filter(has_text="Bulk Delete Events").last


def open_bulk_delete(page: Page):
    dock_delete(page).click()
    dialog = delete_dialog(page)
    expect(dialog).to_be_visible()
    return dialog


def confirm_delete(page: Page, count):
    dialog = open_bulk_delete(page)
    dialog.get_by_role("button", name="Delete", exact=True).click()
    expect_toast(page, f"Successfully deleted {count} event(s)!")
    expect(dialog).to_be_hidden()


# ---------- create / cleanup ----------

def create_event(page: Page, title, category="Celebrations", days_ahead=1, active=True):
    """Creates an event through the Create Event dialog (Description is required: without it the
    save silently does nothing)."""
    goto(page, EVENTS_URL)
    main_content(page).get_by_role("button", name="Create Event", exact=True).click()
    page.locator("#title").fill(title)
    page.locator("#category").select_option(CATEGORIES[category])
    page.locator("#event_date").fill((date.today() + timedelta(days=days_ahead)).isoformat())
    if not active:
        page.locator("#title").locator("xpath=ancestor::form[1]").get_by_text("Inactive", exact=True).click()
    page.locator("#description").fill("Created by the bulk select tests.")
    page.get_by_role("button", name="Create Event", exact=True).last.click()
    expect_toast(page, "Event created successfully.")


def create_events(page: Page, prefix, count=2):
    """Creates `prefix 1`, `prefix 2`, ... and returns their titles."""
    titles = [f"{prefix} {i}" for i in range(1, count + 1)]
    for i, title in enumerate(titles, 1):
        create_event(page, title, days_ahead=i)
    return titles


def event_ids(page: Page, prefix):
    """Ids of the events matching `prefix`, read from what a bulk delete would send (the request
    is intercepted and dropped, so nothing is deleted)."""
    sent = []

    def capture(route):
        body = route.request.post_data
        route.abort()
        sent.append(body)

    # a throwaway tab, since the dropped request leaves the page unable to navigate
    tab = page.context.new_page()
    try:
        open_events(tab, search=prefix)
        count = card_boxes(tab).count()
        tab.route(f"**{BULK_DELETE}", capture)
        select_all_box(tab).check()
        expect_selected(tab, count)
        open_bulk_delete(tab).get_by_role("button", name="Delete", exact=True).click()
        tab.wait_for_timeout(1500)
    finally:
        tab.close()
    return json.loads(sent[0])["ids"]


def delete_events(page: Page, prefix):
    """Bulk-deletes every event matching `prefix` (used as test cleanup)."""
    open_events(page, search=prefix)
    count = card_boxes(page).count()
    if count == 0:
        return
    select_all_box(page).check()
    expect_selected(page, count)
    confirm_delete(page, count)
    open_events(page, search=prefix)
    expect(card_boxes(page)).to_have_count(0)
