#!/usr/bin/env python3
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

for stream_name in ("stdout", "stderr"):
    stream = getattr(sys, stream_name, None)
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

try:
    import yaml
except ImportError:
    print("Требуется PyYAML. Установите пакет командой: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_FILE = ROOT / "manifest.json"
SUBMISSION_FILE = ROOT / "student" / "submission.yaml"
REFLECTION_FILE = ROOT / "student" / "reflection.md"
REPORT_FILE = ROOT / "report.md"

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def load_manifest() -> dict:
    if not MANIFEST_FILE.exists():
        fail("Отсутствует файл manifest.json")
        return {}
    try:
        return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Некорректный JSON в manifest.json: {exc}")
        return {}


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def meaningful_text(text: str, min_len: int) -> bool:
    cleaned = " ".join((text or "").split())
    if len(cleaned) < min_len:
        return False
    lowered = cleaned.lower()
    placeholders = [
        "заполните",
        "кратко опишите",
        "опишите",
        "объясните",
        "укажите",
        "напишите",
        "оцените",
        "подведите итог",
        "если были ошибки",
        "да/нет",
        "замените этот текст",
        "замените",
        "todo",
        "your text",
        "шаблон",
    ]
    if any(marker in lowered for marker in placeholders):
        return False
    return True


def extract_section(markdown_text: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*(.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, markdown_text, flags=re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def has_markdown_table(text: str, min_data_rows: int = 2) -> bool:
    lines = [line.rstrip() for line in (text or "").splitlines()]
    for index in range(len(lines) - 2):
        header = lines[index].strip()
        separator = lines[index + 1].strip()
        if not (header.startswith("|") and header.endswith("|")):
            continue
        if not re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", separator):
            continue
        data_rows = 0
        for row in lines[index + 2:]:
            row = row.strip()
            if row.startswith("|") and row.endswith("|"):
                data_rows += 1
            else:
                break
        if data_rows >= min_data_rows:
            return True
    return False


def count_checked_checkboxes(text: str) -> int:
    return len(re.findall(r"(?im)^\s*-\s*\[[xX]\]\s+", text or ""))


def count_fenced_code_blocks(text: str) -> int:
    markers = re.findall(r"(?m)^\s*```", text or "")
    return len(markers) // 2


def missing_required_terms(text: str, required_terms: list[str]) -> list[str]:
    lowered = (text or "").lower()
    missing: list[str] = []
    for term in required_terms:
        normalized = str(term or "").strip()
        if normalized and normalized.lower() not in lowered:
            missing.append(normalized)
    return missing


def missing_required_any_term_groups(text: str, groups: list[object]) -> list[str]:
    lowered = (text or "").lower()
    missing: list[str] = []
    for group in groups:
        if isinstance(group, (list, tuple, set)):
            options = [str(item or "").strip() for item in group if str(item or "").strip()]
        else:
            options = [str(group or "").strip()] if str(group or "").strip() else []
        if not options:
            continue
        if not any(option.lower() in lowered for option in options):
            missing.append(" / ".join(options))
    return missing


def count_real_files(path: Path, patterns: tuple[str, ...]) -> int:
    total = 0
    for pattern in patterns:
        for candidate in path.glob(pattern):
            if candidate.is_file():
                total += 1
    return total


def iter_markdown_images(markdown_text: str) -> list[tuple[int, str, str]]:
    images: list[tuple[int, str, str]] = []
    in_code_block = False
    image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    for line_number, line in enumerate(markdown_text.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        for match in image_pattern.finditer(line):
            images.append((line_number, match.group(1).strip(), match.group(2).strip()))
    return images


def normalize_markdown_image_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if " " in target:
        target = target.split()[0].strip()
    return unquote(target.strip("'\""))


def caption_after_image(markdown_text: str, image_line_number: int) -> bool:
    lines = markdown_text.splitlines()
    for line in lines[image_line_number:image_line_number + 4]:
        stripped = line.strip()
        if not stripped:
            continue
        normalized = stripped.lstrip("- ").replace("*", "").strip().lower()
        return normalized.startswith("подпись:") or normalized.startswith("подпись -")
    return False


def validate_embedded_images(markdown_path: Path, markdown_text: str) -> tuple[int, int]:
    valid_images = 0
    captioned_images = 0
    allowed_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    repo_root = ROOT.resolve()

    for line_number, alt_text, raw_target in iter_markdown_images(markdown_text):
        target = normalize_markdown_image_target(raw_target)
        if not target:
            fail(f"{markdown_path.relative_to(ROOT)}: пустой путь к изображению в строке {line_number}")
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("//"):
            fail(f"{markdown_path.relative_to(ROOT)}: изображение в строке {line_number} должно быть локальным файлом, а не внешней ссылкой")
            continue
        if target.startswith("#"):
            fail(f"{markdown_path.relative_to(ROOT)}: изображение в строке {line_number} указывает на якорь, а не на файл")
            continue

        candidate = (markdown_path.parent / target).resolve()
        try:
            candidate.relative_to(repo_root)
        except ValueError:
            fail(f"{markdown_path.relative_to(ROOT)}: путь к изображению выходит за пределы репозитория: {target}")
            continue

        if candidate.suffix.lower() not in allowed_extensions:
            fail(f"{markdown_path.relative_to(ROOT)}: неподдерживаемое расширение изображения в строке {line_number}: {target}")
            continue
        if not candidate.is_file():
            fail(f"{markdown_path.relative_to(ROOT)}: битая ссылка на изображение в строке {line_number}: {target}")
            continue
        if len(alt_text) < 8:
            fail(f"{markdown_path.relative_to(ROOT)}: у изображения в строке {line_number} должно быть понятное описание внутри ![описание](...)")
            continue

        valid_images += 1
        if caption_after_image(markdown_text, line_number):
            captioned_images += 1
        else:
            fail(f"{markdown_path.relative_to(ROOT)}: после изображения в строке {line_number} нужна подпись в формате 'Подпись: ...'")

    return valid_images, captioned_images


def get_commit_count() -> tuple[int | None, str]:
    def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(ROOT), *args],
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    try:
        shallow = run_git(["rev-parse", "--is-shallow-repository"], check=False)
        if shallow.returncode == 0 and shallow.stdout.strip().lower() == "true":
            fetch = run_git(["fetch", "--unshallow", "--quiet"], check=False)
            if fetch.returncode != 0:
                fetch = run_git(["fetch", "--depth=1000000", "--quiet"], check=False)
            if fetch.returncode != 0:
                details = (fetch.stderr or fetch.stdout or "").strip()
                return None, "репозиторий склонирован без полной истории, git fetch не удался: " + (details or "нет деталей ошибки")

        result = run_git(["rev-list", "--count", "HEAD"])
    except FileNotFoundError:
        return None, "команда git не найдена"
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or str(exc)).strip()
        return None, details or "git rev-list завершился с ошибкой"
    try:
        return int(result.stdout.strip()), ""
    except ValueError:
        return None, f"неожиданный вывод git: {result.stdout.strip()}"


def get_commit_history() -> tuple[list[dict[str, object]] | None, str]:
    def run_git(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(ROOT), *args],
            check=check,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

    try:
        result = run_git(["log", "--format=COMMIT%x1f%H%x1f%s", "--name-only"])
    except FileNotFoundError:
        return None, "команда git не найдена"
    except subprocess.CalledProcessError as exc:
        details = (exc.stderr or exc.stdout or str(exc)).strip()
        return None, details or "git log завершился с ошибкой"

    commits: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    for raw_line in result.stdout.splitlines():
        if raw_line.startswith("COMMIT\x1f"):
            if current is not None:
                commits.append(current)
            _, sha, subject = (raw_line.split("\x1f", 2) + ["", ""])[:3]
            current = {"sha": sha.strip(), "subject": subject.strip(), "files": []}
            continue
        if current is None:
            continue
        line = raw_line.strip()
        if line:
            cast_files = current.setdefault("files", [])
            if isinstance(cast_files, list):
                cast_files.append(line)
    if current is not None:
        commits.append(current)
    return commits, ""


def build_token(github_login: str, token_prefix: str) -> str:
    normalized = github_login.strip().lower()
    suffix = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:4].upper()
    return f"{token_prefix}-{suffix}"


manifest = load_manifest()
rules = manifest.get("rules") if isinstance(manifest, dict) else {}
total_score = int((rules or {}).get("total_score") or 70)
token_prefix = str((manifest or {}).get("token_prefix") or "").strip().upper()
module_code_expected = str((manifest or {}).get("module_code") or "").strip()
allowed_os_types = set((rules or {}).get("allowed_os_types") or ["windows", "linux", "macos"])
submission_points = (rules or {}).get("submission_points") or {}
reflection_sections = (rules or {}).get("reflection_sections") or []
report_sections = (rules or {}).get("report_sections") or []
artifact_tables = (rules or {}).get("artifact_tables") or []
artifact_texts = (rules or {}).get("artifact_texts") or []
checklist_rule = (rules or {}).get("checklist") or {}
screenshots_rule = (rules or {}).get("screenshots") or {}
reflection_token_points = int((rules or {}).get("reflection_token_points") or 0)
min_commits = int((rules or {}).get("min_commits") or 0)
commit_checks = (rules or {}).get("commit_checks") or {}

raw_score = 0.0

template_values = [
    str((manifest or {}).get("assignment_id") or ""),
    str((manifest or {}).get("repository_prefix") or ""),
    str((manifest or {}).get("title") or ""),
    module_code_expected,
    token_prefix,
]
if any("{" in value or "}" in value for value in template_values):
    print("FAIL: 0/70")
    print("1. Шаблон задания ещё не настроен. Сначала обновите manifest.json или запустите tools/customize_template.py")
    sys.exit(1)

if min_commits > 0:
    commit_count, commit_error = get_commit_count()
    if commit_count is None:
        fail(f"Не удалось проверить количество коммитов: {commit_error}")
    elif commit_count < min_commits:
        fail(f"В репозитории должно быть не меньше {min_commits} коммитов, сейчас найдено: {commit_count}")

submission = {}
if not SUBMISSION_FILE.exists():
    fail("Отсутствует файл: student/submission.yaml")
else:
    try:
        submission = yaml.safe_load(SUBMISSION_FILE.read_text(encoding="utf-8")) or {}
        if not isinstance(submission, dict):
            fail("Файл student/submission.yaml должен содержать YAML-объект")
            submission = {}
    except Exception as exc:
        fail(f"Некорректный YAML в student/submission.yaml: {exc}")
        submission = {}

full_name = str(submission.get("full_name", "")).strip()
group = str(submission.get("group", "")).strip()
github_login = str(submission.get("github_login", "")).strip()
student_token = str(submission.get("student_token", "")).strip()
os_type = str(submission.get("os_type", "")).strip().lower()
work_mode = str(submission.get("work_mode", "")).strip()
tools_available = str(submission.get("tools_available", "")).strip()
evidence_mode = str(submission.get("evidence_mode", "")).strip()
module_code = str(submission.get("module_code", "")).strip()

expected_token = build_token(github_login, token_prefix) if github_login and token_prefix else ""

if commit_checks:
    commit_history, commit_history_error = get_commit_history()
    if commit_history is None:
        fail(f"Не удалось проверить историю коммитов: {commit_history_error}")
    else:
        min_token_commits = int(commit_checks.get("min_token_commits") or 0)
        required_touched_paths = [str(path or "").strip() for path in (commit_checks.get("required_touched_paths") or []) if str(path or "").strip()]
        if min_token_commits > 0:
            if not expected_token:
                fail("Невозможно проверить наличие token в commit history, потому что github_login или token заполнены некорректно")
            else:
                token_commits = sum(1 for item in commit_history if expected_token in str(item.get("subject") or ""))
                if token_commits < min_token_commits:
                    fail(f"Минимум {min_token_commits} commit message должны содержать token {expected_token}, сейчас найдено: {token_commits}")
        if required_touched_paths:
            touched_paths = {
                str(path or "").strip().lower()
                for item in commit_history
                for path in (item.get("files") or [])
            }
            missing_touched_paths = [path for path in required_touched_paths if path.lower() not in touched_paths]
            if missing_touched_paths:
                fail("В истории коммитов не найдены обязательные изменения файлов: " + ", ".join(missing_touched_paths))

if module_code == module_code_expected and module_code_expected:
    raw_score += float(submission_points.get("module_code", 0))
else:
    fail(f"Поле module_code должно быть равно {module_code_expected or 'значению из manifest.json'}")

if meaningful_text(full_name, 5):
    raw_score += float(submission_points.get("full_name", 0))
else:
    fail("Поле full_name пустое или слишком короткое")

if meaningful_text(group, 2):
    raw_score += float(submission_points.get("group", 0))
else:
    fail("Поле group пустое")

if re.fullmatch(r"[A-Za-z0-9-]{3,39}", github_login):
    raw_score += float(submission_points.get("github_login", 0))
else:
    fail("Поле github_login должно быть похоже на настоящий GitHub login")

if student_token == expected_token and expected_token:
    raw_score += float(submission_points.get("student_token", 0))
else:
    fail(f"Поле student_token должно совпадать с токеном, сгенерированным для github_login ({expected_token or 'неизвестно'})")

if os_type in allowed_os_types:
    raw_score += float(submission_points.get("os_type", 0))
else:
    fail(f"Поле os_type должно быть одним из значений: {', '.join(sorted(allowed_os_types))}")

if meaningful_text(work_mode, 3):
    raw_score += float(submission_points.get("work_mode", 0))
else:
    fail("Поле work_mode пустое")

if meaningful_text(tools_available, 3):
    raw_score += float(submission_points.get("tools_available", 0))
else:
    fail("Поле tools_available пустое")

if meaningful_text(evidence_mode, 3):
    raw_score += float(submission_points.get("evidence_mode", 0))
else:
    fail("Поле evidence_mode пустое")

reflection_text = read_text(REFLECTION_FILE)
if not reflection_text:
    fail("Файл student/reflection.md отсутствует или пуст")
else:
    token_match = re.search(rf"^Токен:\s*({re.escape(token_prefix)}-[A-F0-9]{{4}})\s*$", reflection_text, flags=re.MULTILINE)
    if token_match and token_match.group(1) == expected_token:
        raw_score += float(reflection_token_points)
    else:
        fail("В файле reflection.md должна быть строка с корректным token в формате 'Токен: ...'")

    for section in reflection_sections:
        title = str(section.get("title") or "").strip()
        min_length = int(section.get("min_length") or 80)
        points = float(section.get("points") or 0)
        text = extract_section(reflection_text, title)
        if meaningful_text(text, min_length):
            raw_score += points
        else:
            fail(f"Раздел reflection.md '{title}' отсутствует или заполнен слишком кратко")

report_text = read_text(REPORT_FILE)
if not report_text:
    fail("Файл report.md отсутствует или пуст")
else:
    for section in report_sections:
        title = str(section.get("title") or "").strip()
        min_length = int(section.get("min_length") or 120)
        points = float(section.get("points") or 0)
        required_terms = [str(term or "").strip() for term in (section.get("required_terms") or []) if str(term or "").strip()]
        text = extract_section(report_text, title)
        missing_terms = missing_required_terms(text, required_terms) if text else required_terms
        if not meaningful_text(text, min_length):
            fail(f"Раздел report.md '{title}' отсутствует или заполнен слишком кратко")
        elif not missing_terms:
            raw_score += points
        else:
            fail(f"Раздел report.md '{title}' не содержит обязательные термины: {', '.join(missing_terms)}")

for rule in artifact_tables:
    rel_path = str(rule.get("path") or "").strip()
    min_rows = int(rule.get("min_data_rows") or 2)
    min_length = int(rule.get("min_length") or 80)
    points = float(rule.get("points") or 0)
    required_terms = [str(term or "").strip() for term in (rule.get("required_terms") or []) if str(term or "").strip()]
    path = ROOT / rel_path
    text = read_text(path)
    missing_terms = missing_required_terms(text, required_terms) if text else required_terms
    if not (text and meaningful_text(text, min_length) and has_markdown_table(text, min_data_rows=min_rows)):
        fail(f"{rel_path} должен содержать заполненную Markdown-таблицу минимум с {min_rows} строками данных")
    elif not missing_terms:
        raw_score += points
    else:
        fail(f"{rel_path} не содержит обязательные элементы: {', '.join(missing_terms)}")

for rule in artifact_texts:
    rel_path = str(rule.get("path") or "").strip()
    min_length = int(rule.get("min_length") or 100)
    min_code_blocks = int(rule.get("min_code_blocks") or 0)
    points = float(rule.get("points") or 0)
    required_sections = rule.get("required_sections") or []
    required_terms = [str(term or "").strip() for term in (rule.get("required_terms") or []) if str(term or "").strip()]
    required_any_term_groups = rule.get("required_any_term_groups") or []
    path = ROOT / rel_path
    text = read_text(path)
    missing_sections: list[str] = []
    for section in required_sections:
        if isinstance(section, dict):
            section_title = str(section.get("title") or "").strip()
            section_min_length = int(section.get("min_length") or 60)
        else:
            section_title = str(section).strip()
            section_min_length = 60
        if not section_title:
            continue
        if not meaningful_text(extract_section(text, section_title), section_min_length):
            missing_sections.append(section_title)
    missing_terms = missing_required_terms(text, required_terms) if text else required_terms
    missing_groups = missing_required_any_term_groups(text, required_any_term_groups) if text else [str(group) for group in required_any_term_groups]
    code_blocks = count_fenced_code_blocks(text)
    if not (text and meaningful_text(text, min_length)):
        fail(f"{rel_path} отсутствует или заполнен слишком кратко")
    elif missing_sections:
        fail(f"{rel_path} должен содержать заполненные разделы: {', '.join(missing_sections)}")
    elif missing_terms:
        fail(f"{rel_path} не содержит обязательные команды или термины: {', '.join(missing_terms)}")
    elif missing_groups:
        fail(f"{rel_path} должен содержать хотя бы один элемент из каждой группы: {', '.join(missing_groups)}")
    elif code_blocks < min_code_blocks:
        fail(f"{rel_path} должен содержать минимум {min_code_blocks} fenced code block с командами и/или выводом")
    else:
        raw_score += points

checklist_path = ROOT / str(checklist_rule.get("path") or "")
checklist_text = read_text(checklist_path)
checklist_points = float(checklist_rule.get("points") or 0)
checklist_min_length = int(checklist_rule.get("min_length") or 80)
checklist_min_boxes = int(checklist_rule.get("min_checkboxes") or 10)
if (
    checklist_text
    and meaningful_text(checklist_text, checklist_min_length)
    and count_checked_checkboxes(checklist_text) >= checklist_min_boxes
):
    raw_score += checklist_points
else:
    fail(f"{checklist_rule.get('path')} должен содержать минимум {checklist_min_boxes} отмеченных чекбоксов и короткую итоговую заметку")

screenshots_index_path = ROOT / str(screenshots_rule.get("index_path") or "")
screenshots_dir = screenshots_index_path.parent
screenshots_text = read_text(screenshots_index_path)
screenshots_points = float(screenshots_rule.get("points") or 0)
screenshots_min_images = int(screenshots_rule.get("min_images") or 2)
screenshots_min_rows = int(screenshots_rule.get("min_data_rows") or 2)
screenshots_min_length = int(screenshots_rule.get("min_length") or 60)
screenshots_token_mentions = int(screenshots_rule.get("token_mentions") or 1)
screenshots_min_embedded = int(screenshots_rule.get("min_embedded_images") or screenshots_min_images)
screenshots_min_captions = int(screenshots_rule.get("min_captions") or screenshots_min_embedded)
screenshots_expected_token_mentions = int(screenshots_rule.get("expected_token_mentions") or 0)
screenshots_required_files = [str(item or "").strip() for item in (screenshots_rule.get("required_files") or []) if str(item or "").strip()]
image_count = count_real_files(screenshots_dir, ("*.png", "*.jpg", "*.jpeg", "*.webp"))
embedded_images, captioned_images = validate_embedded_images(screenshots_index_path, screenshots_text) if screenshots_text else (0, 0)
embedded_targets = {
    normalize_markdown_image_target(raw_target).lower()
    for _, _, raw_target in iter_markdown_images(screenshots_text)
}
missing_required_screenshots = [name for name in screenshots_required_files if not (screenshots_dir / name).is_file()]
missing_required_embeds = [name for name in screenshots_required_files if name.lower() not in embedded_targets]
missing_screenshot_terms = missing_required_terms(screenshots_text, screenshots_required_files) if screenshots_text else screenshots_required_files
expected_token_mentions_ok = True
if screenshots_expected_token_mentions > 0 and expected_token:
    expected_token_mentions_ok = screenshots_text.count(expected_token) >= screenshots_expected_token_mentions
if (
    screenshots_text
    and meaningful_text(screenshots_text, screenshots_min_length)
    and has_markdown_table(screenshots_text, min_data_rows=screenshots_min_rows)
    and image_count >= screenshots_min_images
    and embedded_images >= screenshots_min_embedded
    and captioned_images >= screenshots_min_captions
    and screenshots_text.lower().count("token") >= screenshots_token_mentions
    and not missing_required_screenshots
    and not missing_required_embeds
    and not missing_screenshot_terms
    and expected_token_mentions_ok
):
    raw_score += screenshots_points
elif missing_required_screenshots:
    fail(f"В папке artifacts/screenshots отсутствуют обязательные файлы: {', '.join(missing_required_screenshots)}")
elif missing_required_embeds:
    fail(f"В artifacts/screenshots/README.md не встроены обязательные изображения: {', '.join(missing_required_embeds)}")
elif missing_screenshot_terms:
    fail(f"В artifacts/screenshots/README.md отсутствуют обязательные ссылки или имена файлов: {', '.join(missing_screenshot_terms)}")
elif not expected_token_mentions_ok:
    fail(f"В artifacts/screenshots/README.md token {expected_token} должен встречаться минимум {screenshots_expected_token_mentions} раз")
else:
    fail(
        f"{screenshots_rule.get('index_path')} должен содержать таблицу, минимум {screenshots_min_embedded} вставленных Markdown-изображения с подписями, а в папке artifacts/screenshots должно быть минимум {screenshots_min_images} файлов изображений"
    )

final_score = max(0.0, min(float(total_score), raw_score))
if errors:
    print(f"FAIL: {round(final_score, 2)}/{total_score}")
    for index, error in enumerate(errors, start=1):
        print(f"{index}. {error}")
    for warning in warnings:
        print(f"ПРЕДУПРЕЖДЕНИЕ: {warning}")
    sys.exit(1)

for warning in warnings:
    print(f"ПРЕДУПРЕЖДЕНИЕ: {warning}")
print(f"OK: {round(final_score, 2)}/{total_score}")
sys.exit(0)
