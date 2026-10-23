from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_templates, open_add_template, fill_template_form, template_card, unique_template_name,
    make_text_file, expect_toast, delete_templates,
)


def test_non_image_rejected():
    """CT-009: a template whose background isn't an image is rejected."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_templates(page)
        name = unique_template_name()
        try:
            dialog = open_add_template(page)
            fill_template_form(dialog, name, make_text_file())
            dialog.get_by_role("button", name="Create Template").click()
            expect_toast(page, "Template must be an image file.")

            open_templates(page)
            expect(template_card(page, name)).to_have_count(0)
        finally:
            delete_templates(page, name)

        browser.close()
