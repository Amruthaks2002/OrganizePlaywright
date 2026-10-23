from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, wait_for_history, history_entries, history_search,
    main_content, settle, delete_candidates,
)


def test_search_by_action():
    """AT-006: searching the log by action ("created") finds the matching entry; an unknown term finds nothing."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            wait_for_history(page, candidate_id, 1)

            history_search(page).fill("created")
            settle(page)
            expect(history_entries(page)).to_have_count(1)

            history_search(page).fill("zzqa-no-such-log")
            expect(main_content(page).get_by_text("No logs found")).to_be_visible()
            expect(history_entries(page)).to_have_count(0)
        finally:
            delete_candidates(page, data["name"])

        browser.close()
