import html
import json
import os
import re
import uuid
from urllib.parse import quote, unquote

from playwright.sync_api import Page, expect
from utils.learning_helper import BASE_URL, main_content, settle, goto  # noqa: F401  (re-exported)
from utils.login_helper import login
from utils.onboarding_helper import open_browser_as, login_as  # noqa: F401  (re-exported)

MARKETPLACE_URL = f"{BASE_URL}/marketplace"
CREATE_URL = f"{MARKETPLACE_URL}/create"
REVIEW_URL = f"{MARKETPLACE_URL}/review"
TRENDS_URL = f"{MARKETPLACE_URL}/trends"

QA_PREFIX = "QA App"
PAGE_SIZE = 12
NO_MATCH = "No apps match your filters."
SEARCH_PLACEHOLDER = "Search apps, tools and ideas…"
REJECT_PLACEHOLDER = "What needs to change?"
COMMENT_PLACEHOLDER = "Share your thoughts, feedback or a feature request…"
LIVE_WARNING = "This app is live in the marketplace."
REASON_REQUIRED = "Please tell the author why this submission is rejected."
DRAFT_SAVED = "Draft saved. Submit it for review when you are ready."

# value -> label, as the platform buttons and cards show them
PLATFORMS = {"web": "Website", "extension": "Browser extension", "plugin": "Plugin", "android": "Android app",
             "macos": "macOS app", "ios": "iPhone / iOS app", "idea": "Idea"}
CATEGORIES = ["Productivity", "Reporting", "Utilities", "HR tools", "Integrations", "Other"]
SORTS = {"latest": "Newest first", "downloads": "Most downloaded", "kudos": "Most kudos", "name": "Name A–Z"}
STATUS_LABELS = {"draft": "Draft", "submitted": "Pending review", "approved": "Approved", "rejected": "Rejected"}

FILES_DIR = os.path.join(os.path.dirname(__file__), "..", "dMarketplace", "files")
PACKAGE_ZIP = os.path.abspath(os.path.join(FILES_DIR, "qa_package.zip"))
SCREENSHOT_PNG = os.path.abspath(os.path.join(FILES_DIR, "qa_screenshot.png"))
NOT_A_PACKAGE = os.path.abspath(os.path.join(FILES_DIR, "qa_notes.txt"))


def open_browser(p):
    """Signs in as admin. Unlike the shared open_browser, native confirm() dialogs are NOT
    auto-accepted: use answer_next_dialog() before a click that opens one."""
    browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1")
    context = browser.new_context(viewport={"width": 1600, "height": 900}, accept_downloads=True)
    page = context.new_page()
    login(page)
    return browser, page


def unique_name(prefix=QA_PREFIX):
    # random suffix so parallel runs never find each other's apps
    return f"{prefix} {uuid.uuid4().hex[:6]}"


