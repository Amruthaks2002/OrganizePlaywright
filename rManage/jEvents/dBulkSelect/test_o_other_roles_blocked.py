import re

from playwright.sync_api import sync_playwright, expect
from utils.events_helper import (
    open_browser, open_browser_as, unique_prefix, create_events, delete_events, open_events, event_ids,
    card_titles, bulk_post, EVENTS_URL, BULK_DELETE,
)


def test_other_roles_blocked():
    """EB-015: employees, team leads and project managers get 403 on the Events manager, and their
    direct bulk-delete calls are refused with 403 without deleting anything."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            titles = create_events(page, prefix)
            ids = event_ids(page, prefix)

            for role in ["employee", "team-lead", "project-manager"]:
                role_browser, role_page = open_browser_as(p, role)
                response = role_page.goto(EVENTS_URL, wait_until="domcontentloaded")
                assert response.status == 403, f"{role}: expected 403, got {response.status}"
                expect(role_page).to_have_title(re.compile("Forbidden"))
                expect(role_page.get_by_test_id("sidebar-child-events")).to_have_count(0)
                status, body = bulk_post(role_page, BULK_DELETE, {"ids": ids})
                assert status == 403, f"{role} bulk delete: expected 403, got {status} {body}"
                role_browser.close()

            open_events(page, search=prefix)
            assert sorted(card_titles(page)) == sorted(titles), card_titles(page)
        finally:
            delete_events(page, prefix)

        browser.close()
