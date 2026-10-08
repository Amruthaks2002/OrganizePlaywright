import re

from playwright.sync_api import sync_playwright
from utils.dashboard_helper import open_browser_as, open_attendance, attendance_stat, attendance_text


def test_work_mode_split_and_percentage():
    """DB-005: In Work Mode equals Remote + Request, and the Present % equals present / total (rounded)."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        open_attendance(page)
        text = attendance_text(page)

        in_work_mode = attendance_stat(page, "In Work Mode")
        remote = int(re.search(r"Remote\s*·\s*(\d+)", text).group(1))
        request = int(re.search(r"Request\s*·\s*(\d+)", text).group(1))
        assert in_work_mode == remote + request, f"In Work Mode {in_work_mode} != Remote {remote} + Request {request}"

        total = attendance_stat(page, "Total Employees")
        present = attendance_stat(page, "Present Today")
        percent = int(re.search(r"Present Today\s*\n\s*\d+\s*\n\s*(\d+)%", text).group(1))
        assert percent == round(present / total * 100), f"{percent}% shown for {present}/{total}"
        browser.close()
