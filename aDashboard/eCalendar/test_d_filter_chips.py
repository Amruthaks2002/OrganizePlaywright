from playwright.sync_api import sync_playwright
from utils.dashboard_helper import (open_browser_as, open_dashboard, choose_chip, event_types, retry_if_data_changed,
                                    CALENDAR_CHIPS)


def test_filter_chips():
    """DB-028: each filter chip shows only its own kind of calendar item, and All Events brings
    every kind back."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")

        def check():
            open_dashboard(page)
            everything = sorted(event_types(page))
            for label, kind in CALENDAR_CHIPS.items():
                choose_chip(page, label)
                kinds = set(event_types(page))
                assert kinds <= {kind}, f"{label} shows {kinds}"
                assert len(event_types(page)) == everything.count(kind), \
                    f"{label} shows {len(event_types(page))}, All Events has {everything.count(kind)}"
            choose_chip(page, "ALL EVENTS")
            assert sorted(event_types(page)) == everything

        retry_if_data_changed(check)
        browser.close()
