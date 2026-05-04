"""
git_publisher.py
Push file wiki .md langsung ke GitHub repo via GitHub API.
File disimpan HANYA di GitHub — tidak ada storage di local siapapun.
"""

import os
import base64
import requests

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO  = os.environ.get("GITHUB_REPO", "etanaditoridho/techops-wiki")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")

BASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept":        "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_file_sha(path: str) -> str | None:
    """
    Cek apakah file sudah ada di GitHub dan ambil SHA-nya.
    SHA diperlukan jika ingin update file yang sudah ada.
    Returns None jika file belum ada.
    """
    url  = f"{BASE_URL}/contents/{path}"
    resp = requests.get(url, headers=HEADERS, params={"ref": GITHUB_BRANCH}, timeout=30)

    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()["sha"]


def push_file(path: str, content: str, commit_message: str) -> dict:
    """
    Push satu file ke GitHub repo.
    Jika file sudah ada → update (PUT dengan SHA).
    Jika file belum ada → create (PUT tanpa SHA).

    path: path di repo, contoh "wiki/engineering/operasi-hvac.md"
    content: isi file dalam string
    commit_message: pesan commit
    """
    url      = f"{BASE_URL}/contents/{path}"
    encoded  = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    sha      = get_file_sha(path)

    payload = {
        "message": commit_message,
        "content": encoded,
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha  # diperlukan untuk update file existing

    resp = requests.put(url, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()

    action = "Updated" if sha else "Created"
    print(f"    [github] ✓ {action}: {path}")
    return resp.json()


def push_wiki(slug: str, content: str, dept: str = "engineering") -> str:
    """
    Push wiki .md ke folder wiki/<dept>/<slug>.md di GitHub.
    Returns path file yang di-push.
    """
    path           = f"wiki/{dept}/{slug}.md"
    commit_message = f"wiki: update {slug} via SharePoint sync"
    push_file(path, content, commit_message)
    return path


def update_state(state: dict) -> None:
    """
    Update file .raw-ingest-state.json di GitHub untuk tracking file yang sudah diproses.
    """
    import json
    content        = json.dumps(state, indent=2, ensure_ascii=False)
    commit_message = "chore: update ingest state after SharePoint sync"
    push_file(".raw-ingest-state.json", content, commit_message)
    print(f"    [github] ✓ State file updated")


def get_state() -> dict:
    """
    Ambil state file dari GitHub untuk tahu file mana yang sudah diproses.
    Returns empty dict jika belum ada state.
    """
    import json
    url  = f"{BASE_URL}/contents/.raw-ingest-state.json"
    resp = requests.get(url, headers=HEADERS, params={"ref": GITHUB_BRANCH}, timeout=30)

    if resp.status_code == 404:
        return {}

    resp.raise_for_status()
    encoded = resp.json()["content"]
    decoded = base64.b64decode(encoded).decode("utf-8")
    return json.loads(decoded)


if __name__ == "__main__":
    # Test koneksi ke GitHub
    from dotenv import load_dotenv
    load_dotenv()

    url  = f"{BASE_URL}"
    resp = requests.get(url, headers=HEADERS, timeout=30)
    if resp.status_code == 200:
        print(f"✓ GitHub connection OK: {resp.json()['full_name']}")
        print(f"  Default branch: {resp.json()['default_branch']}")
    else:
        print(f"✗ GitHub connection failed: {resp.status_code}")
