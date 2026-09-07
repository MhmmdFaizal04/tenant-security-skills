# Contributing

We welcome contributions to the Tenant Security Skills repository!

## How to add fixture scenarios

1. Create a new directory under `fixtures/` for your scenario.
2. Ensure you have both a vulnerable and a secure version of the API.
3. Update the `README.md` to reflect the new fixtures.
4. Add expected findings JSON files in `fixtures/expected/`.

## How to add evaluation cases

1. Add your new evaluation case to `evals/cases.json`.
2. Document the case in `evals/README.md`.
3. Ensure the `tests/validate_repo.py` script validates the new case.

## How to report issues

Please use the issue templates provided in the `.github/ISSUE_TEMPLATE` directory to report bugs or request features.

## Code style requirements

- Follow PEP 8 for Python code.
- Ensure all markdown files are properly formatted.
- Write clear and concise commit messages.

## Good First Issues

1. Add a fixture for GraphQL tenant isolation
2. Add a fixture for JWT-based tenant auth
3. Add evaluation case for batch endpoint testing
4. Add PostgreSQL RLS remediation example
5. Translate README to another language
