from playwright.sync_api import sync_playwright
from utils.ai_assistant_helper import open_ai_as_employee, api_headers, TRANSCRIBE_URL, AUDIO_REQUIRED


def test_transcribe_requires_audio_api():
    """AI-051: /ai/transcribe without an audio file returns 422 "The audio field is required."."""
    with sync_playwright() as p:
        browser, page = open_ai_as_employee(p)

        response = page.request.post(TRANSCRIBE_URL, multipart={}, headers=api_headers(page))

        assert response.status == 422
        assert response.json()["errors"]["audio"] == [AUDIO_REQUIRED]

        browser.close()
