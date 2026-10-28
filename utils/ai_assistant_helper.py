import os
import re
from datetime import date, timedelta
from urllib.parse import unquote

from playwright.sync_api import Page, expect
from utils.app_usage_helper import page_props
from utils.learning_helper import BASE_URL, main_content  # noqa: F401  (re-exported for the tests)
from utils.onboarding_helper import open_browser_as, unique_tag  # noqa: F401  (re-exported for the tests)

AI_URL = f"{BASE_URL}/ai"
SEND_URL = f"{BASE_URL}/ai/send"
TRANSCRIBE_URL = f"{BASE_URL}/ai/transcribe"
WELCOME_API_URL = f"{BASE_URL}/api/ai/welcome-message"
LEAVE_DASHBOARD_URL = f"{BASE_URL}/leave/dashboard"
SIDEBAR_LINK = "sidebar-navlink-ai assistant"

# The employee-side account the user gave for AI Assistant tests only - don't use it anywhere else.
EMPLOYEE_EMAIL = "swathi@iocod.com"
EMPLOYEE_PASSWORD = "password"
EMPLOYEE_NAME = "Swathi"

PLACEHOLDER = "Ask your AI Assistant..."
TRANSCRIBING_PLACEHOLDER = "Transcribing your voice..."
DISCLAIMER = "AI Assistant can make mistakes. Check important info."
ERROR_REPLY = "Something went wrong. Please try again."
OUT_OF_SCOPE_REPLY = "i can only assist you with hr-related queries"
QUICK_ACTIONS = ["Apply Leave", "Leave Balance", "My Leaves"]
BALANCE_COLUMNS = ["Leave Type", "Total", "Taken", "Remaining"]
MAX_MESSAGE_LENGTH = 5000
MESSAGE_REQUIRED = "The message field is required."
MESSAGE_TOO_LONG = "The message field must not be greater than 5000 characters."
CONVERSATION_ID_INVALID = "The conversation id field must be a valid UUID."
AUDIO_REQUIRED = "The audio field is required."
RECORDING_LIMIT_SECONDS = 60
# a WAV of "What is my current leave balance?" (made with macOS `say`), played by Chromium as the microphone
VOICE_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bAIAssistant", "gVoice", "leave_balance.wav")

# AI replies regularly take 10-30s, sometimes more
REPLY_TIMEOUT = 120000
TIME_LABEL = re.compile(r"^\d{2}:\d{2} (AM|PM)$")


# ---------- browser / login ----------

def launch(p, fake_mic_file=None):
    args = []
    if fake_mic_file:
        # Chromium plays this WAV as the microphone and auto-accepts the permission prompt
        args = ["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream",
                f"--use-file-for-fake-audio-capture={fake_mic_file}"]
    browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "1", args=args)
    context = browser.new_context(viewport={"width": 1600, "height": 900})
    return browser, context.new_page()


def login_employee(page: Page):
    page.goto(BASE_URL)
    page.fill("#email", EMPLOYEE_EMAIL)
    page.fill("#password", EMPLOYEE_PASSWORD)
    page.click("[data-testid='sign-in-button']")
    page.wait_for_url("**/dashboard**")


def refresh_session(page: Page):
    # Known bug (AI-063): after signing in, the SPA keeps the guest csrf-token meta, so the first /ai/send
    # gets 419 "CSRF token mismatch" until a full page load. The other tests reload so they still run.
    page.reload()
    page.wait_for_url("**/dashboard**")


def open_ai(page: Page):
    page.get_by_test_id(SIDEBAR_LINK).click()
    page.wait_for_url(AI_URL)
    expect_welcome_loaded(page)


def open_ai_as_employee(p, fake_mic_file=None):
    """Signs in as the employee-side AI test account and opens the AI Assistant from the sidebar."""
    browser, page = launch(p, fake_mic_file)
    login_employee(page)
    refresh_session(page)
    open_ai(page)
    return browser, page


def open_ai_as(p, role):
    """Dev quick-login as admin / hr / team-lead / project-manager and open the AI Assistant."""
    browser, page = open_browser_as(p, role)
    refresh_session(page)
    open_ai(page)
    return browser, page


