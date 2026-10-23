from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, login_as, add_note, go_to_month, note_event, cleanup_notes,
                                    main_content, note_text, note_day)


def test_notes_are_private():
    """DB-044: a note the admin adds is not shown on the employee's calendar."""
    day = note_day()
    text = note_text("private")
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        try:
            add_note(page, day, text)

            employee = browser.new_context(viewport={"width": 1600, "height": 900}).new_page()
            login_as(employee, "employee")
            go_to_month(employee, day)
            expect(main_content(employee).get_by_text("Calendar", exact=True)).to_be_visible()
            expect(note_event(employee, day, text)).to_have_count(0)
            expect(main_content(employee).get_by_text(text)).to_have_count(0)
        finally:
            cleanup_notes(page, day, text)
            browser.close()
