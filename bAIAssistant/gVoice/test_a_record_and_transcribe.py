import re

from playwright.sync_api import sync_playwright, expect
from utils.ai_assistant_helper import (open_ai_as_employee, mic_button, recording_label, textarea,
                                       TRANSCRIBING_PLACEHOLDER, TRANSCRIBE_URL, REPLY_TIMEOUT, VOICE_FILE)


def test_record_and_transcribe():
    """AI-048: The mic records with a running timer; stopping it shows "Transcribing your voice..." with the
    textarea disabled, then the transcript lands in the textarea (not sent yet)."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p, fake_mic_file=VOICE_FILE)

        mic_button(page).click()
        expect(recording_label(page)).to_be_visible()
        expect(recording_label(page)).to_contain_text("00:00")
        expect(recording_label(page)).to_contain_text("00:03", timeout=6000)

        with page.expect_response(TRANSCRIBE_URL, timeout=REPLY_TIMEOUT) as response_info:
            mic_button(page).click()
            expect(textarea(page)).to_have_attribute("placeholder", TRANSCRIBING_PLACEHOLDER)
            expect(textarea(page)).to_be_disabled()
        assert response_info.value.status == 200

        expect(textarea(page)).to_be_enabled()
        expect(textarea(page)).to_have_value(re.compile(r"leave", re.I))

        browser.close()
