from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, delete_apps, open_review, review_card, open_reject, expect_toast,
    open_app, status_badge, history, main_content, search_app_names, REJECT_PLACEHOLDER,
)


def test_reject_with_reason():
    """MP-024: rejecting with a reason takes the app out of the queue, keeps it off the public
    list, and shows the reason on its page and in its history."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        reason = "Please add screenshots before resubmitting."
        try:
            create_app(page, name)
            open_review(page)
            dialog = open_reject(page, review_card(page, name))
            dialog.get_by_placeholder(REJECT_PLACEHOLDER).fill(reason)
            dialog.get_by_role("button", name="Reject submission").click()
            expect_toast(page, "was rejected and the author notified")
            expect(dialog).to_be_hidden()
            expect(review_card(page, name)).to_have_count(0)

            open_app(page, name)
            main = main_content(page)
            expect(status_badge(page, "rejected")).to_be_visible()
            expect(main.get_by_text("This submission was rejected.")).to_be_visible()
            expect(main.get_by_text(f"Reason: {reason}")).to_be_visible()
            expect(main.get_by_text("Edit the Website and resubmit when it's ready.")).to_be_visible()
            assert history(page)[0] == "Rejected by Admin User", history(page)
            expect(main.get_by_text(reason, exact=True)).to_be_visible()

            assert search_app_names(page, name) == [], "a rejected app must not be listed publicly"
        finally:
            delete_apps(page, name)

        browser.close()
