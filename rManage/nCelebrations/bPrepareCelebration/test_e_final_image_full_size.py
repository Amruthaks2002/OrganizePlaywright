import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, open_prepare, main_content, final_image, image_viewer


def test_final_image_full_size():
    """PC-005: the final image is shown as ready for approval and opens full size."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_prepare(page)

        expect(final_image(page)).to_be_visible()
        expect(main_content(page).get_by_text("Image ready for approval!")).to_be_visible()
        final_image(page).hover()
        expect(main_content(page).get_by_text("View Full Size")).to_be_visible()

        final_image(page).click()
        viewer = image_viewer(page, "Final Celebration Image")
        expect(viewer).to_be_visible()
        expect(viewer.locator("img")).to_have_attribute("src", re.compile(r"/storage/celebrations/final/"))
        viewer.get_by_role("button").first.click()
        expect(viewer).to_be_hidden()

        browser.close()
