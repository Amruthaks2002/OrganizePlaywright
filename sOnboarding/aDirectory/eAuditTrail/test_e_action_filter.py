from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_review, save_field_value, wait_for_history,
    history_entries, history_filter, main_content, settle, delete_candidates,
)


def test_action_filter():
    """AT-005: the action filter shows only Created / Updated / Deleted entries."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            open_review(page, candidate_id)
            save_field_value(page, "Designation", "QA Engineer")
            wait_for_history(page, candidate_id, 2)

            history_filter(page, "All Actions").select_option("created")
            settle(page)
            expect(history_entries(page)).to_have_count(1)
            expect(history_entries(page).first).to_contain_text(data["email"])

            history_filter(page, "All Actions").select_option("updated")
            settle(page)
            expect(history_entries(page)).to_have_count(1)
            expect(history_entries(page).first).to_contain_text("QA Engineer")

            history_filter(page, "All Actions").select_option("deleted")
            settle(page)
            expect(main_content(page).get_by_text("No logs found")).to_be_visible()
        finally:
            delete_candidates(page, data["name"])

        browser.close()
