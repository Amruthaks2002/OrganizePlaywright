from playwright.sync_api import sync_playwright, expect
from utils.app_releases_helper import open_browser, open_releases, form, field

FIELDS = {
    "latest_version": ("Latest version", "1.4.0", "The newest version live in the store."),
    "min_version": ("Minimum version", "1.2.0", "Anything older is blocked until it updates."),
    "optional_message": ("Optional update message", "A new version is available with…",
                         "Shown to installs below the latest version; they can dismiss it. "
                         "Leave empty for the default text."),
    "mandatory_message": ("Mandatory update message", "This version is no longer supported…",
                          "Shown on the blocking screen to installs below the minimum. "
                          "Leave empty for the default text."),
}


def test_labels_and_hints():
    """AR-007: each field has its label, placeholder and helper text; the platform choice offers Android and iOS."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_releases(page)

        assert [t.strip() for t in form(page).locator("input[name=platform] + span").all_inner_texts()] == \
            ["Android", "iOS"]
        for name, (label, placeholder, hint) in FIELDS.items():
            expect(form(page).locator(f"label[for={name}]")).to_have_text(label)
            expect(field(page, name)).to_have_attribute("placeholder", placeholder)
            expect(field(page, name).locator("xpath=..").locator("p").first).to_have_text(hint)

        browser.close()
