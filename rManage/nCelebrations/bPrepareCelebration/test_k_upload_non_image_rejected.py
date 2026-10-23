from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_prepare, final_image, final_image_input, make_text_file,
)


def test_upload_non_image_rejected():
    """PC-011: uploading a non-image as the final image is rejected and the image is unchanged."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_prepare(page)
        before = final_image(page).get_attribute("src")

        final_image_input(page).set_input_files(make_text_file())
        expect(page.get_by_text("Please upload a JPEG, PNG, JPG, or WEBP image.").first).to_be_visible()

        open_prepare(page)
        expect(final_image(page)).to_have_attribute("src", before)

        browser.close()
