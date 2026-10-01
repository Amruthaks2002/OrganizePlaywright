import re
from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, submit_response_api, delete_forms, goto,
    responses_url, view_tab, responses_table, table_rows,
)


def test_tabular_view():
    """RS-003: Tabular shows one row per response with a column per question."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Name"), question("Pets", "checkbox", ["Cat", "Dog"])])
            submit_response_api(page, form, {"Name": "Sam", "Pets": ["Cat", "Dog"]})
            goto(page, responses_url(form))

            view_tab(page, "Tabular").click()
            table = responses_table(page)
            expect(table.locator("th")).to_have_text(
                [re.compile(h, re.I) for h in ["#", "Responder", "Name", "Pets"]])
            assert table_rows(page) == [["1", "Admin User", "Sam", "Cat, Dog"]], table_rows(page)
        finally:
            delete_forms(page, title)

        browser.close()
