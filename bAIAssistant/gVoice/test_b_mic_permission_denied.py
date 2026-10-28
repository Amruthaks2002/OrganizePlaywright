from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import (launch, login_employee, refresh_session, open_ai, mic_button, recording_label,
                                       textarea, TRANSCRIBE_URL)

DENY_MIC = """navigator.mediaDevices.getUserMedia = () =>
    Promise.reject(new DOMException('Permission denied', 'NotAllowedError'));"""


def test_mic_permission_denied():
    """AI-049: When microphone access is denied, clicking the mic doesn't crash or get stuck recording -
    the textarea and mic keep working."""
    with sync_playwright() as p:
        browser, page = launch(p)
        page.add_init_script(DENY_MIC)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        login_employee(page)
        refresh_session(page)
        open_ai(page)
        transcribes = []
        page.on("request", lambda r: transcribes.append(r) if r.url == TRANSCRIBE_URL else None)

        mic_button(page).click()
        page.wait_for_timeout(1500)

        expect(recording_label(page)).to_have_count(0)
        expect(textarea(page)).to_be_editable()
        expect(mic_button(page)).to_be_enabled()
        assert not transcribes
        assert not errors, f"page errors: {errors}"

        browser.close()
