from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, create_template, template_card, unique_template_name, delete_templates, delete_dialog,
    open_templates,
)


def test_cancel_delete():
    """CT-017: Delete asks for confirmation, and Cancel keeps the template."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_template_name()
        try:
            create_template(page, name)
            template_card(page, name).get_by_role("button", name="Delete").click()
            dialog = delete_dialog(page)
            expect(dialog).to_be_visible()
            expect(dialog.get_by_text("Are you sure you want to delete this template? This action cannot be undone.")).to_be_visible()

            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()
            open_templates(page)
            expect(template_card(page, name)).to_be_visible()
        finally:
            delete_templates(page, name)

        browser.close()
