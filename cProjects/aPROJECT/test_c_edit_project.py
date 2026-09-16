from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login

def test_edit_project():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.click("[data-testid='sidebar-navlink-projects']")
        page.locator('//*[@id="app"]/div/div/div[2]/main/div/div/div[2]/div/div[2]/button[2]').click()
        page.locator("tbody tr").first.get_by_role("button", name="Edit").click()
        page.fill("#edit_name","Automation Project Edited")
        page.select_option("#edit_project_manager_id",index=2)
        page.fill("#edit_description", "Automation Project description edited")
        create_project_btn = page.locator("//form//button[contains(., 'Update Project')]")
        create_project_btn.click()
        success_msg = page.locator("text=Project updated successfully")
        expect(success_msg).to_be_visible()
        print("✅ Project updated success message displayed")



