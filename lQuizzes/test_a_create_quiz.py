import re
import time

from playwright.sync_api import sync_playwright
from utils.login_helper import login

def wait_for_message(page, pattern, timeout=10000):
    msg = page.get_by_text(pattern)
    msg.wait_for(state="visible", timeout=timeout)
    return msg

def test_create_quiz():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")

        page.get_by_test_id("sidebar-navlink-quizzes").click()
        time.sleep(2)

        page.get_by_role("button", name="Create New Quiz", exact=True).click()
        time.sleep(1)

        unique_suffix = str(int(time.time()))

        # Leave "Attach to Session" at its default "Standalone Quiz (No Session)"
        page.locator("#title").fill(f"Automation Quiz {unique_suffix}")
        page.locator("#description").fill("Created by automated Playwright test.")

        page.get_by_role("button", name="CREATE & CONTINUE").click()
        wait_for_message(page, re.compile("Quiz created", re.I))
        print("Quiz created successfully.")
        time.sleep(2)

        # Add questions to the quiz we just created
        questions = [
            ("What is 2 + 2?", "4", "5", "30", "10"),
            ("What is the capital of France?", "Paris", "Berlin", "30", "10"),
            ("Which language does Playwright support?", "Python", "COBOL", "30", "10"),
            ("What does CI stand for?", "Continuous Integration", "Central Intelligence", "30", "10"),
        ]

        for question, answer1, answer2, duration, points in questions:
            page.get_by_role("button", name="ADD QUESTION").first.click()
            time.sleep(1)

            page.get_by_placeholder("Type your question…").fill(question)
            page.get_by_placeholder("Answer 1").fill(answer1)
            page.get_by_placeholder("Answer 2").fill(answer2)

            number_inputs = page.locator("input[type=number]")
            number_inputs.nth(0).fill(duration)
            number_inputs.nth(1).fill(points)

            # The modal's own submit button is the last "ADD QUESTION" button on the page
            page.get_by_role("button", name="ADD QUESTION").last.click()
            time.sleep(1.5)
            print(f"Question added successfully: {question}")

        time.sleep(3)
