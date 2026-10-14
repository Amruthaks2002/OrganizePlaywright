import re
from datetime import datetime
from urllib.parse import unquote

from playwright.sync_api import Page, expect
from utils.app_usage_helper import (BASE_URL, open_browser, open_browser_as, expect_forbidden, main_content,  # noqa: F401
                                    load, page_props, reload_props, heading, query_params, wait_for_visit,
                                    APP_RELEASES_URL, APP_USAGE_URL)
from utils.learning_helper import expect_toast  # noqa: F401  (re-exported for the tests)
from utils.onboarding_helper import unique_tag  # noqa: F401  (re-exported for the tests)

SIDEBAR_LINK = "sidebar-navlink-app releases"
PLATFORMS = {"android": "Android", "ios": "iOS"}
FIELDS = ("latest_version", "min_version", "optional_message", "mandatory_message")
HISTORY_COLUMNS = ["Published", "Platform", "Latest", "Minimum", "Release notes", "By", "Actions"]
RELEASES_PER_PAGE = 20
SUBTITLE = ("Installs below the minimum must update. "
            "Installs between the minimum and the latest are offered an update.")
VERSION_FORMAT = "Use a version like 1.4.0."
# The tests that save publish / edit Android: it has fewer real installs on QC, and they keep its latest version
# (and a minimum at or below it), so no real install is blocked or offered an update while a test runs.
TEST_PLATFORM = "android"


# ---------- server data / restoring ----------

def api_headers(page: Page):
    # the meta csrf token goes stale after the SPA login, the XSRF cookie doesn't
    token = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    return {"X-XSRF-TOKEN": token, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}


def api(page: Page, method, url, data):
    return page.request.fetch(url, method=method, data=data, headers=api_headers(page), max_redirects=0)


def values(release):
    """The four editable fields of a release (None messages as '', the way the form shows them)."""
    return {k: (release or {}).get(k) or "" for k in FIELDS}


def open_releases(page: Page, url=APP_RELEASES_URL):
    """Full load of App Releases, waiting until the publish form has been filled with the current release (typing
    before that gets overwritten)."""
    response = load(page, url)
    expect(page.locator("#latest_version")).not_to_have_value("")
    return response


def current_releases(page: Page):
    open_releases(page)
    return page_props(page)["current"]


def history_total(page: Page):
    load(page, APP_RELEASES_URL)
    return page_props(page)["history"]["total"]


def restore_releases(page: Page, snapshot):
    """Puts each platform's current release back to the snapshot's values with an in-place edit (no history row is
    added). Releases can't be deleted, so rows a test published stay, and the Published date is the newest row's."""
    current = current_releases(page)
    for platform, release in snapshot.items():
        if release and values(current[platform]) != values(release):
            for attempt in range(3):  # QC's nginx sometimes answers 502; don't leave a test's values live
                response = api(page, "PUT", f"{APP_RELEASES_URL}/{current[platform]['id']}",
                               {k: release[k] for k in FIELDS})
                if response.status < 500:
                    break
                page.wait_for_timeout(3000)
            assert response.status in (302, 303), (platform, response.status, response.text()[:300])
    restored = current_releases(page)
    for platform, release in snapshot.items():
        assert values(restored[platform]) == values(release), (platform, restored[platform], release)


def admin_name(page: Page):
    return page_props(page)["auth"]["user"]["name"]


# ---------- versions / dates ----------

def version_tuple(v):
    return tuple(int(x) for x in v.split("."))


def bump(v):
    """1.2.4 -> 1.2.5"""
    parts = v.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def lower(v):
    """1.2.4 -> 1.2.3, 2.1.0 -> 2.0.0"""
    parts = [int(x) for x in v.split(".")]
    i = max(n for n, x in enumerate(parts) if x > 0)
    parts[i] -= 1
    return ".".join(map(str, parts))


def raised_min(release):
    """A higher minimum that's still at or below the latest, so no install on the latest version gets blocked."""
    new = bump(release["min_version"])
    return new if version_tuple(new) <= version_tuple(release["latest_version"]) else release["latest_version"]


def published_text(iso):
    """'2026-10-07T11:45:44+00:00' -> '7 Oct, 2026, 05:15 PM' in the browser's (this machine's) time zone."""
    d = datetime.fromisoformat(iso).astimezone()
    return f"{d.day} {d:%b, %Y, %I:%M %p}"


