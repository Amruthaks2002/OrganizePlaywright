import re
from playwright.sync_api import sync_playwright, expect
from utils.celebrations_helper import (
    open_browser, open_templates, tab, expect_tab_active, template_cards, template_names, ANNIVERSARY_TEMPLATES, TEST_TEMPLATE_PREFIX,
)


def real_names(page):
    # leave out templates that other tests are creating at the same time
    return [n for n in template_names(page) if not n.startswith(TEST_TEMPLATE_PREFIX)]


def test_switch_tabs():
    """CT-002: the Birthday and Anniversary tabs list their own templates."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_templates(page)

        expect(template_cards(page).first).to_be_visible()
        birthday = real_names(page)
        assert birthday and not set(birthday) & set(ANNIVERSARY_TEMPLATES), f"birthday tab lists {birthday}"

        tab(page, "Anniversary Templates").click()
        expect(page).to_have_url(re.compile(r"\?type=work_anniversary$"))
        expect_tab_active(page, "Anniversary Templates")
        expect(template_cards(page).first).to_be_visible()
        assert sorted(real_names(page)) == ANNIVERSARY_TEMPLATES, template_names(page)
        for card in template_cards(page).all():
            for label in ["Photo", "Size", "Text"]:
                expect(card.get_by_text(label, exact=True)).to_be_visible()
            for action in ["Deactivate", "Delete"]:
                expect(card.get_by_role("button", name=action)).to_be_visible()
            expect(card.get_by_role("link", name="Edit")).to_be_visible()

        tab(page, "Birthday Templates").click()
        expect_tab_active(page, "Birthday Templates")
        expect(template_cards(page).first).to_be_visible()
        assert real_names(page) == birthday, template_names(page)

        browser.close()
