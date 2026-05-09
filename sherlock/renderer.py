from __future__ import annotations

from typing import Any


_FORMATS = {
    "new_case": "NEW CASE: {case_id} {severity} {slug}",
    "severity_changed": "SEVERITY CHANGED: {case_id} {old_severity} -> {new_severity}",
    "resolved": "RESOLVED: {case_id} {slug}",
}


def format_transition(transition: dict[str, Any]) -> str | None:
    t_type = transition["type"]
    if t_type == "steady_state":
        return None
    return _FORMATS[t_type].format(**transition)
