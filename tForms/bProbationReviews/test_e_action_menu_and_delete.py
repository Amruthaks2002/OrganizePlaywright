from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_probation_reviews, unique_form_title, create_form_api, delete_forms, search_forms,
    form_row, delete_dialog, expect_toast,
)


def test_action_menu_and_delete():
    """PR-005: the ⋮ menu offers Copy Link, Clone, Edit, Delete, and Delete removes the form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_probation_reviews(page)
        title = unique_form_title()
        try:
            create_form_api(page, title, type="probation_review")
            search_forms(page, title)
            row = form_row(page, title)

            row.get_by_role("button", name="⋮").click()
            menu = row.locator(".action-menu").get_by_role("button").filter(has_not_text="⋮")
            expect(menu).to_have_text(["Copy Link", "Clone", "Edit", "Delete"], use_inner_text=True)

            menu.filter(has_text="Delete").click()
            delete_dialog(page).get_by_role("button", name="Delete", exact=True).click()
            expect(delete_dialog(page)).to_be_hidden()
            expect_toast(page, "Form deleted successfully.")

            search_forms(page, title)
            expect(form_row(page, title)).to_have_count(0)
        finally:
            delete_forms(page, title)

        browser.close()