# ---------- page parts ----------

def card(page: Page, platform):
    return main_content(page).locator("section").filter(
        has=page.locator("h2", has_text=re.compile(rf"^\s*{PLATFORMS[platform]}\s*$", re.I)))


def card_values(page: Page, platform):
    c = card(page, platform)
    return {"latest": c.locator("dd").nth(0).inner_text().strip(),
            "min": c.locator("dd").nth(1).inner_text().strip(),
            "published": " ".join(c.locator("p").last.inner_text().split())}


def form(page: Page):
    return main_content(page).locator("form")


def form_section(page: Page):
    return main_content(page).locator("section").filter(has=page.locator("form"))


def form_heading(page: Page):
    return form_section(page).locator("h2").first


def platform_radio(page: Page, platform):
    return form(page).locator(f"input[name=platform][value={platform}]")


def field(page: Page, name):
    return form(page).locator(f"#{name}")


def field_error(page: Page, name):
    return field(page, name).locator("xpath=..").get_by_test_id("input-error-message")


def form_values(page: Page):
    return {k: field(page, k).input_value() for k in FIELDS}


def fill_form(page: Page, platform=None, **fields):
    if platform:
        platform_radio(page, platform).check()
    for name, value in fields.items():
        field(page, name).fill(value)


def publish_button(page: Page):
    return form(page).get_by_role("button", name="Publish release")


def save_button(page: Page):
    return form(page).get_by_role("button", name="Save changes")


def cancel_edit_button(page: Page):
    return form_section(page).get_by_role("button", name="Cancel", exact=True).first


def confirm_dialog(page: Page):
    # dialogs render several copies in the DOM; only the open one is visible
    return page.locator("[data-testid=confirm-dialog]:visible")


def dialog_title(page: Page):
    return confirm_dialog(page).locator("#confirm-dialog-title")


def dialog_message(page: Page):
    return confirm_dialog(page).locator("#confirm-dialog-message")


def dialog_buttons(page: Page):
    return [t.strip() for t in confirm_dialog(page).get_by_role("button").all_inner_texts() if t.strip()]


def is_release_request(request):
    return request.url.startswith(APP_RELEASES_URL) and request.method in ("POST", "PUT")


def is_save_finished(request):
    """The last request of a publish / save: the POST or PUT itself, or the page it redirects back to."""
    first = request
    while first.redirected_from:
        first = first.redirected_from
    return is_release_request(first) and request.redirected_to is None


def submit(page: Page, button, confirm=None):
    """Clicks Publish release / Save changes and confirms the dialog (by default whatever its confirm button says)."""
    button.click()
    expect(confirm_dialog(page)).to_be_visible()
    confirm_button = (confirm_dialog(page).get_by_role("button", name=confirm, exact=True) if confirm
                      else confirm_dialog(page).get_by_role("button").last)
    with page.expect_request_finished(is_save_finished, timeout=15000):
        confirm_button.click()
    page.wait_for_timeout(500)  # let Vue re-render with the new props / errors


def submit_expecting_error(page: Page, button, name, message, platform=None, prepare=None, **fields):
    """Fills the form, submits it (Publish release / Save changes, confirmed) and expects `message` under `name`.
    `prepare` runs before each attempt (e.g. opening edit mode).

    App race: for ~15s after a page load the app keeps downloading its page chunks, and sometimes (about 1 in 4 fresh
    sessions) the refused save comes back with the form reset to the current release and no error shown. Nothing is
    saved either way. When that happens the same values are submitted once more."""
    for attempt in range(2):
        if prepare:
            prepare()
        fill_form(page, platform, **fields)
        submit(page, button)
        reset = all(field(page, k).input_value() != v for k, v in fields.items()) and \
            form(page).get_by_test_id("input-error-message").count() == 0
        if not reset:
            break
        print(f"form was reset after a refused save (app race), resubmitting: {fields}")
    expect(field_error(page, name)).to_have_text(message)


def publish(page: Page, platform=None, **fields):
    fill_form(page, platform, **fields)
    submit(page, publish_button(page))


