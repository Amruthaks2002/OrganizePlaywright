from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, open_settings, settings_toggle, form_type_select, expect_toggle_on,
)


def test_settings_panel():
    """CF-016: Settings shows form type, response editing and the stop-accepting options."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        panel = open_settings(page)

        expect(form_type_select(panel).locator("option")).to_have_text(["General", "Probation Review"])
        expect(form_type_select(panel)).to_have_value("general")
        expect(panel.get_by_text("Stop accepting responses")).to_be_visible()
        for label in ["Allow response editing", "On a date", "After number of responses"]:
            expect_toggle_on(settings_toggle(panel, label), False)
        expect(panel.locator("input[type=date], input[type=time], input[type=number]")).to_have_count(0)

        settings_toggle(panel, "Allow response editing").click()
        expect_toggle_on(settings_toggle(panel, "Allow response editing"))

        settings_toggle(panel, "On a date").click()
        expect_toggle_on(settings_toggle(panel, "On a date"))
        expect(panel.locator("input[type=date]")).to_be_visible()
        expect(panel.locator("input[type=time]")).to_be_visible()

        settings_toggle(panel, "After number of responses").click()
        expect_toggle_on(settings_toggle(panel, "After number of responses"))
        expect(panel.get_by_placeholder("Max responses")).to_have_value("40")

        browser.close()
