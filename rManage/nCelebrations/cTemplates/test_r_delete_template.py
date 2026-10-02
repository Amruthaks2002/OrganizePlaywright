from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, create_template, template_card, unique_template_name, delete_templates, delete_dialog,
    open_templates, expect_toast,
)


def test_delete_template():
    """CT-018: confirming Delete removes the template."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_template_name()
        try:
            create_template(page, name)
            template_card(page, name).get_by_role("button", name="Delete").click()
            delete_dialog(page).get_by_role("button", name="Delete", exact=True).click()
            expect_toast(page, "Template deleted successfully!")
            expect(template_card(page, name)).to_have_count(0)

            open_templates(page)
            expect(template_card(page, name)).to_have_count(0)
        finally:
            delete_templates(page, name)

        browser.close()
