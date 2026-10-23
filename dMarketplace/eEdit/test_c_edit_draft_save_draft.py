from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, goto, unique_name, create_app, delete_apps, main_content, fill_form, save_draft, expect_toast,
    status_badge, open_review, review_card, show_url, app_data, MARKETPLACE_URL, LIVE_WARNING,
)


def test_edit_draft_save_draft():
    """MP-040: editing a draft and choosing Save draft keeps the changes and leaves it a draft,
    out of the review queue."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            app_id = create_app(page, name, submit=False)
            goto(page, f"{MARKETPLACE_URL}/{app_id}/edit")
            expect(main_content(page).get_by_text(LIVE_WARNING)).to_have_count(0)

            fill_form(page, short="Edited draft summary.", category="Integrations")
            save_draft(page)
            expect_toast(page, "Website updated successfully.")
            page.wait_for_url(show_url(name))
            expect(status_badge(page, "draft")).to_be_visible()
            expect(main_content(page).get_by_text("Edited draft summary.")).to_be_visible()
            data = app_data(page, name)
            assert (data["status"], data["category"]) == ("draft", "Integrations"), data

            open_review(page)
            expect(review_card(page, name)).to_have_count(0)
        finally:
            delete_apps(page, name)

        browser.close()
