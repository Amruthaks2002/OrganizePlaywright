from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import open_browser, open_directory, open_add_candidate


def test_phone_max_ten_digits():
    """OD-030: the phone field stops at 10 digits."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_directory(page)
        dialog = open_add_candidate(page)

        phone = dialog.get_by_placeholder("10-digit number")
        phone.press_sequentially("98765432101234")
        expect(phone).to_have_value("9876543210")

        browser.close()
