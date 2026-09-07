from playwright.sync_api import sync_playwright
import time
from utils.login_helper import login

def test_events():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        login(page)
        page.wait_for_url("**/dashboard**")
        time.sleep(3)
        page.get_by_text("View All").click()
        time.sleep(3)

        value_selector = "span.min-w-\\[60px\\]"

        # --- Zoom In ---
        before_zoom_in = page.locator(value_selector).first.inner_text().strip()
        before_zoom_in_value = float(before_zoom_in.replace("%", "").strip())

        page.locator("button:has(svg.lucide-zoom-in)").first.click()
        time.sleep(2)

        after_zoom_in = page.locator(value_selector).first.inner_text().strip()
        after_zoom_in_value = float(after_zoom_in.replace("%", "").strip())

        print(f"Zoom In -> Before: {before_zoom_in_value}%, After: {after_zoom_in_value}%")
        assert after_zoom_in_value > before_zoom_in_value, (
            f"Expected value to increase after zoom-in, but went from "
            f"{before_zoom_in_value}% to {after_zoom_in_value}%"
        )

        # --- Zoom Out (click twice) ---
        before_zoom_out_value = after_zoom_in_value  # current value before zoom out

        zoom_out_button = page.locator("button:has(svg.lucide-zoom-out)").first

        # First click
        zoom_out_button.click()
        time.sleep(1)
        after_first_click = page.locator(value_selector).first.inner_text().strip()
        after_first_click_value = float(after_first_click.replace("%", "").strip())

        print(f"Zoom Out (1st click) -> Before: {before_zoom_out_value}%, After: {after_first_click_value}%")
        assert after_first_click_value < before_zoom_out_value, (
            f"Expected value to decrease after 1st zoom-out click, but went from "
            f"{before_zoom_out_value}% to {after_first_click_value}%"
        )

        # Second click
        zoom_out_button.click()
        time.sleep(1)
        after_second_click = page.locator(value_selector).first.inner_text().strip()
        after_second_click_value = float(after_second_click.replace("%", "").strip())

        print(f"Zoom Out (2nd click) -> Before: {after_first_click_value}%, After: {after_second_click_value}%")
        assert after_second_click_value < after_first_click_value, (
            f"Expected value to decrease further after 2nd zoom-out click, but went from "
            f"{after_first_click_value}% to {after_second_click_value}%"
        )

        # --- Reset zoom  ---
        page.get_by_role("button", name="Reset Filters").click()
        time.sleep(1)

        after_reset = page.locator(value_selector).first.inner_text().strip()
        after_reset_value = float(after_reset.replace("%", "").strip())

        print(f"Reset -> Value after reset: {after_reset_value}%")

        assert after_reset_value == 85.0, (
            f"Expected value to reset to 100%, but got {after_reset_value}%"
        )

        browser.close()