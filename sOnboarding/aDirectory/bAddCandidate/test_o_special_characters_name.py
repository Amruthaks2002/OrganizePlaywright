from playwright.sync_api import sync_playwright, expect
from utils.onboarding_helper import (
    open_browser, create_candidate, new_candidate_data, open_directory, candidate_row, open_review,
    main_content, delete_candidates, unique_tag,
)


def test_special_characters_name():
    """OD-033: a name with apostrophes, hyphens, accents and non-Latin letters is saved and shown as typed."""
    with sync_playwright() as p:
        browser, page = open_browser(p)
        tag = unique_tag()
        data = {**new_candidate_data(tag), "name": f"QA Candidate {tag} D'Souza-Ñúñez 李"}
        try:
            candidate_id = create_candidate(page, **data)
            open_directory(page, search=tag)
            expect(candidate_row(page, data["name"])).to_have_count(1)

            open_review(page, candidate_id)
            expect(main_content(page).get_by_role("heading", name=data["name"])).to_be_visible()
        finally:
            delete_candidates(page, tag)

        browser.close()
