import uuid
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, open_prepare, message_box, save_message, ORIGINAL_MESSAGE


def test_save_message():
    """PC-009: Save Message stores the custom message (the original message is put back afterwards)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_prepare(page)
        original = message_box(page).input_value() or ORIGINAL_MESSAGE
        text = f"QA message {uuid.uuid4().hex[:8]}"
        try:
            save_message(page, text)
            open_prepare(page)
            expect(message_box(page)).to_have_value(text)
        finally:
            open_prepare(page)
            save_message(page, original)
            open_prepare(page)
            expect(message_box(page)).to_have_value(original)

        browser.close()
