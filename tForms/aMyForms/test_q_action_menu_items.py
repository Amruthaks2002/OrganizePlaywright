from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, form_row,
)


def test_action_menu_items():
    """FM-017: the ⋮ menu offers Copy Link, Clone, Edit and Delete."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        title = unique_form_title()
        try:
            create_form_api(page, title)
            search_forms(page, title)
            row = form_row(page, title)

            row.get_by_role("button", name="⋮").click()
            expect(row.locator(".action-menu").get_by_role("button").filter(has_not_text="⋮")).to_have_text(
                ["Copy Link", "Clone", "Edit", "Delete"], use_inner_text=True)
        finally:
            delete_forms(page, title)

        browser.close()
