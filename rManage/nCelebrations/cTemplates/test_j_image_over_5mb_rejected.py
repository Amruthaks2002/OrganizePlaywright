from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_templates, open_add_template, fill_template_form, template_card, unique_template_name,
    make_png, delete_templates, ANNIVERSARY_TEMPLATES_URL, TEMPLATE_SIZES,
)


def test_image_over_5mb_rejected():
    """CT-010: picking an image over 5MB shows an alert and the template isn't created."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_templates(page, ANNIVERSARY_TEMPLATES_URL)
        name = unique_template_name()
        # the right size for an anniversary template, so only the 5MB limit applies
        big = make_png("big.png", *TEMPLATE_SIZES["work_anniversary"], noise=True)
        try:
            dialog = open_add_template(page)
            # open_browser accepts every dialog; this only records the message
            with page.expect_event("dialog") as alert:
                fill_template_form(dialog, name, big)
            assert alert.value.message == "Image size must not exceed 5MB", alert.value.message

            dialog.get_by_role("button", name="Create Template").click()
            open_templates(page, ANNIVERSARY_TEMPLATES_URL)
            expect(template_card(page, name)).to_have_count(0)
        finally:
            delete_templates(page, name)

        browser.close()
