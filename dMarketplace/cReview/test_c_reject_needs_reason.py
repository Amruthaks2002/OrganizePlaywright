from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, delete_apps, open_review, review_card, open_reject, app_data,
    REASON_REQUIRED,
)


def test_reject_needs_reason():
    """MP-023: rejecting without a reason is refused in the dialog and the app stays pending."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            create_app(page, name)
            open_review(page)
            dialog = open_reject(page, review_card(page, name))
            expect(dialog).to_contain_text(f'Reject "{name}"')
            expect(dialog).to_contain_text("The reason is shown to the author so they can fix and resubmit.")

            dialog.get_by_role("button", name="Reject submission").click()
            expect(dialog.get_by_text(REASON_REQUIRED)).to_be_visible()
            expect(dialog).to_be_visible()
            assert app_data(page, name)["status"] == "submitted"
        finally:
            delete_apps(page, name)

        browser.close()
