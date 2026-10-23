from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, wait_for_history, history_entries, history_filter,
    history_search, main_content, settle, delete_candidates,
)


def test_reset_filters():
    """AT-007: Reset and "Clear all filters" put every filter back and show all entries again."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            wait_for_history(page, candidate_id, 1)
            main = main_content(page)

            for clear in ["Reset", "Clear all filters"]:
                history_filter(page, "All Logs").select_option("document")
                history_filter(page, "All Actions").select_option("deleted")
                history_search(page).fill("zzqa")
                settle(page)
                expect(main.get_by_text("No logs found")).to_be_visible()

                main.get_by_role("button", name=clear).click()
                settle(page)
                expect(history_filter(page, "All Logs")).to_have_value("all")
                expect(history_filter(page, "All Actions")).to_have_value("all")
                expect(history_search(page)).to_have_value("")
                expect(history_entries(page)).to_have_count(1)
        finally:
            delete_candidates(page, data["name"])

        browser.close()
