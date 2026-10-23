import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_prepare, main_content, final_image, backup_final_image, upload_final_image, make_png,
)


def test_upload_final_image():
    """PC-010: Upload Final Image replaces the final image (the original image is uploaded back afterwards)."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_prepare(page)
        original = backup_final_image(page)
        try:
            upload_final_image(page, make_png("final.png", 540, 960))
            new_src = final_image(page).get_attribute("src")

            open_prepare(page)
            expect(final_image(page)).to_have_attribute("src", new_src)
            expect(main_content(page).get_by_text("Image ready for approval!")).to_be_visible()
            details = main_content(page).get_by_role("heading", name="Celebration Details").locator("xpath=..")
            expect(details).to_contain_text(re.compile(r"Status:\s*APPROVED"))
        finally:
            open_prepare(page)
            upload_final_image(page, original)

        browser.close()
