import re

from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, open_app, comment_box, post_comment_button, comment,
    comments, expect_toast, main_content,
)

EMPTY = "No comments yet — be the first to share feedback."


def test_post_comment():
    """MP-032: 'Post comment' stays disabled until there's real text; posting shows the comment
    with its author, clears the box and updates the count."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        text = "QA comment: works well for our team."
        try:
            create_live_app(page, name)
            open_app(page, name)
            main = main_content(page)
            expect(main.get_by_text(EMPTY)).to_be_visible()
            expect(post_comment_button(page)).to_be_disabled()
            comment_box(page).fill("   ")
            expect(post_comment_button(page)).to_be_disabled()

            comment_box(page).fill(text)
            expect(post_comment_button(page)).to_be_enabled()
            post_comment_button(page).click()
            expect_toast(page, "Comment posted.")
            expect(comment(page, text)).to_contain_text("Admin User")
            expect(comment_box(page)).to_have_value("")
            expect(main.get_by_text(EMPTY)).to_have_count(0)
            expect(comments(page)).to_have_count(1)
            heading = main.get_by_role("heading", name=re.compile(r"^\s*Comments"))
            expect(heading).to_have_text(re.compile(r"Comments\s*1$"))

            open_app(page, name)
            expect(comment(page, text)).to_be_visible()
        finally:
            delete_apps(page, name)

        browser.close()
