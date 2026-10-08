from playwright.sync_api import sync_playwright, expect
from utils.dashboard_helper import (open_browser_as, open_tasks, section, section_header, task_header_counts, task_cards,
                                    card_status)


def test_expand_collapse_and_counts():
    """DB-012: the Tasks section opens and closes; the header total equals the number of task cards
    and the To do / In Progress badges match the cards' statuses."""
    with sync_playwright() as p:
        browser, page = open_browser_as(p, "admin")
        body = section(page, "Tasks")
        expect(body.get_by_text("Task Filter")).to_be_hidden()

        open_tasks(page)
        total, todo, in_progress = task_header_counts(page)
        statuses = [card_status(card) for card in task_cards(page).all()]
        assert len(statuses) == total, f"header says {total} tasks, {len(statuses)} cards shown"
        assert statuses.count("To Do") == todo, f"badge To do {todo}, cards {statuses.count('To Do')}"
        assert statuses.count("In Progress") == in_progress, \
            f"badge In Progress {in_progress}, cards {statuses.count('In Progress')}"

        section_header(page, "Tasks").click()
        expect(body.get_by_text("Task Filter")).to_be_hidden()
        browser.close()
