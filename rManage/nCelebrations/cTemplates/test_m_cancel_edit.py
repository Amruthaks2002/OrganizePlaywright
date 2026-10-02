import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, create_template, template_card, unique_template_name, delete_templates, main_content,
    edit_template_url, goto, open_templates,
)


def test_cancel_edit():
    """CT-013: Cancel and Back to Templates leave the edit page without saving."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_template_name()
        try:
            create_template(page, name)
            url = edit_template_url(page, name)

            for leave in ["Cancel", "Back to Templates"]:
                goto(page, url)
                main = main_content(page)
                main.locator("input[type=text]").fill(f"{name} not saved")
                main.get_by_role("button", name=leave).or_(main.get_by_role("link", name=leave)).first.click()
                expect(page).to_have_url(re.compile(r"/celebration-templates(\?.*)?$"))

                open_templates(page)
                expect(template_card(page, name)).to_be_visible()
                expect(template_card(page, f"{name} not saved")).to_have_count(0)
        finally:
            delete_templates(page, name)

        browser.close()
