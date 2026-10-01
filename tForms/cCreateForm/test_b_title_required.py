from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_create_form, save_button, expect_toast, title_input


def test_title_required():
    """CF-002: saving without a title shows "The title field is required." and saves nothing."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)

        save_button(page).click()
        expect_toast(page, "The title field is required.")
        expect(title_input(page).locator("xpath=..").get_by_text("The title field is required.")).to_be_visible()
        expect(page.get_by_role("heading", name="Form Created Successfully")).to_have_count(0)
        expect(title_input(page)).to_be_visible()

        browser.close()