def open_edit_from_card(page: Page, platform):
    card(page, platform).get_by_role("button", name="Edit").click()
    expect(form_heading(page)).to_have_text(re.compile(rf"Edit current {PLATFORMS[platform]} release", re.I))


# ---------- history ----------

def history_section(page: Page):
    return main_content(page).locator("section").filter(
        has=page.locator("h2", has_text=re.compile(r"^\s*History\s*$", re.I)))


def history_select(page: Page):
    return history_section(page).locator("select")


def filter_history(page: Page, value):
    wait_for_visit(page, lambda: history_select(page).select_option(value), APP_RELEASES_URL)


def history_rows(page: Page):
    rows = []
    for tr in history_section(page).locator("table tbody tr").all():
        cells = tr.locator("td")
        if cells.count() < 7:
            continue  # an empty-state row
        notes = cells.nth(4).locator("p")
        rows.append({
            "row": tr,
            "published": cells.nth(0).evaluate("e => e.firstChild.textContent.trim()"),
            "badges": [t.strip() for t in cells.nth(0).locator("span.rounded-full").all_inner_texts()],
            "platform": cells.nth(1).inner_text().strip(),
            "latest": cells.nth(2).inner_text().strip(),
            "min": cells.nth(3).inner_text().strip(),
            "optional": re.sub(r"^Optional:\s*", "", notes.nth(0).inner_text().strip()),
            "mandatory": re.sub(r"^Mandatory:\s*", "", notes.nth(1).inner_text().strip()),
            "by": cells.nth(5).inner_text().strip(),
            "has_notes": cells.nth(4).get_by_role("button", name="View release notes").count() > 0,
            "has_edit": cells.nth(6).get_by_role("button", name="Edit").count() > 0,
        })
    return rows


def expected_row(release, current_ids):
    """What a history row should show for a release from the server data."""
    return {
        "published": published_text(release["created_at"]),
        "badges": (["Current"] if release["id"] in current_ids else []) + (["Edited"] if release["edited"] else []),
        "platform": PLATFORMS[release["platform"]],
        "latest": release["latest_version"],
        "min": release["min_version"],
        "optional": release["optional_message"] or "Default",
        "mandatory": release["mandatory_message"] or "Default",
        "by": release["created_by"],
        "has_notes": bool(release["optional_message"] or release["mandatory_message"]),
        "has_edit": release["id"] in current_ids,
    }


def visible_row(row):
    return {k: v for k, v in row.items() if k != "row"}


def current_ids(props):
    return {r["id"] for r in props["current"].values() if r}


# ---------- release notes dialog ----------

def notes_dialog(page: Page):
    return page.locator("div.fixed.inset-0:visible").filter(has_text="Mandatory update message").last


def open_notes(row):
    row["row"].get_by_role("button", name="View release notes").click()


def assert_nothing_saved(page: Page, snapshot, total):
    """The current releases and the History total are what they were before the test."""
    load(page, APP_RELEASES_URL)
    props = page_props(page)
    assert props["current"] == snapshot, props["current"]
    assert props["history"]["total"] == total, (props["history"]["total"], total)


def all_history(page: Page, platform=None):
    """Every release in History (all pages), newest first, from the server data."""
    query = f"platform={platform}&" if platform else ""
    open_releases(page, f"{APP_RELEASES_URL}?{query}page=1")
    history = page_props(page)["history"]
    data = list(history["data"])
    for n in range(2, history["last_page"] + 1):
        open_releases(page, f"{APP_RELEASES_URL}?{query}page={n}")
        data += page_props(page)["history"]["data"]
    return data


def page_link(page: Page, number):
    # the pager renders a phone, a tablet and a desktop layout; at 1600px only the desktop one (page numbers and
    # unlabelled arrows) is visible
    return history_section(page).locator("a:visible").filter(has_text=re.compile(rf"^\s*{number}\s*$")).first


def current_row(page: Page, platform):
    """A platform's Current row. Opens History filtered to that platform, where it's always the top row (unfiltered,
    it can be on page 2 once the other platform has 20 newer releases)."""
    open_releases(page, f"{APP_RELEASES_URL}?platform={platform}")
    row = history_rows(page)[0]
    assert "Current" in row["badges"], (platform, visible_row(row))
    return row