def slug_of(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def show_url(name):
    return f"{MARKETPLACE_URL}/{slug_of(name)}"


def answer_next_dialog(page: Page, accept=True):
    """Answers the next native confirm() and returns a list that receives its message."""
    messages = []

    def handle(dialog):
        messages.append(dialog.message)
        dialog.accept() if accept else dialog.dismiss()

    page.once("dialog", handle)
    return messages


def expect_toast(page: Page, message, timeout=10000):
    expect(page.locator("div.border-l-4.shadow-lg").filter(has_text=message).first).to_be_visible(timeout=timeout)


# ---------- server calls (setup, cleanup and endpoint checks) ----------

def api(page: Page, method, path, data=None):
    """Calls an endpoint with the page's session, the way the app's own requests do.
    Returns (status, json-or-None)."""
    xsrf = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    response = page.request.fetch(f"{BASE_URL}{path}", method=method, data=data, max_redirects=0, headers={
        "X-XSRF-TOKEN": xsrf, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"})
    try:
        return response.status, response.json()
    except Exception:
        return response.status, None


def page_props(page: Page, url):
    """The Inertia props a GET of `url` renders, read without navigating the page.
    Returns None when the page isn't 200."""
    response = page.request.get(url)
    if response.status != 200:
        return None
    text = response.text()
    start = text.find('data-page="') + len('data-page="')
    return json.loads(html.unescape(text[start:text.find('"', start)]))["props"]


def app_data(page: Page, name):
    """The app record the detail page renders (id, status, counts, history...), or None if gone."""
    props = page_props(page, show_url(name))
    return props["app"] if props else None


def app_payload(name, platform="web", category="Utilities", submit=True, **fields):
    delivery = "none" if platform == "idea" else "link"
    data = {"name": name, "short_description": "Created by the marketplace tests.", "description": "",
            "platform": platform, "delivery_type": delivery, "category": category, "tags": "",
            "external_url": "" if platform == "idea" else f"https://example.com/{slug_of(name)}",
            "package": None, "screenshots": [], "removed_screenshot_ids": [], "version": "",
            "min_os_version": "", "host_app": "VS Code" if platform == "plugin" else "",
            "submit_for_review": submit}
    data.update(fields)
    return data


def create_app(page: Page, name, platform="web", category="Utilities", submit=True, **fields):
    """Creates a link-delivered app (an Idea has no delivery) and returns its id.
    submit=False leaves it as a draft."""
    status, body = api(page, "POST", "/marketplace", app_payload(name, platform, category, submit, **fields))
    assert status == 302, f"create {name}: expected 302, got {status} {body}"
    return app_data(page, name)["id"]


def create_file_app(page: Page, name, platform="plugin", submit=True):
    """Creates an app delivered as an uploaded package (qa_package.zip) and returns its id."""
    xsrf = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    with open(PACKAGE_ZIP, "rb") as f:
        package = {"name": "qa_package.zip", "mimeType": "application/zip", "buffer": f.read()}
    response = page.request.post(f"{MARKETPLACE_URL}", max_redirects=0, headers={
        "X-XSRF-TOKEN": xsrf, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        multipart={"name": name, "short_description": "Created by the marketplace tests.", "platform": platform,
                   "delivery_type": "file", "category": "Utilities", "host_app": "VS Code",
                   "submit_for_review": "1" if submit else "0", "package": package})
    assert response.status == 302, f"create {name}: expected 302, got {response.status} {response.text()[:300]}"
    return app_data(page, name)["id"]


def approve_app(page: Page, app_id):
    status, body = api(page, "POST", f"/marketplace/{app_id}/approve")
    assert status == 302, f"approve {app_id}: expected 302, got {status} {body}"


def reject_app(page: Page, app_id, reason="Rejected by the marketplace tests."):
    status, body = api(page, "POST", f"/marketplace/{app_id}/reject", {"action_reason": reason})
    assert status == 302, f"reject {app_id}: expected 302, got {status} {body}"


def create_live_app(page: Page, name, **kwargs):
    """Creates an app and approves it as admin, so it's listed in the marketplace."""
    app_id = create_app(page, name, **kwargs)
    approve_app(page, app_id)
    return app_id


def give_kudos(page: Page, app_id):
    status, body = api(page, "POST", f"/marketplace/{app_id}/kudos")
    assert status == 302, f"kudos {app_id}: expected 302, got {status} {body}"


def post_comment(page: Page, app_id, text):
    status, body = api(page, "POST", f"/marketplace/{app_id}/comments", {"body": text})
    assert status == 302, f"comment on {app_id}: expected 302, got {status} {body}"


def download(page: Page, app_id):
    response = page.request.get(f"{MARKETPLACE_URL}/{app_id}/download")
    assert response.status == 200, f"download {app_id}: expected 200, got {response.status}"
    return response


def delete_apps(page: Page, *names):
    """Deletes the named apps if they still exist (test cleanup). `page` must be an admin."""
    for name in names:
        data = app_data(page, name)
        if data:
            status, body = api(page, "DELETE", f"/marketplace/{data['id']}")
            assert status in (302, 303), f"delete {name}: got {status} {body}"
        assert page.request.get(show_url(name)).status == 404, f"{name} still exists after cleanup"


def search_app_names(page: Page, search, mine=False):
    """Names the marketplace list returns for a search, across every page."""
    names, page_no = [], 1
    while True:
        props = page_props(page, list_url(search=search, mine=mine, page_no=page_no))
        names += [a["name"] for a in props["apps"]["data"]]
        if page_no >= props["apps"]["last_page"]:
            return names
        page_no += 1


# ---------- list ----------

def list_url(search="", category="", platform="", sort="", mine=False, page_no=None):
    params = {"search": search, "category": category, "platform": platform, "sort": sort,
              "mine": "1" if mine else "", "page": page_no or ""}
    query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items() if v)
    return f"{MARKETPLACE_URL}?{query}" if query else MARKETPLACE_URL


def open_marketplace(page: Page, **filters):
    goto(page, list_url(**filters))
    expect(main_content(page).get_by_role("heading", name="Application Marketplace")).to_be_visible()


def search_box(page: Page):
    return main_content(page).get_by_placeholder(SEARCH_PLACEHOLDER)


def category_select(page: Page):
    return main_content(page).locator("select").nth(0)


def sort_select(page: Page):
    return main_content(page).locator("select").nth(1)


def platform_chip(page: Page, label):
    return main_content(page).get_by_role("button", name=label, exact=True)


def mine_switch(page: Page):
    return main_content(page).get_by_role("switch", name="My submissions")


def clear_filters_button(page: Page):
    # the button carries a badge counting the active filters
    return main_content(page).get_by_role("button", name=re.compile(r"^\s*Clear filters"))


def result_count(page: Page):
    return main_content(page).get_by_text(re.compile(r"^\d+ results?$"))


def app_cards(page: Page):
    # each card is a link to the app's detail page, with the name in an h2
    return main_content(page).locator("a[href*='/marketplace/']").filter(has=page.locator("h2"))


def app_card(page: Page, name):
    return app_cards(page).filter(has=page.locator("h2", has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")))


def card_names(page: Page):
    return [t.strip() for t in app_cards(page).locator("h2").all_inner_texts()]


# ---------- create / edit form ----------

def open_create(page: Page):
    goto(page, CREATE_URL)
    expect(main_content(page).get_by_role("heading", name=re.compile("Add a new application"))).to_be_visible()


def pick_platform(page: Page, value):
    # each platform button holds its label plus a hint line, e.g. "Website" / "external URL"
    main_content(page).locator("button").filter(has=page.get_by_text(PLATFORMS[value], exact=True)).click()


def fill_description(page: Page, text):
    editor = page.locator(".html-editor-content")
    editor.click()
    page.keyboard.press("ControlOrMeta+a")
    page.keyboard.type(text)


def fill_form(page: Page, name=None, short=None, description=None, category=None, tags=None, url=None,
              version=None, host_app=None, min_os=None):
    if name is not None:
        page.locator("#name").fill(name)
    if short is not None:
        page.locator("#short_description").fill(short)
    if description is not None:
        fill_description(page, description)
    if category is not None:
        page.locator("#category").select_option(category)
    if tags is not None:
        page.locator("#tags").fill(tags)
    if url is not None:
        page.locator("#external_url").fill(url)
    if version is not None:
        page.locator("#version").fill(version)
    if host_app is not None:
        page.locator("#host_app").fill(host_app)
    if min_os is not None:
        page.locator("#min_os_version").fill(min_os)


def delivery_section(page: Page):
    return main_content(page).locator("div, section").filter(has_text=re.compile("^3 · DELIVERY")).last


def package_input(page: Page):
    return main_content(page).locator("input[type=file]:not([accept^='image'])")


def screenshot_input(page: Page):
    return main_content(page).locator("input[type=file][accept^='image']")


def field_error(page: Page, message):
    return main_content(page).get_by_text(message, exact=True)


def submit_for_review(page: Page):
    main_content(page).get_by_role("button", name="Submit for review").click()


def save_draft(page: Page):
    main_content(page).get_by_role("button", name="Save draft").click()


def submit_new_app(page: Page, name, platform="web", **fields):
    """Fills the create form with the essentials (plus `fields`) and submits it for review."""
    open_create(page)
    pick_platform(page, platform)
    fields.setdefault("short", "Created by the marketplace tests.")
    if platform != "idea":
        fields.setdefault("url", f"https://example.com/{slug_of(name)}")
    if platform == "plugin":
        fields.setdefault("host_app", "VS Code")
    fill_form(page, name=name, **fields)
    submit_for_review(page)
    expect_toast(page, f"{PLATFORMS[platform]} submitted for review.")
    page.wait_for_url(show_url(name))


# ---------- detail page ----------

def open_app(page: Page, name):
    goto(page, show_url(name))
    expect(main_content(page).get_by_role("heading", name=name, exact=True)).to_be_visible()


def status_badge(page: Page, status):
    return main_content(page).get_by_text(STATUS_LABELS[status], exact=True).first


def history(page: Page):
    """The history entries, newest first, e.g. ['Approved by Admin User', 'Submitted by Admin User']."""
    section = main_content(page).get_by_text("History", exact=True).locator("xpath=..")
    return [t.strip() for t in section.locator("p", has_text=re.compile(r" by ")).all_inner_texts()]


def stat(page: Page, label):
    """The number above 'Downloads' / 'Kudos' in the side panel."""
    value = main_content(page).get_by_text(label, exact=True).locator("xpath=preceding-sibling::*[1]")
    return int(value.inner_text().strip())


def comment_box(page: Page):
    return main_content(page).get_by_placeholder(COMMENT_PLACEHOLDER)


def post_comment_button(page: Page):
    return main_content(page).get_by_role("button", name="Post comment")


def comments(page: Page):
    return main_content(page).locator("li.group")


def comment(page: Page, text):
    return comments(page).filter(has=page.locator("p", has_text=re.compile(rf"^\s*{re.escape(text)}\s*$")))


def delete_comment_button(page: Page, text):
    item = comment(page, text)
    item.hover()
    return item.locator("button[title='Delete comment']")


def kudos_button(page: Page):
    return main_content(page).get_by_role("button", name=re.compile("^(Give kudos|Kudos given)$"))


def remove_app_ui(page: Page, name):
    """Removes the app from its detail page, accepting the confirm()."""
    open_app(page, name)
    messages = answer_next_dialog(page)
    main_content(page).get_by_role("button", name="Remove", exact=True).click()
    expect_toast(page, "removed from the marketplace.")
    assert messages == ["Remove this app from the marketplace? This cannot be undone."], messages


# ---------- review queue ----------

def open_review(page: Page):
    goto(page, REVIEW_URL)
    expect(main_content(page).get_by_role("heading", name="Review queue")).to_be_visible()


def review_card(page: Page, name):
    title = main_content(page).get_by_role("link", name=name, exact=True)
    return title.locator("xpath=ancestor::div[.//button[normalize-space()='Reject']][1]")


def reject_dialog(page: Page):
    return page.get_by_placeholder(REJECT_PLACEHOLDER).locator(
        "xpath=ancestor::div[.//button[normalize-space()='Reject submission']][1]")


def open_reject(page: Page, scope):
    scope.get_by_role("button", name="Reject", exact=True).click()
    dialog = reject_dialog(page)
    expect(dialog).to_be_visible()
    return dialog


# ---------- trends ----------

def open_trends(page: Page):
    goto(page, TRENDS_URL)
    expect(main_content(page).get_by_role("heading", name="Marketplace trends")).to_be_visible()


def trend_tile(page: Page, label):
    """The number on a stat tile, e.g. 'Pending review'."""
    value = main_content(page).get_by_text(label, exact=True).locator("xpath=following-sibling::p[1]")
    return int(value.inner_text().strip())


def trending_list(page: Page):
    heading = main_content(page).get_by_role("heading", name="Trending apps")
    return heading.locator("xpath=ancestor::div[.//ul or .//p[contains(., 'No activity')]][1]")


def trend_totals(page: Page):
    return page_props(page, TRENDS_URL)["trends"]["totals"]
