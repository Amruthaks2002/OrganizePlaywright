from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    open_browser, main_content, unique_name, create_program, add_root_module, modal, expect_toast,
    select_node, delete_program,
)


def test_material_crud():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        main = main_content(page)
        title = unique_name("QA Learning Material")
        program_id = create_program(page, title, hours="1")
        try:
            add_root_module(page, program_id, "QA Material Module", hours="1")
            select_node(page, "QA Material Module")
            expect(main.get_by_text("No materials added.")).to_be_visible()

            # a URL is required for URL/link materials
            main.get_by_role("button", name="+ Add Material").click()
            dialog = modal(page, "Add Learning Material")
            dialog.get_by_role("button", name="Add Material").click()
            expect_toast(page, "The url field is required when material type is url.")

            dialog.locator("select").select_option(label="Link (Google Docs, Figma, Notion, GitHub, etc.)")
            dialog.locator("input[type=text]").fill("QA Material Link")
            dialog.locator("input[type=url]").fill("https://example.com/qa-material")
            dialog.get_by_role("button", name="Add Material").click()
            expect_toast(page, "Material added successfully.")
            row = main.locator("li").filter(has_text="QA Material Link")
            expect(row).to_contain_text("(link)")
            expect(row.locator("a[title='Preview / Open Resource']")).to_have_attribute("href", "https://example.com/qa-material")

            row.locator("button[title='Edit material']").click()
            dialog = modal(page, "Edit Learning Material")
            dialog.locator("input[type=text]").fill("QA Material Link Edited")
            dialog.get_by_role("button", name="Save Changes").click()
            expect_toast(page, "Material updated successfully.")
            expect(main.locator("li").filter(has_text="QA Material Link Edited")).to_have_count(1)

            main.locator("li").filter(has_text="QA Material Link Edited").locator("button[title='Delete material']").click()
            expect_toast(page, "Material deleted successfully.")
            expect(main.get_by_text("No materials added.")).to_be_visible()
        finally:
            delete_program(page, title)

        browser.close()
