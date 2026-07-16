import base64
import os

import requests

_HEADERS = {
    "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN', '')}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
_REPO = os.environ.get("GITHUB_REPOSITORY", "")
_HEAD_SHA = os.environ.get("HEAD_SHA", "")


def get_file_content(file_path: str) -> str:
    """Return the full source of a file at the PR's head commit.

    Use this when the diff alone lacks enough context — e.g. to see a full
    function body, understand imports, or check a type definition.

    Args:
        file_path: Repo-relative path, e.g. "backend/app/models.py".

    Returns:
        File content as a string, or an error message if not found.
    """
    url = f"https://api.github.com/repos/{_REPO}/contents/{file_path}?ref={_HEAD_SHA}"
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    if resp.status_code == 404:
        return f"[File not found: {file_path}]"
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        return f"[{file_path} is a directory, not a file]"
    if data.get("encoding") == "base64":
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    return data.get("content", "")
