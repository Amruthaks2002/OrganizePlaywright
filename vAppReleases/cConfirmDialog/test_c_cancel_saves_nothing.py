from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, open_releases, page_props, reload_props, fill_form, form_values,
                                       publish_button, confirm_dialog, is_release_request, bump)


def test_cancel_saves_nothing():
    """AR-011: closing the publish confirmation with Cancel or the X sends nothing, and the form keeps what was typed.
    Esc doesn't close this dialog (it does close the release notes one), but it doesn't publish either."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        before = page_props(page)
        sent = []
        page.on("request", lambda r: sent.append(r.url) if is_release_request(r) else None)

        fill_form(page, "android", latest_version=bump(before["current"]["android"]["latest_version"]),
                  optional_message="AR-011 not saved")
        typed = form_values(page)
        cancel = confirm_dialog(page).get_by_role("button", name="Cancel", exact=True)
        for close in [lambda: cancel.click(),
                      lambda: (page.keyboard.press("Escape"), page.wait_for_timeout(500), cancel.click()),
                      lambda: confirm_dialog(page).get_by_role("button", name="Close").click()]:
            publish_button(page).click()
            expect(confirm_dialog(page)).to_be_visible()
            close()
            expect(confirm_dialog(page)).to_have_count(0)
            assert form_values(page) == typed, form_values(page)

        page.wait_for_timeout(1000)
        assert sent == [], sent
        after = reload_props(page)
        assert after["current"] == before["current"]
        assert after["history"]["total"] == before["history"]["total"]

        browser.close()