# ---------- page parts ----------

def textarea(page: Page):
    return main_content(page).locator("textarea")


def input_bar(page: Page):
    # the textarea is swapped for a "Recording..." label while recording, the two buttons stay
    return main_content(page).locator("div:has(> button svg[class*='lucide-arrow-up'])").last


def mic_button(page: Page):
    return input_bar(page).locator("button").first


def send_button(page: Page):
    return input_bar(page).locator("button").last


def recording_label(page: Page):
    return main_content(page).get_by_text(re.compile(r"Recording\.\.\. \d{2}:\d{2}"))


def quick_action(page: Page, label):
    return main_content(page).get_by_role("button", name=label, exact=True)


def replies(page: Page):
    """The AI replies, oldest first (the welcome card isn't one)."""
    return main_content(page).locator(".assistant-content")


def user_messages(page: Page):
    """The text of each message the user sent, oldest first."""
    return main_content(page).locator("div.bg-blue-100 .break-words")


def user_message_times(page: Page):
    return main_content(page).locator("div.items-end").filter(has=page.get_by_text("You", exact=True)) \
        .locator("span.text-xs")


def typing_indicator(page: Page):
    return main_content(page).locator("span.animate-bounce").first


def copy_buttons(page: Page):
    return main_content(page).get_by_title("Copy Text")


def expect_welcome_loaded(page: Page):
    expect(quick_action(page, QUICK_ACTIONS[0])).to_be_visible(timeout=15000)


# ---------- chatting ----------

def wait_for_reply(page: Page, previous_count):
    expect(replies(page)).to_have_count(previous_count + 1, timeout=REPLY_TIMEOUT)
    expect(typing_indicator(page)).to_have_count(0)
    return replies(page).last


def ask(page: Page, message):
    """Types a message, sends it with Enter and returns (the new reply, the /ai/send response) -
    response.request.post_data_json is what the page sent, response.json() what the server answered."""
    before = replies(page).count()
    textarea(page).fill(message)
    with page.expect_response(SEND_URL, timeout=REPLY_TIMEOUT) as response_info:
        textarea(page).press("Enter")
    return wait_for_reply(page, before), response_info.value


def click_quick_action(page: Page, label):
    before = replies(page).count()
    with page.expect_response(SEND_URL, timeout=REPLY_TIMEOUT) as response_info:
        quick_action(page, label).click()
    return wait_for_reply(page, before), response_info.value


def sent_message(response):
    return response.request.post_data_json["message"]


def reply_text(reply):
    return reply.inner_text().strip()


def table_headers(reply):
    # the headers are text-transformed to upper case, so read the DOM text rather than inner_text
    return [h.strip() for h in reply.locator("table").first.locator("thead th").all_text_contents()]


def table_rows(reply):
    """The first table of a reply as a list of {header: cell} dicts (headers as written, e.g. 'Leave Type')."""
    headers = table_headers(reply)
    return [dict(zip(headers, [c.strip() for c in row.locator("td").all_text_contents()]))
            for row in reply.locator("table").first.locator("tbody tr").all()]


def balance_table(reply):
    """{leave type: (total, taken, remaining)} from a leave balance reply."""
    return {row["Leave Type"]: tuple(float(row[c]) for c in BALANCE_COLUMNS[1:]) for row in table_rows(reply)}


def normalise_leave_type(name):
    """'Planned Leave' / 'planned' / 'Special Holiday Leave' -> 'planned' / 'special holiday'."""
    return re.sub(r"\s+leave$", "", name.strip().lower())


# ---------- API ----------

