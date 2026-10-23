from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_create_form, open_settings, form_type_select, anonymous_button


def test_probation_hides_anonymous():
    """CF-018: switching the form type to Probation Review hides the Anonymous button."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        expect(anonymous_button(page)).to_be_visible()

        panel = open_settings(page)
        form_type_select(panel).select_option("probation_review")
        panel.get_by_role("button", name="✕").click()
        expect(anonymous_button(page)).to_be_hidden()

        panel = open_settings(page)
        form_type_select(panel).select_option("general")
        panel.get_by_role("button", name="✕").click()
        expect(anonymous_button(page)).to_be_visible()

        browser.close()
