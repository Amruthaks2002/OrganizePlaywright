from playwright.sync_api import sync_playwright, expect
from datetime import date
from utils.login_helper import login

def test_task_assign():

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.locator("//a[@data-testid='sidebar-navlink-projects']").click()
        page.wait_for_url("**/projects")
        print("✔ Navigated to Projects Page")
        page.locator("//button[contains(., 'Create Project')]").click()
        page.fill("#name", "Automation Test Project")
        page.select_option("#project_manager_id", index=1)
        print("✔ Manager selected")
        page.locator("//label[normalize-space()='core development team']").click()
        today = date.today().strftime("%Y-%m-%d")
        page.fill("#end_date", today)
        create_project_btn = page.locator("//form//button[contains(., 'Create Project')]")
        create_project_btn.scroll_into_view_if_needed()
        create_project_btn.click()
        print("✔ Project Created")
        project_name = "Automation Test Project"
        view_btn = page.locator(
            f"//h3/a[text()='{project_name}']/ancestor::div[contains(@class,'rounded-2xl')]//a[contains(text(),'View')]"
        )
        view_btn.click(force=True)
        print("✔ Opened Project")
        create_task(page, "Automation Task 01", None)
        create_task(page, "Automation Task 02", "in_progress")
        create_task(page, "Automation Task 03", "completed")
        create_task_with_due_date(page, "Automation Task 04", today)
        print("\n✔ ALL 4 TASKS CREATED SUCCESSFULLY")
        context.close()
        browser.close()


# ---------------- NORMAL TASK FUNCTION ----------------

def create_task(page, task_name, status=None):

    page.locator("//button[contains(., 'Add Task')]").click()

    page.fill("#name", task_name)
    page.fill("#description", "This task is created via Playwright automation.")

    assign_user(page)

    if status:
        page.select_option("#status", value=status)
        print(f"✔ Status set to {status.upper()}")

    page.locator("//button[normalize-space()='Create']").click()

    success_msg = page.locator("text=successfully")
    expect(success_msg).to_be_visible(timeout=8000)

    print(f"✔ {task_name} Created Successfully\n")

    page.wait_for_timeout(2000)


# ---------------- TASK WITH DUE DATE FUNCTION ----------------

def create_task_with_due_date(page, task_name, due_date):

    page.locator("//button[contains(., 'Add Task')]").click()

    page.fill("#name", task_name)
    page.fill("#description", "This task includes due date automation.")

    # ✅ Set Due Date (Today)
    page.fill("#due_date", due_date)

    print("✔ Due date set:", due_date)

    assign_user(page)

    page.locator("//button[normalize-space()='Create']").click()

    success_msg = page.locator("text=successfully")
    expect(success_msg).to_be_visible(timeout=8000)

    print(f"✔ {task_name} Created With Due Date Successfully\n")


def assign_user(page):

    dropdown_toggle = page.locator(
        "//div[contains(@class,'max-h-[90vh]')]//div[contains(@class,'vs__dropdown-toggle')]"
    )
    dropdown_toggle.click()

    page.wait_for_timeout(1000)

    search_box = page.locator(
        "//div[contains(@class,'max-h-[90vh]')]//input[contains(@class,'vs__search')]"
    )
    search_box.fill("Admin")

    page.wait_for_timeout(1000)

    page.locator("//li[contains(., 'Admin User')]").click()
