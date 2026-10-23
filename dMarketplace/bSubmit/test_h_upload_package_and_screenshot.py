import re

from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, open_create, pick_platform, fill_form, submit_for_review, expect_toast, delete_apps,
    main_content, package_input, screenshot_input, show_url, app_data, approve_app, open_app, stat,
    PACKAGE_ZIP, SCREENSHOT_PNG,
)


def test_upload_package_and_screenshot():
    """MP-017: a plugin submitted with an uploaded package and a screenshot shows the screenshot,
    a Download link with version and size, and its host app; once live, downloading it serves
    the file and adds one to Downloads."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            open_create(page)
            pick_platform(page, "plugin")
            main = main_content(page)
            main.get_by_role("button", name="Upload", exact=True).click()
            fill_form(page, name=name, short="Uploaded package test.", host_app="VS Code", version="2.0.0")
            screenshot_input(page).set_input_files(SCREENSHOT_PNG)
            expect(main.get_by_text("Cover", exact=True)).to_be_visible()
            package_input(page).set_input_files(PACKAGE_ZIP)
            expect(main.get_by_text("qa_package.zip")).to_be_visible()
            submit_for_review(page)
            expect_toast(page, "Plugin submitted for review.")
            page.wait_for_url(show_url(name))

            data = app_data(page, name)
            expect(main.get_by_role("link", name="Download", exact=True)).to_have_attribute(
                "href", re.compile(rf"/marketplace/{data['id']}/download$"))
            expect(main.get_by_text("v2.0.0 · 128 B")).to_be_visible()
            expect(main.locator("img[src*='/screenshots/']")).to_have_count(1)
            expect(main).to_contain_text("VS Code")

            approve_app(page, data["id"])
            open_app(page, name)
            assert stat(page, "Downloads") == 0
            with page.expect_download() as downloaded:
                main.get_by_role("link", name="Download", exact=True).click()
            assert downloaded.value.suggested_filename == "qa_package.zip"
            open_app(page, name)
            assert stat(page, "Downloads") == 1
        finally:
            delete_apps(page, name)

        browser.close()
