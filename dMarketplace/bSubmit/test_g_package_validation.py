from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import (
    open_browser, unique_name, open_create, pick_platform, fill_form, submit_for_review, field_error, delete_apps,
    main_content, package_input, CREATE_URL, NOT_A_PACKAGE,
)


def test_package_validation():
    """MP-016: choosing Upload needs a package file, and a file of the wrong type is refused."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        name = unique_name()
        try:
            open_create(page)
            pick_platform(page, "plugin")
            main_content(page).get_by_role("button", name="Upload", exact=True).click()
            fill_form(page, name=name, short="Package validation.", host_app="VS Code")

            submit_for_review(page)
            expect(field_error(page, "A package file is required for this delivery method.")).to_be_visible()

            package_input(page).set_input_files(NOT_A_PACKAGE)
            expect(main_content(page).get_by_text("qa_notes.txt")).to_be_visible()
            submit_for_review(page)
            expect(field_error(page, "The package field must have one of the following extensions: zip, vsix.")).to_be_visible()
            assert page.url == CREATE_URL, page.url
        finally:
            delete_apps(page, name)

        browser.close()
