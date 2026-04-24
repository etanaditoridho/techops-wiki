import sys


DEPRECATION_MESSAGE = """
[DEPRECATED] scripts/sync-to-notion.py is intentionally disabled.

Reason:
- This legacy script is unsafe for the current repository architecture.
- It uses a different sync model than the active production path.
- Running it risks incorrect updates or unintended archival in Notion.

Canonical sync architecture:
- raw/    = immutable source documents
- wiki/   = source of truth for maintained knowledge
- Notion  = synced database/UI layer
- SOP/    = generated mirror for Obsidian consumption

Supported sync paths:
- wiki/ -> Notion via scripts/populate-sop-database.py
- Notion -> SOP/ via .github/workflows/sync-notion-to-obsidian.yml

Do not re-enable this script without an explicit architecture change.
"""


def main() -> int:
    print(DEPRECATION_MESSAGE.strip())
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
