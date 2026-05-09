from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

_PKG_DIR = Path(__file__).parent
_PROJECT_ROOT = _PKG_DIR.parent
CASES_DIR = _PROJECT_ROOT / "memory" / "cases"
MEMORY_DIR = _PROJECT_ROOT / "memory"

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)

_ORDERED_KEYS = [
    "case_id", "slug", "status", "severity",
    "first_seen", "last_seen", "last_severity_change",
    "resolved_at", "resolution_reason", "dedup_signature",
    "hypothesis",
]
_PRIVATE_KEYS = {"_body", "_path"}


def _coerce_str(v: Any) -> Any:
    if isinstance(v, object) and not isinstance(v, (str, int, float, bool, type(None), list, dict)):
        return str(v)
    return v


def _parse_case_file(text: str) -> dict[str, Any]:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError("Case file missing YAML frontmatter")
    case = yaml.safe_load(m.group(1))
    for k in ("first_seen", "last_seen", "last_severity_change", "resolved_at"):
        if k in case and case[k] is not None:
            case[k] = str(case[k])
    case["_body"] = m.group(2)
    return case


def _render_case_file(case: dict[str, Any]) -> str:
    body = case.get("_body", "")
    fm_data = {k: case[k] for k in _ORDERED_KEYS if k in case}
    for k, v in case.items():
        if k not in fm_data and k not in _PRIVATE_KEYS:
            fm_data[k] = v
    frontmatter = yaml.dump(fm_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{frontmatter}---\n{body}"


def load_cases() -> list[dict[str, Any]]:
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    cases = []
    for path in sorted(CASES_DIR.glob("*.md")):
        if path.name == ".gitkeep":
            continue
        case = _parse_case_file(path.read_text(encoding="utf-8"))
        case["_path"] = path
        cases.append(case)
    return cases


def save_case(case: dict[str, Any]) -> None:
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    path = case.get("_path")
    if path is None:
        filename = f"{case['case_id']}-{case['slug']}.md"
        path = CASES_DIR / filename
        case["_path"] = path
    Path(path).write_text(_render_case_file(case), encoding="utf-8")


def allocate_case_id(extra_offset: int = 0) -> str:
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    max_n = 0
    for path in CASES_DIR.glob("CASE-*.md"):
        stem = path.stem
        parts = stem.split("-")
        if len(parts) >= 2 and parts[1].isdigit():
            max_n = max(max_n, int(parts[1]))
    return f"CASE-{max_n + 1 + extra_offset:04d}"


def load_memory_doc(name: str) -> str:
    return (MEMORY_DIR / name).read_text(encoding="utf-8")
