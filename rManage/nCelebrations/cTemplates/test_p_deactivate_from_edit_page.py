from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, create_template, template_card, unique_template_name, delete_templates, main_content,
    edit_template_url, goto, expect_toast,
)


def test_deactivate_from_edit_page():
    """CT-016: unticking 'Template is active' on the edit page deactivates the template."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_template_name()
        try:
            create_template(page, name)
            url = edit_template_url(page, name)
            goto(page, url)

            page.locator("#is_active").uncheck()
            main_content(page).get_by_role("button", name="Update Template").click()
            expect_toast(page, "Template updated successfully!")
            card = template_card(page, name)
            expect(card.get_by_text("INACTIVE", exact=True)).to_be_visible()
            expect(card.get_by_role("button", name="Activate", exact=True)).to_be_visible()

            goto(page, url)
            expect(page.locator("#is_active")).not_to_be_checked()
        finally:
            delete_templates(page, name)

        browser.close()
