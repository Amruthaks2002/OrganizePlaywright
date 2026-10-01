import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_my_forms, unique_form_title, create_form_api, delete_forms, search_forms, form_rows,
    footer_summary, page_label, pager_link, expect_pager_disabled, settle,
)


def test_pagination():
    """FM-025: 11 forms split into pages of 10 with working Previous / Next."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_my_forms(page)
        base = unique_form_title()
        try:
            for i in range(11):
                create_form_api(page, f"{base} {i:02d}")
            search_forms(page, base)

            expect(form_rows(page)).to_have_count(10)
            expect(footer_summary(page)).to_have_text("Showing 1 to 10 of 11 rows")
            expect(page_label(page)).to_have_text(re.compile(r"Page 1 / 2"))
            expect_pager_disabled(pager_link(page, "Previous"))
            expect_pager_disabled(pager_link(page, "Next"), False)

            pager_link(page, "Next").click()
            expect(page).to_have_url(re.compile(r"page=2"))
            settle(page)
            expect(form_rows(page)).to_have_count(1)
            expect(footer_summary(page)).to_have_text("Showing 11 to 11 of 11 rows")
            expect(page_label(page)).to_have_text(re.compile(r"Page 2 / 2"))
            expect_pager_disabled(pager_link(page, "Next"))

            expect_pager_disabled(pager_link(page, "Previous"), False)
            pager_link(page, "Previous").click()
            expect(page).to_have_url(re.compile(r"page=1"))
            settle(page)
            expect(form_rows(page)).to_have_count(10)
            expect(footer_summary(page)).to_have_text("Showing 1 to 10 of 11 rows")

            # a single page of results disables both buttons
            search_forms(page, f"{base} 00")
            expect(footer_summary(page)).to_have_text("Showing 1 to 1 of 1 rows")
            expect(page_label(page)).to_have_text(re.compile(r"Page 1 / 1"))
            expect_pager_disabled(pager_link(page, "Previous"))
            expect_pager_disabled(pager_link(page, "Next"))
        finally:
            delete_forms(page, base)

        browser.close()
