from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_templates, create_template, template_card, unique_template_name, delete_templates,
    ANNIVERSARY_TEMPLATES_URL,
)


def test_create_birthday_template():
    """CT-007: a birthday template is created and shown on the Birthday tab only."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_template_name()
        try:
            create_template(page, name, "birthday", "QA birthday description")
            card = template_card(page, name)
            expect(card.get_by_text("QA birthday description")).to_be_visible()
            expect(card.get_by_role("img", name=name)).to_be_visible()
            expect(card.get_by_role("button", name="Deactivate")).to_be_visible()

            open_templates(page, ANNIVERSARY_TEMPLATES_URL)
            expect(template_card(page, name)).to_have_count(0)
        finally:
            delete_templates(page, name)

        browser.close()
