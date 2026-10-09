from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, goto, unique_name, create_live_app, delete_apps, fill_form, submit_for_review, field_error,
    app_data, MARKETPLACE_URL,
)


def test_edit_validation():
    """MP-041: clearing required fields on the edit form is refused and the live app is unchanged."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            app_id = create_live_app(page, name)
            edit_url = f"{MARKETPLACE_URL}/{app_id}/edit"
            goto(page, edit_url)
            fill_form(page, name="", short="", url="")
            submit_for_review(page)
            for message in ["The name field is required.", "The short description field is required.",
                            "A link is required for this delivery method."]:
                expect(field_error(page, message)).to_be_visible()
            assert page.url == edit_url, page.url

            data = app_data(page, name)
            assert (data["name"], data["status"]) == (name, "approved"), data
        finally:
            delete_apps(page, name)

        browser.close()
