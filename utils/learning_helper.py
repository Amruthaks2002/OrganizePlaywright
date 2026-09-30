import os
import time
from urllib.parse import quote

from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError
from utils.login_helper import login

BASE_URL = "https://organice.qc.iocod.com"


def open_browser(p):
    # set HEADLESS=1 to run without a visible browser window
    browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
    context = browser.new_context(viewport={"width": 1600, "height": 900})
    page = context.new_page()
    # material / assessment / node deletes use a native confirm()
    page.on("dialog", lambda dialog: dialog.accept())
    login(page)
    return browser, page


def unique_name(prefix):
    return f"{prefix} {str(int(time.time() * 1000))[-6:]}"


def main_content(page: Page):
    return page.get_by_test_id("main-content")


def modal(page: Page, text):
    # confirmation dialogs render several copies in the DOM, so use the last visible one
    return page.locator("div.fixed.inset-0:visible").filter(has_text=text).last


def expect_toast(page: Page, message, timeout=10000):
    expect(page.get_by_text(message).first).to_be_visible(timeout=timeout)


def open_learning_submenu(page: Page, child):
    # the Learning group is already expanded when we're on one of its pages
    if not page.get_by_test_id(f"sidebar-child-{child}").is_visible():
        page.get_by_test_id("sidebar-parent-learning").click()
    page.get_by_test_id(f"sidebar-child-{child}").click()


def open_manage_programs(page: Page):
    open_learning_submenu(page, "manage-programs")
    page.wait_for_url("**/admin/learning")
    page.wait_for_timeout(1500)


def search_programs(page: Page, title):
    goto(page, f"{BASE_URL}/admin/learning?search={quote(title)}")


def create_program(page: Page, title, description="", hours="0", days="0"):
    """Creates a draft program from the Manage Programs page and returns its id."""
    main = main_content(page)
    goto(page, f"{BASE_URL}/admin/learning")
    main.get_by_role("button", name="New Program").click()
    dialog = modal(page, "Create new program")
    dialog.locator("input[type=text]").fill(title)
    dialog.locator("textarea").fill(description)
    dialog.locator("input[type=number]").nth(0).fill(str(hours))
    dialog.locator("input[type=number]").nth(1).fill(str(days))
    dialog.get_by_role("button", name="Create program").click()
    expect(page.get_by_text("Create new program")).to_have_count(0, timeout=10000)
    search_programs(page, title)
    card = main.locator("article").filter(has_text=title).first
    expect(card).to_be_visible()
    href = card.locator("a", has_text="Open program").get_attribute("href")
    return href.rstrip("/").split("/")[-1]


def delete_program(page: Page, title):
    """Deletes every program matching the title (used as test cleanup)."""
    main = main_content(page)
    search_programs(page, title)
    cards = main.locator("article").filter(has_text=title)
    while cards.count() > 0:
        cards.first.locator("button[aria-label=Delete]").click(force=True)
        modal(page, "Delete Learning Program").get_by_role("button", name="Delete", exact=True).click()
        expect_toast(page, "Learning Program deleted successfully.")
        search_programs(page, title)
    expect(main.get_by_text("No programs found")).to_be_visible()


def cleanup_program(page: Page, title, program_id=None):
    """Unenrolls any learners (a program with learners can't be reverted/cleaned) and deletes it."""
    if program_id:
        unenroll_all(page, program_id)
    delete_program(page, title)


def program_url(program_id, tab=""):
    return f"{BASE_URL}/admin/learning/programs/{program_id}{tab}"


def settle(page: Page):
    # wait for the Vue app to hydrate, otherwise early clicks are lost; some
    # pages keep polling and never go fully idle, so cap the wait
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except PlaywrightTimeoutError:
        pass


def goto(page: Page, url):
    page.goto(url)
    settle(page)


def open_program(page: Page, program_id, tab=""):
    goto(page, program_url(program_id, tab))


def add_root_module(page: Page, program_id, title, hours="1", description=""):
    main = main_content(page)
    open_program(page, program_id, "/curriculum")
    main.get_by_role("button", name="Add Root Module").click()
    dialog = modal(page, "Add Module to Curriculum")
    dialog.locator("input[type=text]").fill(title)
    dialog.locator("textarea").fill(description)
    dialog.locator("input[type=number]").fill(str(hours))
    dialog.get_by_role("button", name="Save Node").click()
    expect_toast(page, "Learning Node created successfully.")
    expect(main.get_by_text(title, exact=True).first).to_be_visible()


def select_node(page: Page, title):
    main = main_content(page)
    main.get_by_text(title, exact=True).first.click()
    expect(main.get_by_role("button", name="+ Add Material")).to_be_visible()


def publish_program(page: Page, program_id):
    main = main_content(page)
    open_program(page, program_id, "?tab=settings")
    main.get_by_role("button", name="Publish Program").click()
    modal(page, "Publish Learning Program").get_by_role("button", name="Publish", exact=True).click()
    expect_toast(page, "Learning Program published successfully.")
    expect(main.get_by_role("button", name="Revert to Draft")).to_be_visible()


def open_enroll_dialog(page: Page, program_id):
    open_program(page, program_id, "/learners")
    main_content(page).get_by_role("button", name="Enroll Learner").click()
    return modal(page, "Enroll Learners in Program")


def enroll_learner(page: Page, program_id, name, email):
    dialog = open_enroll_dialog(page, program_id)
    dialog.get_by_placeholder("Search members...").fill(name)
    dialog.get_by_text(email).first.click()
    expect(dialog.get_by_text("Select Users (1 selected)")).to_be_visible()
    # close the member dropdown so it stops covering the submit button
    dialog.locator("form div.fixed.inset-0").first.click(position={"x": 5, "y": 5})
    dialog.get_by_role("button", name="Enroll Learners").click()


def unenroll_all(page: Page, program_id):
    main = main_content(page)
    open_program(page, program_id, "/learners")
    page.wait_for_timeout(1500)
    while main.get_by_role("button", name="Unenroll").count() > 0:
        main.get_by_role("button", name="Unenroll").first.click()
        modal(page, "Unenroll Learner").get_by_role("button", name="Unenroll", exact=True).click()
        expect_toast(page, "User unenrolled and progress cleared successfully.")
        page.wait_for_timeout(1500)


def open_submissions_review(page: Page):
    open_learning_submenu(page, "submissions-review")
    page.wait_for_url("**/admin/learning/submissions**")
    settle(page)


def submission_rows(page: Page):
    # the empty-state message is also rendered as a single table row
    return main_content(page).locator("tbody tr").filter(has=page.get_by_role("link", name="Grade / Review"))
