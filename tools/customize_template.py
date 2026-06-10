#!/usr/bin/env python3
import argparse
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
TEXT_FILES = [
    ROOT / "README.md",
    ROOT / "report.md",
    ROOT / "student" / "submission.yaml",
    ROOT / "student" / "reflection.md",
    ROOT / "materials" / "module_guide.md",
    ROOT / "artifacts" / "concepts_table.md",
    ROOT / "artifacts" / "guided_exercises_log.md",
    ROOT / "artifacts" / "practice_notes.md",
    ROOT / "artifacts" / "lab_autocheck_result.md",
    ROOT / "artifacts" / "evidence_log.md",
    ROOT / "artifacts" / "verification_checklist.md",
    ROOT / "artifacts" / "screenshots" / "README.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Быстро настроить ib-up-os-task-template под новое задание.")
    parser.add_argument("--assignment-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--module-code", required=True)
    parser.add_argument("--token-prefix", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--repo-prefix", default=None)
    parser.add_argument("--min-commits", type=int, default=None)
    parser.add_argument("--duration", type=int, default=None)
    parser.add_argument("--level", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    manifest["assignment_id"] = args.assignment_id
    manifest["title"] = args.title
    manifest["module_code"] = args.module_code
    manifest["token_prefix"] = args.token_prefix.upper()
    manifest["student_goal"] = args.goal
    manifest["repository_prefix"] = args.repo_prefix or f"{args.assignment_id}-"
    if args.min_commits is not None:
        manifest.setdefault("rules", {})["min_commits"] = int(args.min_commits)
    if args.duration is not None:
        manifest["estimated_duration_minutes"] = int(args.duration)
    if args.level:
        manifest["level"] = args.level
    MANIFEST_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    replacements = {
        "{{ASSIGNMENT_ID}}": args.assignment_id,
        "{{ASSIGNMENT_TITLE}}": args.title,
        "{{MODULE_CODE}}": args.module_code,
        "{{TOKEN_PREFIX}}": args.token_prefix.upper(),
        "{{STUDENT_GOAL}}": args.goal,
        "{{REPO_PREFIX}}": args.repo_prefix or f"{args.assignment_id}-",
        "{{MIN_COMMITS}}": str(manifest.get("rules", {}).get("min_commits", 7)),
    }

    for path in TEXT_FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")

    print("Шаблон обновлён.")
    print(f"assignment_id: {args.assignment_id}")
    print(f"title: {args.title}")
    print(f"module_code: {args.module_code}")
    print(f"token_prefix: {args.token_prefix.upper()}")
    print(f"repo_prefix: {manifest['repository_prefix']}")
    print(f"min_commits: {manifest.get('rules', {}).get('min_commits')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
