from playwright.sync_api import sync_playwright, expect
from utils.asset_helper import (
    open_browser, open_browser_as, unique_prefix, create_assets, delete_assets, bulk_check_out, open_assets,
    main_content, dock,
)


def test_employee_no_bulk_select():
    """BS-029: an employee only sees their own assets, with no row checkboxes, no Select all and no
    dock - even when they hold assets."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        prefix = unique_prefix()
        try:
            names = create_assets(page, prefix)
            bulk_check_out(page, prefix, 2)  # to Ajith PT, the employee quick-login user

            emp_browser, emp_page = open_browser_as(p, "employee")
            open_assets(emp_page)
            main = main_content(emp_page)
            expect(main.get_by_text("Hardware currently assigned to you.")).to_be_visible()
            for name in names:
                expect(main.get_by_text(name)).to_be_visible()
            expect(main.locator("input[type=checkbox]")).to_have_count(0)
            expect(main.get_by_label("Select all assets on this page")).to_have_count(0)
            expect(dock(emp_page)).to_have_count(0)
            emp_browser.close()
        finally:
            delete_assets(page, prefix)

        browser.close()
