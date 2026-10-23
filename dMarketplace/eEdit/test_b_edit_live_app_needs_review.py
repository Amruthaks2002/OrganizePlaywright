from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, goto, unique_name, create_live_app, delete_apps, main_content, fill_form, submit_for_review,
    expect_toast, status_badge, search_app_names, open_review, review_card, show_url, MARKETPLACE_URL,
    LIVE_WARNING,
)


def test_edit_live_app_needs_review():
    """MP-039: editing a live app warns that it goes back to review; saving hides it from the
    marketplace and puts it in the queue with the new details."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            app_id = create_live_app(page, name)
            goto(page, f"{MARKETPLACE_URL}/{app_id}/edit")
            main = main_content(page)
            expect(main.get_by_text(LIVE_WARNING)).to_be_visible()
            expect(main.get_by_text("Saving changes will take it back to the review queue", exact=False)).to_be_visible()

            fill_form(page, short="Edited live summary.", version="1.0.1")
            submit_for_review(page)
            expect_toast(page, "Website updated successfully.")
            page.wait_for_url(show_url(name))
            expect(status_badge(page, "submitted")).to_be_visible()
            expect(main.get_by_text("Edited live summary.")).to_be_visible()

            assert search_app_names(page, name) == [], "an app back in review must not be listed publicly"
            open_review(page)
            expect(review_card(page, name)).to_contain_text("Edited live summary.")
        finally:
            delete_apps(page, name)

        browser.close()
