from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, post_comment, delete_apps, open_app, comment, comments,
    delete_comment_button, answer_next_dialog, expect_toast, main_content,
)


def test_delete_own_comment():
    """MP-033: deleting your comment asks for confirmation, then removes it."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        text = "QA comment to delete."
        try:
            app_id = create_live_app(page, name)
            post_comment(page, app_id, text)
            open_app(page, name)

            messages = answer_next_dialog(page, accept=True)
            delete_comment_button(page, text).click()
            expect_toast(page, "Comment removed.")
            assert messages == ["Delete this comment?"], messages
            expect(comment(page, text)).to_have_count(0)
            expect(comments(page)).to_have_count(0)
            expect(main_content(page).get_by_text("No comments yet — be the first to share feedback.")).to_be_visible()

            open_app(page, name)
            expect(comment(page, text)).to_have_count(0)
        finally:
            delete_apps(page, name)

        browser.close()
