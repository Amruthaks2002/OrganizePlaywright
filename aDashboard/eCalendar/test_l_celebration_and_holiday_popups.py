import re

import pytest
from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, find_month_with, event_date, modal, ui_date,
                                    EVENT_POPUP_LABELS)


def test_celebration_and_holiday_popups():
    """DB-036: clicking a holiday, birthday or anniversary opens a popup with its type, name and date."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        found = 0
        for kind in ["holiday", "birthday", "anniversary"]:
            open_dashboard(page)
            event = find_month_with(page, kind)
            if event is None:
                continue
            found += 1
            # the calendar decorates names ("anu 🎂", "Anish Mohan K (2 years 🎉)"); the popup shows the bare name
            name = re.sub(r"\s*(🎂|\(.*\))\s*$", "", event.inner_text().strip())
            day = event_date(event)
            event.click()
            popup = modal(page, EVENT_POPUP_LABELS[kind])
            # the type label is upper-cased by CSS only
            expect(popup.get_by_text(re.compile(rf"^\s*{EVENT_POPUP_LABELS[kind]}\s*$", re.I))).to_be_visible()
            expect(popup).to_contain_text(name)
            expect(popup).to_contain_text(ui_date(day))
            popup.get_by_role("button", name="Close").click()
            expect(popup).to_be_hidden()
        if not found:
            pytest.skip("no holidays or celebrations in the next six months")
        browser.close()
