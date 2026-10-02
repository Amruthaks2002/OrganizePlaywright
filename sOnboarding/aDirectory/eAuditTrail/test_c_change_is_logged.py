import re
from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_review, save_field_value, wait_for_history,
    history_entries, delete_candidates,
)


def test_change_is_logged():
    """AT-003: creating a candidate and editing a value both show up in the audit trail,
    with who did it and the previous / new values."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        data = new_candidate_data()
        try:
            candidate_id = create_candidate(page, **data)
            open_review(page, candidate_id)
            save_field_value(page, "Designation", "QA Engineer")

            wait_for_history(page, candidate_id, 2)
            entries = history_entries(page)

            update = entries.filter(has_text="QA Engineer")
            expect(update).to_have_count(1)
            expect(update.get_by_role("row").filter(has=page.get_by_role("cell", name="Designation", exact=True))).to_contain_text(
                "QA Engineer")
            created = entries.filter(has_text=data["email"])
            expect(created.get_by_role("row").filter(has=page.get_by_role("cell", name="Full Name", exact=True))).to_contain_text(
                data["name"])
            for text in ["Admin User", "updated", "created"]:
                expect(page.get_by_test_id("main-content").get_by_text(
                    re.compile(rf"^\s*{text}\s*$", re.I)).filter(visible=True).first).to_be_visible()
        finally:
            delete_candidates(page, data["name"])

        browser.close()
