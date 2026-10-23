import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, create_template, template_card, unique_template_name, delete_templates, main_content, settle,
)


def test_edit_page_prefilled():
    """CT-011: Edit opens the template's edit page filled in with its current values."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_template_name()
        try:
            create_template(page, name, "birthday", "QA prefilled description")
            template_card(page, name).get_by_role("link", name="Edit").click()
            expect(page).to_have_url(re.compile(r"/celebration-templates/\d+/edit$"))
            settle(page)
            main = main_content(page)

            expect(main.get_by_role("heading", name=re.compile("Edit Template"))).to_be_visible()
            expect(main.get_by_text("Update birthday template")).to_be_visible()
            expect(main.locator("input[type=text]")).to_have_value(name)
            expect(main.locator("textarea")).to_have_value("QA prefilled description")
            expect(main.get_by_text("Current Background Template")).to_be_visible()
            expect(main.locator("img[src*='/storage/templates/birthday/']")).to_be_visible()
            expect(main.get_by_text("Replace Background Template (Optional)")).to_be_visible()
            expect(page.locator("#is_active")).to_be_checked()
        finally:
            delete_templates(page, name)

        browser.close()
