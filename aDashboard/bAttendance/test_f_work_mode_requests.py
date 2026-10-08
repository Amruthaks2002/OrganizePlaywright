import re

from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_attendance, attendance_panel, attendance_text, panel_count,
                                    person_buttons, person_row)


def test_work_mode_requests():
    """DB-009: the Work Mode Requests count matches its list (and Request · N); each row shows the
    work mode, and an empty list says 'No WFH requests today'."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        open_attendance(page)
        count = panel_count(page, "Work Mode Requests")
        request = int(re.search(r"Request\s*·\s*(\d+)", attendance_text(page)).group(1))
        assert count == request, f"Work Mode Requests {count} != Request · {request}"
        expect(person_buttons(page, "Work Mode Requests")).to_have_count(count)

        empty = attendance_panel(page, "Work Mode Requests").get_by_text("No WFH requests today")
        if count == 0:
            expect(empty).to_be_visible()
        else:
            expect(empty).to_have_count(0)
        for button in person_buttons(page, "Work Mode Requests").all():
            assert re.search(r"(WORK FROM HOME|ONSITE|REMOTE)", person_row(button, "-").inner_text(), re.I)
        browser.close()
