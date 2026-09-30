from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import settle, open_browser, main_content, open_submissions_review, submission_rows


def test_pagination():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_submissions_review(page)
        main = main_content(page)
        rows = submission_rows(page)

        def review_links():
            return [rows.nth(i).get_by_role("link", name="Grade / Review").get_attribute("href") for i in range(rows.count())]

        first_page = review_links()
        main.get_by_role("link", name="2", exact=True).click()
        page.wait_for_url("**submissions_page=2**")
        settle(page)
        second_page = review_links()

        assert second_page, "Expected submissions on page 2"
        assert not set(first_page) & set(second_page), "Expected page 2 to list different submissions"

        browser.close()
