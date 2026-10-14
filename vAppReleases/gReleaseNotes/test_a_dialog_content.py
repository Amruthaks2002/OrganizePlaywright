from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import (open_browser, open_releases, page_props, history_rows, open_notes,
                                       notes_dialog, published_text, PLATFORMS)


def test_dialog_content():
    """AR-038: View release notes opens '<Platform> release <latest>' with the minimum, publish date and author, and
    both messages in full under their explanations."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)
        data = page_props(page)["history"]["data"]
        index = next(i for i, r in enumerate(data) if r["optional_message"] and r["mandatory_message"])
        release = data[index]

        open_notes(history_rows(page)[index])
        dialog = notes_dialog(page)
        for text in [f"{PLATFORMS[release['platform']]} release {release['latest_version']}",
                     f"Minimum {release['min_version']} · Published {published_text(release['created_at'])} "
                     f"by {release['created_by']}",
                     "Optional update message", "Shown to installs below the latest version.",
                     release["optional_message"],
                     "Mandatory update message", "Shown on the blocking screen below the minimum.",
                     release["mandatory_message"]]:
            expect(dialog.get_by_text(text, exact=True)).to_be_visible()
        expect(dialog.get_by_role("button", name="Close")).to_be_visible()

        browser.close()
