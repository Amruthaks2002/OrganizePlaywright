import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, retry_if_data_changed, choose_chip, chip_count, event_types, calendar_events, month_cells,
                                    MODAL, CALENDAR_CHIPS, EVENT_POPUP_LABELS)

# these chips add up days (a half-day request counts 0.5), the rest count items
DURATION_CHIPS = {"LEAVES": "leave", "WORK MODE": "work_mode"}


def total_days(page, kind):
    days = 0.0
    events = calendar_events(month_cells(page), kind)
    for i in range(events.count()):
        events.nth(i).click()
        page.wait_for_timeout(700)  # let the popup finish opening
        popup = page.locator(MODAL).last
        expect(popup).to_contain_text(re.compile(EVENT_POPUP_LABELS[kind], re.I))
        days += float(re.search(r"DURATION\s*\n\s*([\d.]+)\s*days?", popup.inner_text(), re.I).group(1))
        popup.get_by_role("button", name="Close").click()
        page.wait_for_timeout(700)  # and finish closing before the next one
    return days


def test_chip_counts():
    """DB-029: the number on each filter chip matches the month: Holidays, Birthdays, Anniversaries and
    Notes count their items, while Leaves and Work Mode add up days (so two half-days count as 1).

    The Notes chip has no number when it is zero, which counts as 0."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")

        def check():
            open_dashboard(page)
            kinds = event_types(page)
            mismatches = {label: (chip_count(page, label), kinds.count(kind))
                          for label, kind in CALENDAR_CHIPS.items()
                          if label not in DURATION_CHIPS and chip_count(page, label) != kinds.count(kind)}

            for label, kind in DURATION_CHIPS.items():
                choose_chip(page, label)  # only this kind, so nothing is folded under '+N more'
                days = total_days(page, kind)
                if chip_count(page, label) != round(days):
                    mismatches[label] = (chip_count(page, label), days)
            assert not mismatches, f"chip count vs month (items or days): {mismatches}"

        retry_if_data_changed(check)
        browser.close()
