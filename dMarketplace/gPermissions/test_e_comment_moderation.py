from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, open_browser_as, unique_name, create_live_app, post_comment, delete_apps, api, app_data, open_app,
    comment, delete_comment_button, answer_next_dialog, expect_toast,
)


def test_comment_moderation():
    """MP-049: people can delete only their own comments (others' have no delete button and the
    call is refused with 403), while an admin can delete anyone's."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        admin_text, emp_text = "QA admin comment.", "QA employee comment."
        try:
            app_id = create_live_app(page, name)
            post_comment(page, app_id, admin_text)
            emp_browser, emp_page = open_browser_as(p, "employee")
            post_comment(emp_page, app_id, emp_text)
            ids = {c["body"]: c["id"] for c in app_data(page, name)["comments"]}

            open_app(emp_page, name)
            expect(delete_comment_button(emp_page, emp_text)).to_have_count(1)
            expect(delete_comment_button(emp_page, admin_text)).to_have_count(0)
            status, _ = api(emp_page, "DELETE", f"/marketplace/comments/{ids[admin_text]}")
            assert status == 403, f"employee deleting admin's comment: expected 403, got {status}"
            emp_browser.close()

            tl_browser, tl_page = open_browser_as(p, "team-lead")
            status, _ = api(tl_page, "DELETE", f"/marketplace/comments/{ids[emp_text]}")
            assert status == 403, f"team-lead deleting employee's comment: expected 403, got {status}"
            tl_browser.close()

            open_app(page, name)
            expect(comment(page, admin_text)).to_be_visible()
            answer_next_dialog(page)
            delete_comment_button(page, emp_text).click()
            expect_toast(page, "Comment removed.")
            expect(comment(page, emp_text)).to_have_count(0)
            assert [c["body"] for c in app_data(page, name)["comments"]] == [admin_text]
        finally:
            delete_apps(page, name)

        browser.close()
