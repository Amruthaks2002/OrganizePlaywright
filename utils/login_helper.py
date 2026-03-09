from playwright.sync_api import Page
def login(page:Page):
    page.goto("https://organice.qc.iocod.com")
    page.fill("#email", "admin@example.com")
    page.fill("#password", "password")
    page.click("[data-testid='sign-in-button']")
    page.wait_for_url("**/dashboard**")
    print("✔ Logged in successfully")
