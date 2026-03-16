from playwright.sync_api import sync_playwright, expect
from utils.login_helper import login
import time

def wait_for_message(page,text,timeout=10000):
    msg= page.get_by_text(text)
    msg.wait_for(state="visible",timeout=timeout)
    return msg

def test_id_proof():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        login(page)
        page.get_by_test_id("theme-toggle-button").click()

        page.get_by_test_id("sidebar-parent-manage").click()
        page.get_by_test_id("sidebar-child-documents").click()
        time.sleep(2)

        import re
        expect(page).to_have_url(re.compile(r".*/user-documents"))

        #search for admin
        page.get_by_placeholder("Search by name or email...").fill("admin")
        page.click("div.vs__selected-options")
        search_input = page.locator("input.vs__search")
        search_input.fill("Admin")
        page.locator("li:has-text('Admin')").click()
        time.sleep(3)

        #upload a document
        celebration_photo_upload = page.get_by_role("button" , name=" Upload ")
        celebration_photo_upload.nth(1).click()
        page.get_by_placeholder("Document Name").fill("Automated document name")
        page.get_by_placeholder("Description").fill("Automated Description")
        page.locator("#upload-doc-file").set_input_files("/Users/amruthaks/Downloads/file_sample.doc")
        page.locator("#upload-doc-submit").click()
        wait_for_message(page,"Document uploaded successfully.")
        time.sleep(3)

        #reset filters
        page.locator("#user-docs-reset-filters").click()
        time.sleep(2)

        #view the uploaded document of admin and check id "automated document name" is present in the popup
        page.get_by_placeholder("Search by name or email...").fill("admin")
        page.click("div.vs__selected-options")
        search_input = page.locator("input.vs__search")
        search_input.fill("Admin")
        page.locator("li:has-text('Admin')").click()
        time.sleep(3)
        page.locator("#view-doc-7-id_proof").nth(0).click()
        expect(page.get_by_text("Automated document name")).to_be_visible()

        #download the document
        with page.expect_download() as download_info:
            page.locator("#view-doc-download").click()
        download = download_info.value

        # print the downloaded file name
        download.save_as("downloads/" + download.suggested_filename)
        print("Downloaded document name is:" , download.suggested_filename)

        #edit the uploaded document
        page.locator("#view-doc-edit").click()
        page.locator("#edit-doc-name").fill("Automated document name edited")
        page.locator("#edit-doc-description").fill("Automated document description edited")
        page.locator("#edit-doc-file").set_input_files("/Users/amruthaks/Downloads/file_sample_edit.doc")
        page.locator("#edit-doc-submit").click()
        time.sleep(3)
        wait_for_message(page, "Document updated successfully.")

        #delete the document
        page.locator("#view-doc-7-id_proof").click()
        page.locator("#view-doc-edit").click()
        print("clicked on edit")
        time.sleep(5)
        modal = page.locator("#edit-doc-modal")
        modal.get_by_role("button", name="Delete").click()
        print("clicked on delete")
        modal1 = page.locator(".modal-surface:has-text('Delete Document')")
        modal1.wait_for(state="visible")
        modal1.get_by_role("button", name="Delete").click()
        time.sleep(3)
        wait_for_message(page, "Document deleted successfully.")












