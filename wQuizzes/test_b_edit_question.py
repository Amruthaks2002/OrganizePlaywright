import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_edit_question():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--start-maximized"]
        )

        page = browser.new_page(no_viewport=True)
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-navlink-quizzes").click()
        time.sleep(2)

        # Open the quiz created by test_a_create_quiz.py - quizzes are listed
        # newest first, so the most recently created one is first in the list
        page.get_by_role("link", name="Manage Dashboard").first.click()
        time.sleep(2)

        # Expand the question row, then click its edit (pencil) icon
        page.get_by_text("What is 2 + 2?", exact=False).first.click()
        time.sleep(1)

        edit_icon = page.locator("button.group-hover\\:opacity-100").first
        edit_icon.click(force=True)
        time.sleep(1)

        page.get_by_placeholder("Type your question…").fill("What is 2 + 2? (Edited)")
        page.get_by_role("button", name=re.compile(r"^update$", re.I)).click()

        print("Question updated successfully.")
        time.sleep(3)
