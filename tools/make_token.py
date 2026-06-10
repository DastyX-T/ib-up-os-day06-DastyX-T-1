#!/usr/bin/env python3
import hashlib
import json
import sys
from pathlib import Path

for stream_name in ("stdout", "stderr"):
    stream = getattr(sys, stream_name, None)
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_FILE = ROOT / "manifest.json"


def load_manifest() -> dict:
    return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))


def build_token(github_login: str, token_prefix: str) -> str:
    normalized = github_login.strip().lower()
    if not normalized:
        raise ValueError("GitHub login is required")
    suffix = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:4].upper()
    return f"{token_prefix}-{suffix}"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python tools/make_token.py <github_login>")
        return 2
    manifest = load_manifest()
    token_prefix = str(manifest.get("token_prefix") or "").strip().upper()
    if not token_prefix or "{" in token_prefix or "}" in token_prefix:
        print("Шаблон ещё не настроен. Сначала обновите manifest.json или запустите tools/customize_template.py")
        return 2
    try:
        print(build_token(argv[1], token_prefix))
        return 0
    except ValueError as exc:
        print(exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
