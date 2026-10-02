from playwright.sync_api import sync_playwright
from utils.celebrations_helper import open_browser, open_prepare, main_content


def test_download_final_image():
    """PC-006: Download Final Image downloads the employee's celebration image."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_prepare(page)

        with page.expect_download() as download:
            main_content(page).get_by_role("button", name="Download Final Image").click()
        assert download.value.suggested_filename == "vidhuprasad-c-p-work_anniversary-celebration.png", \
            download.value.suggested_filename
        assert download.value.failure() is None, download.value.failure()

        browser.close()
