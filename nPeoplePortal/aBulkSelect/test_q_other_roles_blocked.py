import re

from playwright.sync_api import sync_playwright, expect
from utils.people_portal_helper import (
    open_browser, open_browser_as, unique_prefix, create_queries, delete_queries, open_portal, query_row,
    row_assignee, row_id, bulk_post, PORTAL_URL, BULK_ASSIGN, BULK_DELETE, FASNA_ID,
)


def test_other_roles_blocked():
    """PB-017: team leads and project managers get 403 on the People Portal control center, and their
    direct bulk assign / delete calls change nothing."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            subjects = create_queries(p, prefix)
            open_portal(page, search=prefix)
            ids = [row_id(query_row(page, s)) for s in subjects]

            for role in ["team-lead", "project-manager"]:
                role_browser, role_page = open_browser_as(p, role)
                response = role_page.goto(PORTAL_URL, wait_until="domcontentloaded")
                assert response.status == 403, f"{role}: expected 403, got {response.status}"
                expect(role_page).to_have_title(re.compile("Forbidden"))
                for path, data in [(BULK_ASSIGN, {"query_ids": ids, "user_ids": [str(FASNA_ID)]}),
                                   (BULK_DELETE, {"query_ids": ids})]:
                    status, body = bulk_post(role_page, path, data)
                    assert status == 403, f"{role} {path}: expected 403, got {status} {body}"
                role_browser.close()

            open_portal(page, search=prefix)
            for subject in subjects:
                expect(row_assignee(query_row(page, subject))).to_have_text("Unassigned")
        finally:
            delete_queries(page, prefix)

        browser.close()
