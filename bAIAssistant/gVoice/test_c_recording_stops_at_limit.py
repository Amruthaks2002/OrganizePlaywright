import time

from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import (open_ai_as_employee, mic_button, recording_label, TRANSCRIBE_URL,
                                       RECORDING_LIMIT_SECONDS, VOICE_FILE)


def test_recording_stops_at_limit():
    """AI-050: A recording that isn't stopped stops by itself after 60 seconds and is sent for transcription."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p, fake_mic_file=VOICE_FILE)

        with page.expect_request(TRANSCRIBE_URL, timeout=(RECORDING_LIMIT_SECONDS + 15) * 1000):
            mic_button(page).click()
            started = time.monotonic()
            expect(recording_label(page)).to_be_visible()
            expect(recording_label(page)).to_have_count(0, timeout=(RECORDING_LIMIT_SECONDS + 10) * 1000)
        elapsed = time.monotonic() - started

        assert RECORDING_LIMIT_SECONDS - 2 <= elapsed <= RECORDING_LIMIT_SECONDS + 5, f"stopped after {elapsed:.1f}s"

        browser.close()
