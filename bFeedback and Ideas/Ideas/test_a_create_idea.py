from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg=page.get_by_text(text)
    msg.wait_for(state="visible" , timeout=timeout)
    return msg

def test_create_idea():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)

        page.get_by_test_id("sidebar-navlink-feedback & ideas").click()
        print("Current url", page.url)
        expect(page).to_have_url("https://organice.qc.iocod.com/admin/feedback-submissions")
        time.sleep(1)
        page.locator("a[href*='idea-submissions']").click()

        create_btn = page.locator("//button[text()=' Submit Idea']")
        create_btn.click()
        time.sleep(1)
        page.get_by_placeholder("Describe your feedback or idea...").fill("This idea is submitted via automation.")
        time.sleep(1)
        modal = page.locator("div.relative.z-10.transform")
        expect(modal.get_by_text("Submit New Idea")).to_be_visible()
        modal.locator("textarea").fill("Automation Idea test")
        submit_btn = modal.get_by_role("button", name="Submit Idea")
        expect(submit_btn).to_be_enabled()

        submit_btn.click()
        time.sleep(3)

        wait_for_message(page, "Idea submitted successfully.")
        print("success message appeared")


