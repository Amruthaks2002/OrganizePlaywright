import re
from playwright.sync_api import sync_playwright, expect
from utils.learning_helper import BASE_URL, open_browser, main_content, goto


def test_open_quiz_results():
    with sync_playwright() as p:
        browser, page = open_browser(p)
        goto(page, f"{BASE_URL}/admin/learning/submissions?tab=quizzes")
        main = main_content(page)

        link = main.get_by_role("link", name="Quiz 1 Results").first
        href = link.get_attribute("href")
        assert re.search(r"/quizzes/\d+/my-result/\d+", href), f"Unexpected results link {href}"

        if link.get_attribute("target") == "_blank":
            with page.context.expect_page() as new_page:
                link.click()
            result_page = new_page.value
        else:
            link.click()
            result_page = page
        result_page.wait_for_url(re.compile(r"/quizzes/\d+/my-result/\d+"))
        expect(result_page.get_by_test_id("main-content")).to_be_visible()

        browser.close()
