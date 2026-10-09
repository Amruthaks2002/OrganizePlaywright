from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_app, delete_apps, open_app, kudos_button, comment_box, main_content,
)


def test_no_kudos_or_comments_before_live():
    """MP-031: drafts and pending apps can't receive kudos or comments yet."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_name()
        draft, pending = f"{prefix} Draft", f"{prefix} Pending"
        try:
            create_app(page, draft, submit=False)
            create_app(page, pending)
            for name in [draft, pending]:
                open_app(page, name)
                expect(kudos_button(page)).to_have_count(0)
                expect(comment_box(page)).to_have_count(0)
                expect(main_content(page).get_by_role("button", name="Post comment")).to_have_count(0)
        finally:
            delete_apps(page, draft, pending)

        browser.close()
