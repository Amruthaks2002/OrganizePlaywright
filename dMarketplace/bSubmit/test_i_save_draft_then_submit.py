from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, open_create, pick_platform, fill_form, save_draft, expect_toast, delete_apps,
    main_content, show_url, status_badge, open_review, review_card, history, open_app, DRAFT_SAVED,
)


def test_save_draft_then_submit():
    """MP-018: Save draft keeps the app out of the review queue; 'Submit for review' on its detail
    page then sends it there."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            open_create(page)
            pick_platform(page, "idea")
            fill_form(page, name=name, short="Draft first.")
            save_draft(page)
            expect_toast(page, DRAFT_SAVED)
            page.wait_for_url(show_url(name))
            expect(status_badge(page, "draft")).to_be_visible()
            assert history(page) == [], history(page)

            open_review(page)
            expect(review_card(page, name)).to_have_count(0)

            open_app(page, name)
            main_content(page).get_by_role("button", name="Submit for review").click()
            expect_toast(page, "Idea submitted for review.")
            expect(status_badge(page, "submitted")).to_be_visible()
            expect(main_content(page).get_by_role("button", name="Submit for review")).to_have_count(0)
            assert history(page) == ["Submitted by Admin User"], history(page)

            open_review(page)
            expect(review_card(page, name)).to_be_visible()
        finally:
            delete_apps(page, name)

        browser.close()
