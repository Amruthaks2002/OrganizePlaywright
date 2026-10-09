from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, submit_new_app, delete_apps, main_content, status_badge, app_data,
)


def test_idea_submission():
    """MP-019: an idea is submitted with no file or link; its page invites kudos and offers no
    Open or Download link."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            submit_new_app(page, name, platform="idea", short="Just an idea.")
            main = main_content(page)
            expect(status_badge(page, "submitted")).to_be_visible()
            expect(main.get_by_text("This is a concept — show your support with kudos.")).to_be_visible()
            expect(main.get_by_role("link", name="Open", exact=True)).to_have_count(0)
            expect(main.get_by_role("link", name="Download", exact=True)).to_have_count(0)
            data = app_data(page, name)
            assert (data["platform"], data["delivery_type"], data["external_url"]) == ("idea", "none", None), data
        finally:
            delete_apps(page, name)

        browser.close()
