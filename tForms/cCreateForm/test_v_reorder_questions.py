from playwright.sync_api import sync_playwright, expect
from utils.forms_helper import open_browser, open_create_form, question_cards, question_input, add_question


def test_reorder_questions():
    """CF-022: dragging a question by its handle moves it above another question."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        open_create_form(page)
        question_input(question_cards(page).first).fill("First")
        question_input(add_question(page)).fill("Second")

        handle = question_cards(page).nth(1).locator("div.cursor-move")
        target = question_cards(page).nth(0).locator("div.cursor-move")
        box, target_box = handle.bounding_box(), target.bounding_box()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.mouse.down()
        for step in range(1, 11):
            page.mouse.move(target_box["x"] + target_box["width"] / 2,
                            box["y"] + (target_box["y"] - box["y"]) * step / 10)
            page.wait_for_timeout(50)
        page.mouse.up()

        expect(question_input(question_cards(page).nth(0))).to_have_value("Second")
        expect(question_input(question_cards(page).nth(1))).to_have_value("First")

        browser.close()
