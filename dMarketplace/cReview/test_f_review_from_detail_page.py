from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, delete_apps, open_app, main_content, expect_toast, status_badge,
    open_reject, app_data, REJECT_PLACEHOLDER,
)


def test_review_from_detail_page():
    """MP-026: a pending app's own page has an 'Awaiting your review' panel with working Approve
    and Reject buttons."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        approve, reject = f"{prefix} Approve", f"{prefix} Reject"
        try:
            create_app(page, approve)
            create_app(page, reject)

            open_app(page, approve)
            main = main_content(page)
            expect(main.get_by_text("Awaiting your review", exact=False)).to_be_visible()
            main.get_by_role("button", name="Approve", exact=True).click()
            expect_toast(page, "is now live in the marketplace")
            expect(status_badge(page, "approved")).to_be_visible()
            expect(main.get_by_role("button", name="Approve", exact=True)).to_have_count(0)

            open_app(page, reject)
            dialog = open_reject(page, main)
            dialog.get_by_placeholder(REJECT_PLACEHOLDER).fill("Rejected from the detail page.")
            dialog.get_by_role("button", name="Reject submission").click()
            expect_toast(page, "was rejected and the author notified")
            assert app_data(page, reject)["status"] == "rejected"
        finally:
            delete_apps(page, approve, reject)

        browser.close()
