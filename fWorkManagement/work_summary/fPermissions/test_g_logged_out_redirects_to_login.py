import os
from playwright.sync_api import sync_playwright, expect
from utils.work_summary_helper import BASE_URL, HOURS_URL, LOGS_URL, CHART_URL


def test_logged_out_redirects_to_login():
    """WS-046: someone who isn't signed in is sent to the login page, and the data endpoints give them nothing."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
        page = browser.new_context().new_page()

        page.goto(HOURS_URL)
        expect(page).to_have_url(f"{BASE_URL}/login")
        for url in [LOGS_URL, CHART_URL]:
            response = page.request.get(url, max_redirects=0)
            assert response.status in (302, 401), (url, response.status)
            if response.status == 302:
                assert response.headers["location"] == f"{BASE_URL}/login", (url, response.headers["location"])

        browser.close()
