from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, unique_form_title, delete_forms, build_form, open_settings,
    form_type_select, goto, submission_url, PROBATION_URL, FORMS_URL, search_forms, form_row,
    expect_row_active,
)


def test_public_link_opens_form():
    """PR-009: a probation review form saved from the Settings panel is active and its public link opens.

    Known bug: Settings > Save on a new form saves it as Inactive, so the new
    probation form's public link shows "Form Closed — no longer accepting
    responses". (Saving with the Save Form button keeps it active.) This test
    fails until that's fixed.
    """
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        title = unique_form_title()
        try:
            build_form(page, title, [("How did the probation go?", "Short Answer", (), False)])
            panel = open_settings(page)
            form_type_select(panel).select_option("probation_review")
            with page.expect_response(lambda r: r.request.method == "POST" and r.url.rstrip("/") == FORMS_URL
                                      and r.status == 200) as saved:
                panel.get_by_role("button", name="Save").click()
            form = saved.value.json()["data"]

            goto(page, submission_url(form))
            expect(page.get_by_role("heading", name="Form Closed")).to_have_count(0)
            expect(page.get_by_text("Select an employee from the dropdown above to start their evaluation form.")) \
                .to_be_visible()

            goto(page, PROBATION_URL)
            search_forms(page, title)
            expect_row_active(form_row(page, title))
        finally:
            delete_forms(page, title)

        browser.close()
