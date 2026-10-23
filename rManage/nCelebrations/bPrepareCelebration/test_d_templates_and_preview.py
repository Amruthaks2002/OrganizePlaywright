import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_prepare, template_options, template_option, image_viewer, ANNIVERSARY_TEMPLATES,
)


def test_templates_and_preview():
    """PC-004: Step 2 lists the active anniversary templates with one selected; View previews a template."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_prepare(page)

        names = [n.strip() for n in template_options(page).locator("p.font-semibold").all_inner_texts()]
        assert sorted(names) == ANNIVERSARY_TEMPLATES, f"unexpected templates in Step 2: {names}"
        selected = template_options(page).filter(has=page.locator("xpath=self::*[contains(@class,'border-purple-600')]"))
        expect(selected).to_have_count(1)
        for name in names:
            expect(template_option(page, name).get_by_text("right")).to_be_visible()
            expect(template_option(page, name).get_by_text("medium")).to_be_visible()

        name = names[0]
        template_option(page, name).get_by_role("button", name="View").click()
        viewer = image_viewer(page, name)
        expect(viewer).to_be_visible()
        expect(viewer.locator("img")).to_have_attribute("src", re.compile(r"/storage/templates/"))

        browser.close()
