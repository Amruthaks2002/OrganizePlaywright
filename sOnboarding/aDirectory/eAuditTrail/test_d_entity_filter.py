from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, wait_for_history, history_entries, history_filter,
    main_content, settle, delete_candidates,
)


def test_entity_filter():
    """AT-004: the entity filter narrows the log - a new candidate has profile entries but no document reviews."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            wait_for_history(page, candidate_id, 1)

            history_filter(page, "All Logs").select_option("document")
            settle(page)
            expect(main_content(page).get_by_text("No logs found")).to_be_visible()
            expect(history_entries(page)).to_have_count(0)

            history_filter(page, "All Logs").select_option("profile")
            settle(page)
            expect(history_entries(page)).to_have_count(1)
        finally:
            delete_candidates(page, data["name"])

        browser.close()
