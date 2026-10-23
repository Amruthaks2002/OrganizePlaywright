import re
import uuid
from urllib.parse import quote, unquote

from playwright.sync_api import Page, expect
from utils.learning_helper import (  # noqa: F401  (re-exported for the tests)
    BASE_URL, open_browser, main_content, expect_toast, settle, goto,
)

FORMS_URL = f"{BASE_URL}/forms"
CREATE_FORM_URL = f"{BASE_URL}/forms/create"
PROBATION_URL = f"{BASE_URL}/probation-reviews"
MY_SUBMISSIONS_URL = f"{BASE_URL}/my-submissions"
TEST_FORM_PREFIX = "QA Form"

QUESTION_TYPES = ["Short Answer", "Paragraph", "Multiple Choice", "Check Box", "Drop-down", "Date", "Time"]
TYPE_KEYS = {
    "Short Answer": "short_answer", "Paragraph": "long_answer", "Multiple Choice": "multiple_choice",
    "Check Box": "checkbox", "Drop-down": "dropdown", "Date": "date", "Time": "time",
}
CLOSED_MESSAGE = "is no longer accepting responses."


def unique_form_title(suffix=""):
    # random part so tests running in parallel never pick the same title
    title = f"{TEST_FORM_PREFIX} {uuid.uuid4().hex[:8]}"
    return f"{title} {suffix}" if suffix else title


# ---------- API (test setup and cleanup only) ----------

