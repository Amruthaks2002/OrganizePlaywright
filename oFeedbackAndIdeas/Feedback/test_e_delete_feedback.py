from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg = page.get_by_text(text)
    msg.wait_for(state="visible" , timeout=timeout)
    return msg

def test_delete_feedback():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("sidebar-navlink-feedback & ideas").click()
        view_details_btn = page.locator("//button[text()=' View Details ']")
        view_details_btn.first.click()
        modal = page.locator("div.relative.z-10.transform")
        modal.get_by_role("button" , name =" Delete ").click()
        expect(page.get_by_role("heading", name="Delete Feedback")).to_be_visible()

        page.get_by_role("button", name="Delete").last.click()
        time.sleep(2)
        wait_for_message(page,"Submission deleted.")
        print("success message appeared")
