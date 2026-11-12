"""WM-023: Pagination.

Steps:
1. Open Work Mode Audit Logs and set the dates to the year up to yesterday (several pages that don't move while
   new logs are written).
2. Use page 2, Previous, Next and the last page number.

Expected:
- 20 rows a page; on page 1 Previous is disabled and page 1 is highlighted.
- Page 2 shows different rows and is highlighted; Previous goes back to page 1's rows and Next to page 2's.
- The last page has the remaining rows (total - 20 x (pages - 1)) and Next is disabled there.
"""
import time
from datetime import date, timedelta

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/work-mode-logs"
SUBTITLE = "A complete history of all work mode-related actions."
EMPTY_MESSAGE = "No logs found for the selected criteria."


def open_work_mode_logs(page):
    """Logs in as admin and opens Logs > Work Mode Logs from the sidebar (Logs sits in the collapsed System section)."""
    login(page)
    page.get_by_test_id("sidebar-navigation").wait_for(state="visible")
    if not page.get_by_test_id("sidebar-parent-logs").is_visible():
        page.get_by_test_id("sidebar-section-system").dispatch_event("click")
    link = page.get_by_test_id("sidebar-child-work-mode-logs")
    if not link.is_visible():
        page.get_by_test_id("sidebar-parent-logs").click()
    link.wait_for(state="visible")
    link.click()
    page.get_by_text(SUBTITLE).wait_for(state="visible")
    time.sleep(1)


def refresh(page, action):
    """Runs a filter action and returns the props of the reload it triggers (filters are applied server side)."""
    with page.expect_response(lambda r: "/work-mode-logs" in r.url and r.request.method == "GET") as info:
        action()
    time.sleep(1)
    props = info.value.json()["props"]
    props["filters"] = props["filters"] or {}  # the app sends [] when nothing is filtered
    return props


def table_rows(page):
    """Visible log rows as dicts (the empty-state row has a single cell and is skipped)."""
    rows = []
    for row in page.locator("table tbody tr").all():
        cells = row.locator("td")
        if cells.count() != 5:
            continue
        rows.append({
            "timestamp": cells.nth(0).inner_text().strip(),
            "employee": cells.nth(1).inner_text().strip(),
            "action_by": cells.nth(2).inner_text().strip(),
            "action": cells.nth(3).inner_text().strip(),
            "description": cells.nth(4).locator("p").first.inner_text().strip(),
            "details": cells.nth(4).inner_text().strip(),
        })
    return rows


def from_date(page):
    return page.locator("input[type='date']").first


def to_date(page):
    return page.locator("input[type='date']").last


def set_dates(page, start, end):
    """Sets the From/To boxes (in an order that never makes From later than To) and returns the last reload's props,
    or None when both already held those values."""
    props = None
    boxes = [(from_date(page), start), (to_date(page), end)]
    if to_date(page).input_value() and start > to_date(page).input_value():
        boxes.reverse()
    for box, value in boxes:
        if box.input_value() != value:
            props = refresh(page, lambda: box.fill(value))
    return props


def wide_range():
    """The year up to yesterday: wide enough to have logs of most kinds, and ending yesterday so logs being written
    right now (by other tests or users) don't shift the rows while a test reads them."""
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), (today - timedelta(days=1)).isoformat()


def pagination(page):
    return page.locator("nav").filter(has=page.locator("a[href*='page=']")).last


ACTIVE = "bg-indigo-600"


def first_row(page):
    return table_rows(page)[0]


def test_wm_023_pagination():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        open_work_mode_logs(page)

        props = set_dates(page, *wide_range())
        total, last_page = props["logs"]["total"], props["logs"]["last_page"]
        assert last_page >= 3, f"only {last_page} pages in the year up to yesterday"
        assert len(table_rows(page)) == 20

        nav = pagination(page)
        assert nav.locator(":scope > *").first.evaluate("e => e.tagName") == "SPAN", "Previous is enabled on page 1"
        assert ACTIVE in nav.get_by_role("link", name="1", exact=True).get_attribute("class")
        page1 = first_row(page)

        refresh(page, lambda: pagination(page).get_by_role("link", name="2", exact=True).click())
        page2 = first_row(page)
        assert page2 != page1
        nav = pagination(page)
        assert ACTIVE in nav.get_by_role("link", name="2", exact=True).get_attribute("class")
        assert nav.locator(":scope > *").first.evaluate("e => e.tagName") == "A", "Previous is disabled on page 2"

        refresh(page, lambda: pagination(page).locator(":scope > *").first.click())
        assert first_row(page) == page1, "Previous didn't go back to page 1"
        refresh(page, lambda: pagination(page).locator(":scope > *").last.click())
        assert first_row(page) == page2, "Next didn't go to page 2"

        props = refresh(page, lambda: pagination(page).get_by_role("link", name=str(last_page), exact=True).click())
        assert props["logs"]["current_page"] == last_page
        assert len(table_rows(page)) == total - 20 * (last_page - 1)
        assert pagination(page).locator(":scope > *").last.evaluate("e => e.tagName") == "SPAN", "Next is enabled on the last page"

        browser.close()
