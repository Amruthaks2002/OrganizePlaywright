from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, open_prepare, section, image_viewer, EMPLOYEE


def test_view_user_image():
    """PC-003: View in Step 1 opens the employee's photo; ✕ closes it."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_prepare(page)
        step = section(page, "Step 1: User Image")

        expect(step.get_by_text(f"{EMPLOYEE}'s Photo")).to_be_visible()
        expect(step.get_by_role("button", name="Replace")).to_be_visible()
        step.get_by_role("button", name="View").click()
        viewer = image_viewer(page, f"{EMPLOYEE}'s Photo")
        expect(viewer).to_be_visible()
        expect(viewer.get_by_role("img", name=f"{EMPLOYEE}'s Photo")).to_be_visible()

        viewer.get_by_role("button").first.click()
        expect(viewer).to_be_hidden()

        browser.close()
