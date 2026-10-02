from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_templates, open_add_template, fill_template_form, template_card, unique_template_name,
    delete_templates,
)


def test_required_fields():
    """CT-006: the Add Template dialog won't submit without a name and a background image."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_templates(page)
        name = unique_template_name()
        try:
            dialog = open_add_template(page)
            name_input = dialog.locator("input[type=text]")
            file_input = dialog.locator("input[type=file]")

            dialog.get_by_role("button", name="Create Template").click()
            expect(dialog).to_be_visible()
            assert name_input.evaluate("e => e.validity.valueMissing"), "an empty name should be blocked"

            fill_template_form(dialog, name)
            dialog.get_by_role("button", name="Create Template").click()
            expect(dialog).to_be_visible()
            assert file_input.evaluate("e => e.validity.valueMissing"), "a missing image should be blocked"

            open_templates(page)
            expect(template_card(page, name)).to_have_count(0)
        finally:
            delete_templates(page, name)

        browser.close()
