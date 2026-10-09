from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, delete_apps, open_review, review_card, expect_toast, open_marketplace,
    app_card, open_app, status_badge, history,
)


def test_approve_from_queue():
    """MP-022: approving a submission publishes it: it leaves the queue, is listed in the
    marketplace as Approved and its history records who approved it."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            create_app(page, name)
            open_marketplace(page, search=name)
            expect(app_card(page, name)).to_have_count(0)

            open_review(page)
            review_card(page, name).get_by_role("button", name="Approve", exact=True).click()
            expect_toast(page, "is now live in the marketplace")
            expect(review_card(page, name)).to_have_count(0)

            open_marketplace(page, search=name)
            expect(app_card(page, name)).to_contain_text("Approved")
            open_app(page, name)
            expect(status_badge(page, "approved")).to_be_visible()
            assert history(page) == ["Approved by Admin User", "Submitted by Admin User"], history(page)
        finally:
            delete_apps(page, name)

        browser.close()
