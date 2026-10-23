import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import open_browser, open_templates, open_add_template, tab, settle


def test_add_dialog_matches_tab():
    """CT-004: the Add Template dialog is for the tab it was opened from."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_templates(page)

        dialog = open_add_template(page)
        expect(dialog.get_by_text("Upload a background template for birthday celebrations")).to_be_visible()
        for label in ["Template Name *", "Description", "Background Template *", "Maximum size: 5MB. JPEG, PNG"]:
            expect(dialog.get_by_text(label, exact=True)).to_be_visible()
        dialog.get_by_role("button", name="Cancel").click()

        tab(page, "Anniversary Templates").click()
        # the tab is a page visit; a dialog opened before it finishes gets wiped
        expect(page).to_have_url(re.compile(r"\?type=work_anniversary$"))
        settle(page)
        dialog = open_add_template(page)
        expect(dialog.get_by_text("Upload a background template for work anniversary celebrations")).to_be_visible()

        browser.close()
