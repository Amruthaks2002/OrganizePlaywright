from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import (
    open_browser, open_create_form, unique_form_title, delete_forms, build_form, save_new_form, main_content,
    description_editor, goto, submission_url,
)


def test_description_rich_text():
    """CF-006: the description editor formats text, counts words, and the formatting is kept on the form."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        main = main_content(page)
        title = unique_form_title()
        try:
            build_form(page, title)
            editor = description_editor(page)
            editor.click()
            page.keyboard.type("Please answer honestly")
            expect(main.locator(".tox-statusbar__wordcount")).to_have_text("3 words")

            page.keyboard.press("ControlOrMeta+a")
            main.get_by_role("button", name="Bold").click()
            main.get_by_role("button", name="Italic").click()
            expect(editor.locator("strong")).to_have_text("Please answer honestly")
            expect(editor.locator("em")).to_have_text("Please answer honestly")

            form = save_new_form(page)
            assert "<strong>" in form["description"] and "<em>" in form["description"], form["description"]

            goto(page, submission_url(form))
            expect(page.locator("strong", has_text="Please answer honestly")).to_be_visible()
        finally:
            delete_forms(page, title)

        browser.close()
