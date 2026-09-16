import time

from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import re

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_designation_creation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        with context.expect_page() as new_page_info:
            page.get_by_test_id("sidebar-navlink-log viewer").click()
            time.sleep(6)

        new_page = new_page_info.value
        new_page.wait_for_load_state()
        expect(new_page).to_have_url(re.compile(r".*/log-viewer"))