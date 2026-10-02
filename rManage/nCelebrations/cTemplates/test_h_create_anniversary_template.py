from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_templates, create_template, template_card, unique_template_name, delete_templates,
    open_prepare, template_option,
)


def test_create_anniversary_template():
    """CT-008: a work anniversary template shows on the Anniversary tab only and is offered in Prepare Celebration."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_template_name()
        try:
            create_template(page, name, "work_anniversary")

            open_templates(page)
            expect(template_card(page, name)).to_have_count(0)

            open_prepare(page)
            expect(template_option(page, name)).to_be_visible()
        finally:
            delete_templates(page, name)

        browser.close()
