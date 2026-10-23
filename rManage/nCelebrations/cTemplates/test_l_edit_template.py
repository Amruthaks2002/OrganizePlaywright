from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, create_template, template_card, unique_template_name, delete_templates, main_content,
    edit_template_url, goto, expect_toast,
)


def test_edit_template():
    """CT-012: Update Template saves the new name and description."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_template_name()
        new_name = f"{name} edited"
        try:
            create_template(page, name, "birthday", "old description")
            goto(page, edit_template_url(page, name))
            main = main_content(page)

            main.locator("input[type=text]").fill(new_name)
            main.locator("textarea").fill("new description")
            main.get_by_role("button", name="Update Template").click()
            expect_toast(page, "Template updated successfully!")

            card = template_card(page, new_name)
            expect(card).to_be_visible()
            expect(card.get_by_text("new description")).to_be_visible()
            expect(template_card(page, name)).to_have_count(0)
        finally:
            delete_templates(page, name)

        browser.close()
