from playwright.sync_api import sync_playwright, expect
import time
from utils.login_helper import login

def wait_for_message(page,text,timeout=10000):
    msg=page.get_by_text(text)
    msg.wait_for(state="visible" , timeout=timeout)
    return msg

def test_delete_ideas():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("sidebar-navlink-feedback & ideas").click()

        import re
        page.locator("a[href*='idea-submissions']").click()
        expect(page).to_have_url(re.compile(r".*/admin/idea-submissions.*"))

        page.get_by_role("button", name="View Details").first.click()
        time.sleep(1)
        modal = page.locator("div.relative.z-10.transform")
        modal.get_by_role("button", name="Delete").click()
        time.sleep(2)
        delete_modal = page.get_by_role("heading", name="Delete Idea") \
            .locator("xpath=ancestor::div[contains(@class,'max-h')]")
        expect(delete_modal).to_be_visible()
        delete_modal.get_by_role("button", name="Delete").click()
        time.sleep(1)
        wait_for_message(page,"Submission deleted.")
        time.sleep(1)



