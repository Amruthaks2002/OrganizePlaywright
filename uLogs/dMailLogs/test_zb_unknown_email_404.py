"""ML-028: An unknown mail address.

Steps:
1. Log in as admin.
2. Go to /mail-logs/doesnotexist123 and /mail-logs/000000000000000000000000.

Expected: both answer 404 and no mail is shown.
"""
import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"
LOGS_URL = f"{BASE_URL}/mail-logs"
EMPTY_MESSAGE = "No mail has been sent yet."


def test_ml_028_unknown_email_404():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        for mail_id in ["doesnotexist123", "000000000000000000000000"]:
            response = page.goto(f"{LOGS_URL}/{mail_id}")
            assert response.status == 404, f"/mail-logs/{mail_id} answered {response.status}"
            assert page.get_by_text("Recipient:").count() == 0

        browser.close()
