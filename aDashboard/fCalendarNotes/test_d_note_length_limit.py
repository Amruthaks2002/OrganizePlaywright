from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_dashboard, open_day, open_note, cleanup_notes, expect_toast,
                                    note_text, note_day)
import re


def test_note_length_limit():
    """DB-041: a note is limited to 1000 characters - typing 1001 keeps 1000, and those 1000 are saved."""
    day = note_day()
    prefix = note_text("long")
    text = (prefix + " " + "x" * 1001)[:1001]
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            dialog = open_day(page, day)
            box = dialog.locator("#note")
            expect(box).to_have_attribute("maxlength", "1000")
            box.press_sequentially(text[:990])
            box.press_sequentially(text[990:])
            assert len(box.input_value()) == 1000
            dialog.get_by_role("button", name="Save").click()
            expect_toast(page, re.compile("note added successfully", re.I))

            open_dashboard(page)
            dialog = open_note(page, day, prefix)
            assert dialog.locator("#note").input_value() == text[:1000]
            dialog.get_by_role("button", name="Cancel").click()
        finally:
            cleanup_notes(page, day, prefix)
            browser.close()
