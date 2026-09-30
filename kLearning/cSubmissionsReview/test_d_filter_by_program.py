import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import (
    BASE_URL, settle, open_browser, main_content, open_submissions_review, submission_rows, goto,
)


def test_filter_by_program():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)
        rows = submission_rows(page)

        # find the program behind the first submission, then filter by it
        href = rows.first.get_by_role("link", name="Grade / Review").get_attribute("href")
        program_id = re.search(r"/programs/(\d+)/", href).group(1)
        goto(page, f"{BASE_URL}/admin/learning/programs/{program_id}")
        program_title = main.locator("h1, h2").first.inner_text().strip()

        open_submissions_review(page)
        main.get_by_placeholder("All Programs").click()
        page.get_by_role("option", name=program_title, exact=True).click()
        expect(page).to_have_url(re.compile(rf"program_id={program_id}"))
        settle(page)

        assert rows.count() > 0, f"Expected submissions for '{program_title}'"
        for i in range(rows.count()):
            expect(rows.nth(i).get_by_role("link", name="Grade / Review")).to_have_attribute(
                "href", re.compile(rf"/programs/{program_id}/")
            )

        browser.close()
