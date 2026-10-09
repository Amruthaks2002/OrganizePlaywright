from playwright.sync_api import sync_playwright, expect
from utils.marketplace_helper import open_browser, open_create, pick_platform, main_content, package_input

# platform -> (file upload offered, accepted package types, host app field, min OS field)
EXPECTED = {
    "web": (False, None, False, False),
    "extension": (True, ".zip,.crx,.xpi", False, False),
    "plugin": (True, ".zip,.vsix", True, False),
    "android": (True, ".apk,.aab", False, True),
    "macos": (True, ".dmg,.pkg,.zip", False, True),
    "ios": (False, None, False, True),
}


def test_form_adapts_to_platform():
    """MP-010: the Delivery section changes with the platform: a website is a link, packaged apps
    offer Upload or Link (with the right file types), a plugin asks for its host app, mobile and
    macOS apps ask for a minimum OS, iOS is link-only and an idea needs no delivery at all."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create(page)
        main = main_content(page)
        upload = main.get_by_role("button", name="Upload", exact=True)

        for platform, (has_upload, accept, has_host, has_min_os) in EXPECTED.items():
            pick_platform(page, platform)
            expect(page.locator("#external_url"), platform).to_be_visible()
            expect(page.locator("#version"), platform).to_be_visible()
            expect(upload, platform).to_have_count(1 if has_upload else 0)
            expect(page.locator("#host_app"), platform).to_have_count(1 if has_host else 0)
            expect(page.locator("#min_os_version"), platform).to_have_count(1 if has_min_os else 0)
            if has_upload:
                upload.click()
                expect(page.locator("#external_url"), platform).to_have_count(0)
                expect(package_input(page), platform).to_have_attribute("accept", accept)
                expect(main.get_by_text(f"Drop package ({accept})"), platform).to_be_visible()
                main.get_by_role("button", name="Link", exact=True).click()

        pick_platform(page, "ios")
        expect(main.get_by_text("Apple blocks sideloading, so iOS apps are always shared as a link.")).to_be_visible()

        pick_platform(page, "idea")
        expect(main.get_by_text("It's a concept — no file or link needed.", exact=False)).to_be_visible()
        for field in ["#external_url", "#version", "#host_app", "#min_os_version"]:
            expect(page.locator(field), field).to_have_count(0)
        expect(upload).to_have_count(0)

        browser.close()
