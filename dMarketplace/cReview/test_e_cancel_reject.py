from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, delete_apps, open_review, review_card, open_reject, app_data,
    reject_dialog, REJECT_PLACEHOLDER,
)


def test_cancel_reject():
    """MP-025: cancelling the reject dialog closes it and leaves the app pending in the queue."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            create_app(page, name)
            open_review(page)
            dialog = open_reject(page, review_card(page, name))
            dialog.get_by_placeholder(REJECT_PLACEHOLDER).fill("Changed my mind.")
            dialog.get_by_role("button", name="Cancel").click()
            expect(reject_dialog(page)).to_have_count(0)
            expect(review_card(page, name)).to_be_visible()
            assert app_data(page, name)["status"] == "submitted"
        finally:
            delete_apps(page, name)

        browser.close()
