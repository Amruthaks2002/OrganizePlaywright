from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, create_live_app, delete_apps, open_app, comment_box, api, comments,
)


def test_comment_length_limit():
    """MP-035: comments are capped at 2000 characters: the box stops at 2000 and the server
    refuses anything longer."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            app_id = create_live_app(page, name)
            open_app(page, name)
            expect(comment_box(page)).to_have_attribute("maxlength", "2000")
            comment_box(page).fill("y" * 2001)
            assert len(comment_box(page).input_value()) <= 2000

            status, body = api(page, "POST", f"/marketplace/{app_id}/comments", {"body": "z" * 2001})
            assert status == 422, f"expected 422, got {status} {body}"
            assert body["errors"]["body"] == ["The body field must not be greater than 2000 characters."], body
            status, body = api(page, "POST", f"/marketplace/{app_id}/comments", {"body": ""})
            assert status == 422, f"expected 422, got {status} {body}"
            assert body["errors"]["body"] == ["The body field is required."], body

            open_app(page, name)
            expect(comments(page)).to_have_count(0)
        finally:
            delete_apps(page, name)

        browser.close()
