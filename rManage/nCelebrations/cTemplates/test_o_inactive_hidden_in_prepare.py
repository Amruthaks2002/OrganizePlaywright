from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, create_template, unique_template_name, delete_templates, toggle_template, open_prepare,
    open_templates, template_option, ANNIVERSARY_TEMPLATES_URL,
)


def test_inactive_hidden_in_prepare():
    """CT-015: an inactive template isn't offered in Prepare Celebration until it's activated again."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_template_name()
        try:
            create_template(page, name, "work_anniversary")
            toggle_template(page, name, "Deactivate")
            open_prepare(page)
            expect(template_option(page, "1st Work Anniversary")).to_be_visible()
            expect(template_option(page, name)).to_have_count(0)

            open_templates(page, ANNIVERSARY_TEMPLATES_URL)
            toggle_template(page, name, "Activate")
            open_prepare(page)
            expect(template_option(page, name)).to_be_visible()
        finally:
            delete_templates(page, name)

        browser.close()
