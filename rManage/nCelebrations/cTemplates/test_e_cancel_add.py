from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_templates, open_add_template, fill_template_form, template_card, unique_template_name,
    make_png, delete_templates,
)


def test_cancel_add():
    """CT-005: Cancel closes the Add Template dialog without creating the template."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_templates(page)
        name = unique_template_name()
        try:
            dialog = open_add_template(page)
            fill_template_form(dialog, name, make_png("cancel.png"), "should not be saved")
            dialog.get_by_role("button", name="Cancel").click()
            expect(dialog).to_be_hidden()

            open_templates(page)
            expect(template_card(page, name)).to_have_count(0)
        finally:
            delete_templates(page, name)

        browser.close()