def api_headers(page: Page):
    # the meta csrf token goes stale after the SPA login, the XSRF cookie doesn't
    token = unquote(next(c["value"] for c in page.context.cookies() if c["name"] == "XSRF-TOKEN"))
    return {"X-XSRF-TOKEN": token, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"}


def api_send(page: Page, data):
    return page.request.post(SEND_URL, data=data, headers=api_headers(page), timeout=REPLY_TIMEOUT)


# ---------- leave data (the AI test account's own) ----------

def leave_dashboard(page: Page):
    """Props of the employee's Leave Dashboard, read in a separate tab so the chat keeps its conversation."""
    tab = page.context.new_page()
    try:
        tab.goto(LEAVE_DASHBOARD_URL)
        return page_props(tab)
    finally:
        tab.close()


def leave_balance_cards(page: Page):
    """{normalised leave type: available} from the Leave Dashboard cards."""
    return {normalise_leave_type(c["title"]): float(c["available"]) for c in leave_dashboard(page)["leaveBalanceCards"]}


def leave_request_ids(page: Page):
    return {r["id"] for r in leave_dashboard(page)["leaveRequests"]["data"]}


def leave_requests(page: Page):
    """The newest page (7) of leave requests - enough to spot ones a test just created, not the full history."""
    return leave_dashboard(page)["leaveRequests"]["data"]


def approved_leave_dates(page: Page):
    """Start dates of all the employee's approved leaves (the calendar highlights aren't paginated)."""
    return sorted(date.fromisoformat(h["start"]) for h in leave_dashboard(page)["highlightedDates"]
                  if h.get("application_id") and h.get("class") == "approved")


def future_working_days(page: Page, count, days_ahead=45):
    """`count` consecutive Mon-Fri dates starting at least `days_ahead` days out, with no holiday or existing
    (non-cancelled) leave on any of them - far enough ahead for every leave type's advance notice."""
    dashboard = leave_dashboard(page)
    taken = set()
    for item in dashboard["highlightedDates"]:
        if item.get("class") == "cancelled":
            continue
        start = date.fromisoformat(item["start"])
        end = date.fromisoformat(item["end"]) if item.get("end") else start
        taken.update(start + timedelta(days=i) for i in range((end - start).days + 1))
    day = date.today() + timedelta(days=days_ahead)
    while True:
        days = [day + timedelta(days=i) for i in range(count)]
        if all(d.isoweekday() < 6 and d not in taken for d in days):
            return days
        day += timedelta(days=1)


def spoken(day: date):
    return f"{day.day} {day:%B %Y}"


def shown_as(day: date):
    # the assistant writes dates like "08 Dec 2026"
    return re.compile(rf"\b0?{day.day} {day:%b} {day.year}\b")


CONFIRM_WORDS = re.compile(r"confirm|shall i|should i|proceed|go ahead|would you like me to", re.I)


def apply_leave_via_ai(page: Page, message, before_ids, tag):
    """Asks the assistant to apply a leave; if it asks for a confirmation first, says yes.
    Returns the last reply."""
    reply, _ = ask(page, message)
    if not new_leave_requests(page, before_ids, tag) and CONFIRM_WORDS.search(reply_text(reply)):
        reply, _ = ask(page, "Yes, please submit it.")
    return reply


QA_REASON = "QA automation"


def qa_reason(tag):
    """The leave reason the Apply Leave tests use. The tag is what tells one test's requests from another's, since
    the tests may run in parallel (pytest -n) on the same account."""
    return f"{QA_REASON} {tag}"


def new_leave_requests(page: Page, before_ids, tag=None):
    """Requests created since before_ids was taken: with a tag, only the ones whose reason carries it; without one,
    any except the tagged requests other (parallel) Apply Leave tests make."""
    created = [r for r in leave_requests(page) if r["id"] not in before_ids]
    if tag:
        return [r for r in created if tag in (r["reason"] or "")]
    return [r for r in created if QA_REASON not in (r["reason"] or "")]


def cancel_leave(page: Page, leave_id, reason="QA automation cleanup"):
    """Cancels a leave request the way the Leave Dashboard's Cancel Request dialog does."""
    response = page.request.fetch(f"{BASE_URL}/leave/{leave_id}/cancel", method="DELETE",
                                  data={"status": "cancel", "action_reason": reason},
                                  headers=api_headers(page), max_redirects=0)
    assert response.status in (200, 302, 303), f"cancelling leave {leave_id} failed: {response.status}"


def cancel_new_leaves(page: Page, before_ids, tag):
    """Cleanup for the Apply Leave tests: cancels the test's own pending requests (never another test's)."""
    for request in new_leave_requests(page, before_ids, tag):
        if request["status"] == "pending":
            cancel_leave(page, request["id"])
