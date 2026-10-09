from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, post_comment, delete_apps, open_app, comment,
    delete_comment_button, answer_next_dialog,
)


def test_cancel_comment_delete():
    """MP-034: dismissing the 'Delete this comment?' confirmation keeps the comment."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        text = "QA comment to keep."
        try:
            app_id = create_live_app(page, name)
            post_comment(page, app_id, text)
            open_app(page, name)

            messages = answer_next_dialog(page, accept=False)
            delete_comment_button(page, text).click()
            page.wait_for_timeout(1000)
            assert messages == ["Delete this comment?"], messages
            expect(comment(page, text)).to_be_visible()

            open_app(page, name)
            expect(comment(page, text)).to_be_visible()
        finally:
            delete_apps(page, name)

        browser.close()
