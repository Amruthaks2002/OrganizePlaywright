from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, wait_for_history, history_entries, history_search, settle,
    delete_candidates,
)


def test_search_by_user():
    """AT-008: searching the log by the user who made the change ("Admin User") finds their entries,
    as the "Search by user, action, or document name..." placeholder promises.

    Known bug: searching by user (or field name) finds nothing - only action names match.
    This test fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            wait_for_history(page, candidate_id, 1)

            history_search(page).fill("Admin User")
            settle(page)
            page.wait_for_timeout(1000)
            expect(history_entries(page), "searching by user found nothing").to_have_count(1)
        finally:
            delete_candidates(page, data["name"])

        browser.close()
