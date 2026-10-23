from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, page_props, current_releases, open_edit_from_card, fill_form,
                                       save_button, confirm_dialog, dialog_title, dialog_message, dialog_buttons,
                                       form_heading, assert_nothing_saved)


def test_save_confirmation():
    """AR-034: Save changes asks 'Update the current iOS release?' first; Cancel keeps the edit form and saves
    nothing."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        snapshot = current_releases(page)
        total = page_props(page)["history"]["total"]
        release = snapshot["ios"]
        latest, minimum = release["latest_version"], release["min_version"]

        open_edit_from_card(page, "ios")
        fill_form(page, optional_message="AR-034 not saved")
        save_button(page).click()
        expect(dialog_title(page)).to_have_text("Update the current iOS release?")
        expect(dialog_message(page)).to_have_text(
            f"Latest {latest}, minimum {minimum}. Installs below {minimum} will be blocked until they update.")
        assert dialog_buttons(page) == ["Cancel", "Save changes"], dialog_buttons(page)

        confirm_dialog(page).get_by_role("button", name="Cancel", exact=True).click()
        expect(confirm_dialog(page)).to_have_count(0)
        expect(form_heading(page)).to_have_text("Edit current iOS release")
        assert_nothing_saved(page, snapshot, total)

        browser.close()
