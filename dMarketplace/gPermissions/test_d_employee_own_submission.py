from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, open_browser_as, unique_name, submit_new_app, delete_apps, api, app_data, open_app, main_content,
    status_badge, fill_form, submit_for_review, expect_toast, search_app_names, open_review, review_card,
    remove_app_ui, show_url,
)


def test_employee_own_submission():
    """MP-048: an employee's submission waits in the admin queue, is visible to them under My
    submissions but not to colleagues (403), can't be approved by its author, and can be edited
    and removed by them."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            emp_browser, emp_page = open_browser_as(p, "employee")
            submit_new_app(emp_page, name, short="Employee submission.")
            expect(status_badge(emp_page, "submitted")).to_be_visible()
            expect(main_content(emp_page).get_by_role("link", name="Edit", exact=True)).to_be_visible()
            app_id = app_data(emp_page, name)["id"]
            assert search_app_names(emp_page, name, mine=True) == [name]
            assert search_app_names(emp_page, name) == []

            status, _ = api(emp_page, "POST", f"/marketplace/{app_id}/approve")
            assert status == 403, f"author approving own app: expected 403, got {status}"

            tl_browser, tl_page = open_browser_as(p, "team-lead")
            assert tl_page.goto(show_url(name)).status == 403
            tl_browser.close()

            open_review(page)
            expect(review_card(page, name)).to_contain_text("by Ajith PT", ignore_case=True)

            open_app(emp_page, name)
            main_content(emp_page).get_by_role("link", name="Edit", exact=True).click()
            emp_page.wait_for_url("**/edit")
            fill_form(emp_page, short="Employee edited summary.")
            submit_for_review(emp_page)
            expect_toast(emp_page, "updated successfully")
            assert app_data(page, name)["short_description"] == "Employee edited summary."

            remove_app_ui(emp_page, name)
            assert app_data(page, name) is None
            emp_browser.close()
        finally:
            delete_apps(page, name)

        browser.close()
