import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_delete_quiz():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-navlink-quizzes").click()
        time.sleep(2)

        # Search for the quiz created by test_a_create_quiz.py
        search_box = page.get_by_placeholder("Quiz title...")
        search_box.fill("Automation Quiz")
        time.sleep(5)

        assert page.get_by_title("Delete Quiz").count() > 0, "Expected at least one 'Automation Quiz' result"

        # Results are listed newest first, so the first one is the quiz we just created
        page.get_by_title("Delete Quiz").first.click()
        time.sleep(1)

        # The confirmation dialog renders twice in the DOM, so target the last
        # "Delete" button and force the click past the duplicate overlay
        page.get_by_role("button", name="Delete", exact=True).last.click(force=True)

        wait_for_message(page, re.compile("Quiz deleted successfully", re.I))
        print("Quiz deleted successfully.")
        time.sleep(3)
