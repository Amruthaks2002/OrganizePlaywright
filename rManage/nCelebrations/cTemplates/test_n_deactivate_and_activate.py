from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, create_template, template_card, unique_template_name, delete_templates, toggle_template,
)


def test_deactivate_and_activate():
    """CT-014: Deactivate marks a template INACTIVE; Activate makes it active again."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_template_name()
        try:
            create_template(page, name)
            card = template_card(page, name)
            expect(card.get_by_text("INACTIVE", exact=True)).to_have_count(0)

            toggle_template(page, name, "Deactivate")
            expect(card.get_by_text("INACTIVE", exact=True)).to_be_visible()
            expect(card.get_by_role("button", name="Activate", exact=True)).to_be_visible()

            toggle_template(page, name, "Activate")
            expect(card.get_by_text("INACTIVE", exact=True)).to_have_count(0)
            expect(card.get_by_role("button", name="Deactivate", exact=True)).to_be_visible()
        finally:
            delete_templates(page, name)

        browser.close()
