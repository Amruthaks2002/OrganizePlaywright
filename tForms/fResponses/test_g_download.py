import re
from playwright.sync_api import sync_playwright
from utils.forms_helper import (
    open_browser, unique_form_title, create_form_api, question, submit_response_api, delete_forms, goto,
    responses_url, main_content,
)


def test_download():
    """RS-007: Download saves the responses as responses_<title>_<timestamp>.xlsx."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        title = unique_form_title()
        try:
            form = create_form_api(page, title, [question("Name")])
            submit_response_api(page, form, {"Name": "Sam"})
            goto(page, responses_url(form))

            with page.expect_download() as download:
                main_content(page).locator("a").filter(has_text="Download").click()
            slug = title.lower().replace(" ", "_")
            assert re.fullmatch(rf"responses_{slug}_[\d_]+\.xlsx", download.value.suggested_filename), \
                download.value.suggested_filename
        finally:
            delete_forms(page, title)

        browser.close()
