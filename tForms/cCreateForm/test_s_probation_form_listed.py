import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, unique_form_title, delete_forms, build_form, open_settings,
    form_type_select, save_new_form, goto, PROBATION_URL, FORMS_URL, search_forms, form_row, type_filter, settle,
)


def test_probation_form_listed():
    """CF-019: a Probation Review form is listed on Probation Reviews and under the type filter."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        title = unique_form_title()
        try:
            build_form(page, title)
            panel = open_settings(page)
            form_type_select(panel).select_option("probation_review")
            panel.get_by_role("button", name="✕").click()
            form = save_new_form(page)
            assert form["type"] == "probation_review"

            goto(page, PROBATION_URL)
            search_forms(page, title)
            expect(form_row(page, title)).to_have_count(1)

            goto(page, FORMS_URL)
            search_forms(page, title)
            type_filter(page).select_option("probation_review")
            expect(page).to_have_url(re.compile("type=probation_review"))
            settle(page)
            expect(form_row(page, title)).to_have_count(1)
            type_filter(page).select_option("general")
            expect(page).to_have_url(re.compile("type=general"))
            settle(page)
            expect(form_row(page, title)).to_have_count(0)
        finally:
            delete_forms(page, title)

        browser.close()
