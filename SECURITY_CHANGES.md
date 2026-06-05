# COMP3310 secure development changes

This snapshot contains code changes for Tasks 7 and 9 of the COMP3310 group project.

## Authentication and score history
- Added ownership between `Game` records and Django `User` accounts.
- Protected `/history/` with `login_required`.
- Added public, read-only score sharing via UUID at `/score/<share_id>/`.
- Registered models in Django admin so administrators can edit/delete content.

## Secure request handling
- Changed game updates from GET to POST with CSRF token headers.
- Replaced use of the CSRF cookie as a session identifier with the Django server-side session key.
- Added allow-list validation for guessed letters, game IDs, word IDs and difficulty values.
- Added cross-user ownership checks for game update and hint requests.

## Additional features
- Feature 1: One-use hint endpoint at `/hint/`, protected by CSRF and ownership checks.
- Feature 2: Difficulty selection (`easy`, `medium`, `hard`) using a fixed allow-list and safe word filtering.

## Security testing
- Added Django tests for login protection, password hashing, score isolation, input validation, cross-user tampering, read-only sharing, hints and difficulty input.

## Automated analysis
- Added CodeQL workflow for Python static analysis.
- Added dependency audit workflow using `pip-audit`.