def api_headers(page: Page):
    # the meta csrf token goes stale after the SPA login, the XSRF cookie doesn't
    token = next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN")
    return {"X-XSRF-TOKEN": unquote(token), "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}


def question(text, type="short_answer", options=(), required=False):
    return {"id": str(uuid.uuid4()), "question": text, "type": type, "options": list(options),
            "validation": {"required": required}}


def create_form_api(page: Page, title, questions=None, type="general", description="", **settings):
    """Creates a form through the app's JSON endpoint and returns it (id, public_id, fields...)."""
    form_settings = {
        "is_anonymous": False, "allow_editing": False, "stop_on_date": False, "end_date": "", "end_time": "",
        "stop_on_limit": False, "max_responses": 40, "requires_subject": False,
    }
    form_settings.update(settings)
    response = page.request.post(FORMS_URL, headers=api_headers(page), data={
        "title": title, "description": description, "status": "active", "type": type,
        "questions": questions or [question("Question 1")], "settings": form_settings,
    })
    assert response.ok, f"creating form '{title}' failed: {response.status} {response.text()[:300]}"
    return response.json()["data"]


def toggle_status_api(page: Page, form_id):
    response = page.request.patch(f"{FORMS_URL}/{form_id}/toggle-status", data={},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"toggling form status failed: {response.status}"


def submit_response_api(page: Page, form, answers):
    """answers: {question label: answer}; check box answers are lists."""
    by_label = {f["label"]: f["id"] for f in form["fields"]}
    response = page.request.post(
        f"{BASE_URL}/submission/{form['public_id']}", headers=api_headers(page), max_redirects=0,
        data={"answers": [{"field_id": by_label[label], "answer": answer} for label, answer in answers.items()],
              "subject_id": None})
    assert response.status in (200, 302, 303), f"submitting a response failed: {response.status}"


def form_ids(page: Page, search):
    goto(page, f"{FORMS_URL}?search={quote(search)}")
    hrefs = main_content(page).locator("a[title='Preview Form']").evaluate_all("links => links.map(a => a.href)")
    return [h.rstrip("/").split("/")[-1] for h in hrefs]


def delete_forms(page: Page, search):
    """Deletes every form whose title matches the search, clones included (used as test cleanup)."""
    # the list is paged, so keep deleting the first page until nothing matches
    for _ in range(10):
        ids = form_ids(page, search)
        if not ids:
            return
        for form_id in ids:
            page.request.delete(f"{FORMS_URL}/{form_id}", headers=api_headers(page), max_redirects=0)
    assert form_ids(page, search) == [], f"forms matching '{search}' were not deleted"


# ---------- navigation ----------

def open_forms_submenu(page: Page, child):
    # the Forms group is already expanded when we're on one of its pages
    if not page.get_by_test_id(f"sidebar-child-{child}").is_visible():
        page.get_by_test_id("sidebar-parent-forms").click()
    page.get_by_test_id(f"sidebar-child-{child}").click()
    settle(page)


def open_my_forms(page: Page):
    open_forms_submenu(page, "my-forms")
    page.wait_for_url("**/forms")


def open_probation_reviews(page: Page):
    open_forms_submenu(page, "probation-reviews")
    page.wait_for_url("**/probation-reviews")


def open_create_form(page: Page):
    # a full page load, not the sidebar: right after login the SPA still holds the
    # pre-login CSRF token and the first save bounces to the Dashboard (app bug)
    goto(page, CREATE_FORM_URL)
    expect(title_input(page)).to_be_visible()


def open_my_submissions(page: Page):
    open_forms_submenu(page, "my-submissions")
    page.wait_for_url("**/my-submissions")


def submission_url(form):
    return f"{BASE_URL}/submission/{form['public_id']}"


def edit_url(form):
    return f"{FORMS_URL}/{form['id']}/edit"


def responses_url(form):
    return f"{FORMS_URL}/{form['id']}/responses"


# ---------- form list (My Forms / Probation Reviews) ----------

def search_input(page: Page):
    return main_content(page).get_by_placeholder("Search forms...")


def search_forms(page: Page, text):
    pattern = re.compile(r"search=" + re.escape(quote(text)).replace("%20", r"(%20|\+)") + r"(&|$)")
    for attempt in range(3):
        # some actions redirect to an unfiltered list but leave the old text in the box,
        # and typing before the page has hydrated is ignored, so clear and retype
        search_input(page).fill("")
        search_input(page).fill(text)
        try:
            expect(page).to_have_url(pattern, timeout=5000)
            break
        except AssertionError:
            if attempt == 2:
                raise
    settle(page)


def status_filter(page: Page):
    return main_content(page).locator("select").filter(has=page.locator("option[value=active]"))


def type_filter(page: Page):
    return main_content(page).locator("select").filter(has=page.locator("option[value=general]"))


def date_from(page: Page):
    return main_content(page).locator("input[type=date]").nth(0)


def date_to(page: Page):
    return main_content(page).locator("input[type=date]").nth(1)


def form_rows(page: Page):
    # the header row is "lg:grid grid-cols-12", data rows are "lg:grid-cols-12"
    return main_content(page).locator("div[class*='lg:grid-cols-12']").filter(has=page.locator("p.truncate"))


def form_row(page: Page, title):
    return form_rows(page).filter(has=page.locator("p.truncate").get_by_text(title, exact=True))


def row_titles(page: Page):
    return [t.strip() for t in form_rows(page).locator("p.truncate").all_inner_texts()]


def row_status_toggle(row):
    return row.locator("button.w-10.rounded-full")


def expect_row_active(row, active=True):
    expect(row_status_toggle(row)).to_have_class(re.compile("bg-green-500" if active else "bg-gray-300"))


def row_menu_action(row, action):
    row.get_by_role("button", name="⋮").click()
    row.locator(".action-menu").get_by_role("button", name=action).click()


def sort_header(page: Page, name):
    return main_content(page).locator("div.cursor-pointer").filter(has_text=re.compile(rf"^\s*{name}\s*$"))


def delete_dialog(page: Page):
    # the modal renders several overlay layers, so anchor on the heading's own panel
    return page.get_by_role("heading", name="Delete Form").locator("xpath=..")


def footer_summary(page: Page):
    return main_content(page).get_by_text(re.compile(r"Showing \d+ to \d+ of \d+ rows"))


def page_label(page: Page):
    return main_content(page).get_by_text(re.compile(r"^\s*Page \d+ / \d+\s*$"))


def pager_link(page: Page, name):
    return main_content(page).get_by_role("link", name=name, exact=True)


def expect_pager_disabled(link, disabled=True):
    if disabled:
        expect(link).to_have_class(re.compile("pointer-events-none"))
    else:
        expect(link).not_to_have_class(re.compile("pointer-events-none"))


# ---------- form builder (Create Form / Edit Form) ----------

def title_input(page: Page):
    return main_content(page).get_by_placeholder("Enter Form Title")


def description_editor(page: Page):
    return page.frame_locator("iframe.tox-edit-area__iframe").locator("body")


def open_title_editor(page: Page):
    # on the edit page the title/description card is collapsed until clicked
    if not title_input(page).is_visible():
        main_content(page).get_by_text("Click to edit").click()
    expect(title_input(page)).to_be_visible()


def header_button(page: Page, name):
    # Share/Settings/Preview are buttons, except Preview on a saved form, which is a link
    return main_content(page).locator("button, a").filter(
        has=page.locator("span", has_text=re.compile(rf"^\s*{name}\s*$")))


def anonymous_button(page: Page):
    return main_content(page).get_by_title("Toggle Anonymity")


def save_button(page: Page):
    return main_content(page).get_by_role("button", name="Save Form")


def question_cards(page: Page):
    return main_content(page).locator("div[data-draggable] > div.rounded-xl")


def question_input(card):
    return card.get_by_placeholder("Enter question")


def type_button(card):
    return card.locator("div.relative.w-full > button")


def type_menu(card):
    return card.locator("div.absolute.z-50")


def set_question_type(card, type_name):
    type_button(card).click()
    type_menu(card).get_by_role("button", name=type_name, exact=True).click()
    expect(type_button(card)).to_have_text(re.compile(rf"^\s*{re.escape(type_name)}\s*$"))


def option_inputs(card):
    return card.get_by_placeholder("Add the option here")


def required_toggle(card):
    return card.get_by_text("Is Required").locator("xpath=following-sibling::button")


def expect_toggle_on(toggle, on=True):
    if on:
        expect(toggle).to_have_class(re.compile("bg-emerald-500"))
    else:
        expect(toggle).not_to_have_class(re.compile("bg-emerald-500"))


def add_field_buttons(page: Page):
    # first one sits under the description, then one after every question card
    return main_content(page).get_by_title("Add Field")


def add_question(page: Page):
    count = question_cards(page).count()
    add_field_buttons(page).last.click()
    expect(question_cards(page)).to_have_count(count + 1)
    return question_cards(page).last


def fill_question(card, text, type_name="Short Answer", options=(), required=False):
    question_input(card).fill(text)
    if type_name != "Short Answer":
        set_question_type(card, type_name)
    for i, option in enumerate(options):
        if i >= option_inputs(card).count():
            card.get_by_role("button", name="Add Option").click()
        option_inputs(card).nth(i).fill(option)
    if required:
        required_toggle(card).click()
        expect_toggle_on(required_toggle(card))


def build_form(page: Page, title, questions=(("Question 1", "Short Answer", (), False),)):
    """Fills the builder: questions are (text, type, options, required)."""
    open_title_editor(page)
    title_input(page).fill(title)
    for i, (text, type_name, options, required) in enumerate(questions):
        card = question_cards(page).nth(i) if i < question_cards(page).count() else add_question(page)
        fill_question(card, text, type_name, options, required)


def save_new_form(page: Page):
    """Clicks Save Form on the create page and returns the created form."""
    # closing Settings with ✕ already creates the form (app bug), after which Save Form
    # updates it with a PUT instead of creating it with a POST
    def saved(r):
        return r.status == 200 and (
            (r.request.method == "POST" and r.url.rstrip("/") == FORMS_URL)
            or (r.request.method == "PUT" and r.url.startswith(f"{FORMS_URL}/")))

    with page.expect_response(saved) as info:
        save_button(page).click()
    expect_toast(page, "Form saved successfully.")
    return info.value.json()["data"]


def success_dialog(page: Page):
    return page.locator("div.modal-surface").filter(has=page.get_by_role("heading", name="Form Created Successfully"))


def share_dialog(page: Page):
    # the share link dialog (shown after saving and by the Share button)
    return page.locator("div.modal-surface").filter(has=page.get_by_text("Anonymous responses"))


def dialog_setting(dialog, label):
    return dialog.get_by_text(label, exact=True).locator("xpath=../following-sibling::div")


def settings_panel(page: Page):
    return page.get_by_role("heading", name="Form Settings").locator("xpath=../..")


def open_settings(page: Page):
    header_button(page, "Settings").click()
    panel = settings_panel(page)
    expect(panel).to_be_visible()
    return panel


def settings_toggle(panel, label):
    return panel.get_by_text(label, exact=True).locator("xpath=following-sibling::button")


def form_type_select(panel):
    return panel.locator("select")


# ---------- public submission page ----------

def public_form(page: Page):
    return page.locator("form").filter(has=page.get_by_role("button", name="Clear Form"))


def public_question(page: Page, text):
    return public_form(page).locator("> div").filter(has=page.locator("h3", has_text=text))


def answer_input(page: Page, text):
    return public_question(page, text).locator("input[type=text], textarea")


def choose_dropdown(page: Page, text, option):
    public_question(page, text).locator(".v-select").click()
    page.get_by_role("option", name=option, exact=True).click()


def submit_button(page: Page):
    return public_form(page).locator("button[type=submit]")


def closed_page(page: Page, title):
    return page.get_by_text(f'The form "{title}" {CLOSED_MESSAGE}')


def thank_you(page: Page):
    return page.get_by_text("Your response has been recorded. Thank you for your time!")


# ---------- responses page ----------

def view_tab(page: Page, name):
    return main_content(page).get_by_role("button", name=name, exact=True)


def responders_select(page: Page):
    return main_content(page).locator(".v-select").nth(0)


def question_select(page: Page):
    return main_content(page).locator(".v-select").nth(1)


def pick_option(page: Page, select, option):
    # a pick made before the page has hydrated is lost, so check it stuck and retry
    for attempt in range(3):
        select.click()
        page.get_by_role("option", name=re.compile(re.escape(option))).first.click()
        try:
            expect(select.locator(".vs__selected")).to_contain_text(option, timeout=3000)
            return
        except AssertionError:
            if attempt == 2:
                raise


def analytics_card(page: Page, text):
    return main_content(page).locator("h3").filter(has_text=re.compile(rf"^\s*{re.escape(text)}\s*$")).locator("xpath=../..")


def responder_answer(page: Page, text):
    # with one responder picked, each question is an h4 followed by that person's answer
    return main_content(page).locator("h4").filter(has_text=re.compile(rf"^\s*{re.escape(text)}\s*$")).locator("xpath=..")


def responses_table(page: Page):
    return main_content(page).locator("table")


def table_rows(page: Page):
    return [[c.strip() for c in row.locator("td").all_inner_texts()] for row in responses_table(page).locator("tbody tr").all()]


# ---------- my submissions ----------

def submission_rows(page: Page):
    return main_content(page).locator("div[class*='sm:grid-cols-12']").filter(has=page.locator("p.truncate"))


def submission_row(page: Page, title):
    return submission_rows(page).filter(has=page.locator("p.truncate").get_by_text(title))
