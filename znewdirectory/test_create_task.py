from playwright.sync_api import sync_playwright, expect
import time
from datetime import date

def test_task_create():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://organice.qc.iocod.com")
        page.fill("#email", "admin@example.com")
        page.fill("#password", "password")
        page.click("[data-testid='sign-in-button']")
        page.click("[data-testid='sidebar-navlink-projects']")
        search_box = page.get_by_placeholder("Search projects...")
        search_box.fill("Automation")
        search_box.press("Enter")
        time.sleep(5)
        heading = page.locator('[data-testid="topbar-header-slot"]')
        expect(heading).to_contain_text("Automation")
        page.evaluate("window.scrollBy(0, 800)")
        page.get_by_role("button",name="Add Task").click()
        page.fill("#name","Task1 created via automation")
        page.fill("#description","Description created via automation")
        modal_form = page.locator("form.space-y-5")
        modal_form.wait_for(state="visible")
        search_input = modal_form.locator("input.vs__search")
        search_input.scroll_into_view_if_needed()
        search_input.click()
        search_input.fill("Admin User")
        search_input.press("Enter")
        time.sleep(4)
        page.select_option("#status",value="todo")
        today = date.today().strftime("%Y-%m-%d")
        page.fill("#due_date", today)
        time.sleep(2)
        page.locator('//*[@id="app"]/div/div/div[2]/main/div/div/div[4]/div[5]/div/div[2]/div/div/form/div[5]/button[2]').click()

        time.sleep(3)

