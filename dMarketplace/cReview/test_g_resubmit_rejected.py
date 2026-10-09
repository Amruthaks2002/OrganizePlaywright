from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, reject_app, delete_apps, open_app, main_content, fill_form,
    submit_for_review, expect_toast, status_badge, history, open_review, review_card, show_url,
)


def test_resubmit_rejected():
    """MP-027: the author can edit a rejected app and submit it again, which puts it back in the
    review queue as pending."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            reject_app(page, create_app(page, name), reason="Needs a better summary.")
            open_app(page, name)
            main_content(page).get_by_role("link", name="Edit", exact=True).click()
            page.wait_for_url("**/edit")
            fill_form(page, short="A much better summary.")
            submit_for_review(page)
            expect_toast(page, "updated successfully")
            page.wait_for_url(show_url(name))

            expect(status_badge(page, "submitted")).to_be_visible()
            expect(main_content(page).get_by_text("This submission was rejected.")).to_have_count(0)
            expect(main_content(page).get_by_text("A much better summary.")).to_be_visible()
            assert history(page) == ["Submitted by Admin User", "Rejected by Admin User", "Submitted by Admin User"], \
                history(page)
            open_review(page)
            expect(review_card(page, name)).to_contain_text("A much better summary.")
        finally:
            delete_apps(page, name)

        browser.close()
