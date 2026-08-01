#!/usr/bin/env python3
"""Prototype metadata extraction and semantic classification."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

SUPPORTED_PROTOTYPE_META_SCHEMA_VERSIONS = frozenset({"1.0"})
PROTOTYPE_META_STATUSES = frozenset({"Draft", "Confirmed"})
PROTOTYPE_ORIENTATIONS = frozenset({"portrait", "landscape"})
DECISION_STATUSES = frozenset({"待确认", "已确认", "已排除", "已替代"})
PROTOTYPE_META_PLACEHOLDERS = frozenset(
    {"待补充", "待确认", "todo", "tbd", "placeholder", "示例"}
)

class PrototypeMetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.capture = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "script":
            return
        attr_map = {key.lower(): value for key, value in attrs}
        self.capture = attr_map.get("id") == "prototype-meta"

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.capture:
            self.capture = False

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.parts.append(data)


@dataclass
class PrototypeMetaCheck:
    status: str
    missing_fields: list[str] = field(default_factory=list)
    invalid_fields: list[str] = field(default_factory=list)
    duplicate_ids: list[str] = field(default_factory=list)

    def as_payload(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "missingFields": self.missing_fields,
            "invalidFields": self.invalid_fields,
            "duplicateIds": self.duplicate_ids,
            "nextAction": (
                "use_metadata"
                if self.status == "COMPLETE"
                else "read_relevant_html"
            ),
        }


def read_prototype_meta(path: Path) -> dict[str, Any]:
    parser = PrototypeMetaParser()
    parser.feed(path.read_text(encoding="utf-8"))
    raw = "".join(parser.parts).strip()
    if not raw:
        raise ValueError("prototype-meta script 缺失或为空")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("prototype-meta 必须是 JSON object")
    return data


def _nonempty_meta_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_placeholder_meta_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and value.strip().casefold() in PROTOTYPE_META_PLACEHOLDERS
    )


def _append_once(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _validate_meta_string_list(
    value: Any,
    path: str,
    invalid: list[str],
    *,
    require_nonempty: bool = False,
) -> bool:
    if not isinstance(value, list):
        _append_once(invalid, path)
        return False
    if require_nonempty and not value:
        _append_once(invalid, path)
        return False
    valid = True
    for index, item in enumerate(value):
        if not _nonempty_meta_text(item):
            _append_once(invalid, f"{path}[{index}]")
            valid = False
    return valid


def _record_duplicate_id(
    seen: set[str],
    value: Any,
    collection: str,
    duplicate_ids: list[str],
) -> None:
    if not _nonempty_meta_text(value):
        return
    normalized = value.strip()
    if normalized in seen:
        _append_once(duplicate_ids, f"{collection}.id:{normalized}")
    else:
        seen.add(normalized)


def validate_prototype_meta_fields(
    meta: dict[str, Any],
) -> tuple[list[str], list[str]]:
    required_types: dict[str, type[Any]] = {
        "schemaVersion": str,
        "requirementName": str,
        "module": str,
        "prototypeVersion": str,
        "prototypeStatus": str,
        "device": dict,
        "scope": dict,
        "pages": list,
        "scenarios": list,
        "states": list,
        "decisions": list,
    }
    missing = [name for name in required_types if name not in meta]
    invalid: list[str] = []

    for name, expected_type in required_types.items():
        if name in meta and not isinstance(meta[name], expected_type):
            _append_once(invalid, name)
    for name in (
        "schemaVersion",
        "requirementName",
        "module",
        "prototypeVersion",
        "prototypeStatus",
    ):
        if name in meta and not _nonempty_meta_text(meta[name]):
            _append_once(invalid, name)

    scope = meta.get("scope")
    if isinstance(scope, dict):
        for name in ("included", "excluded"):
            path = f"scope.{name}"
            if name not in scope:
                missing.append(path)
            else:
                _validate_meta_string_list(scope[name], path, invalid)

    pages = meta.get("pages")
    if isinstance(pages, list):
        for index, page in enumerate(pages):
            if not isinstance(page, dict):
                _append_once(invalid, f"pages[{index}]")
                continue
            for name in ("id", "name"):
                if not _nonempty_meta_text(page.get(name)):
                    _append_once(invalid, f"pages[{index}].{name}")

    scenarios = meta.get("scenarios")
    if isinstance(scenarios, list):
        for index, scenario in enumerate(scenarios):
            if not isinstance(scenario, dict):
                _append_once(invalid, f"scenarios[{index}]")
                continue
            if not _nonempty_meta_text(scenario.get("id")):
                _append_once(invalid, f"scenarios[{index}].id")
            if not _nonempty_meta_text(scenario.get("entry")):
                _append_once(invalid, f"scenarios[{index}].entry")
            flow_present = "flow" in scenario
            result_present = "result" in scenario
            flow_valid = False
            result_valid = False
            if flow_present:
                flow_valid = _validate_meta_string_list(
                    scenario.get("flow"),
                    f"scenarios[{index}].flow",
                    invalid,
                    require_nonempty=True,
                )
            if result_present:
                result = scenario.get("result")
                if _nonempty_meta_text(result):
                    result_valid = True
                elif isinstance(result, list):
                    result_valid = _validate_meta_string_list(
                        result,
                        f"scenarios[{index}].result",
                        invalid,
                        require_nonempty=True,
                    )
                else:
                    _append_once(invalid, f"scenarios[{index}].result")
            if not flow_valid and not result_valid:
                _append_once(invalid, f"scenarios[{index}].flowOrResult")

    states = meta.get("states")
    if isinstance(states, list):
        for index, state in enumerate(states):
            if not isinstance(state, dict):
                _append_once(invalid, f"states[{index}]")
                continue
            for name in ("id", "description"):
                if not _nonempty_meta_text(state.get(name)):
                    _append_once(invalid, f"states[{index}].{name}")

    decisions = meta.get("decisions")
    if isinstance(decisions, list):
        for index, decision in enumerate(decisions):
            if not isinstance(decision, dict):
                _append_once(invalid, f"decisions[{index}]")
                continue
            decision_id = decision.get("id")
            if not (
                isinstance(decision_id, str)
                and re.fullmatch(r"D-\d{3}", decision_id)
            ):
                _append_once(invalid, f"decisions[{index}].id")
            for name in ("status", "summary"):
                if not _nonempty_meta_text(decision.get(name)):
                    _append_once(invalid, f"decisions[{index}].{name}")

    return missing, invalid


def validate_prototype_meta_semantics(
    meta: dict[str, Any],
) -> tuple[list[str], list[str], list[str]]:
    missing: list[str] = []
    invalid: list[str] = []
    duplicate_ids: list[str] = []

    schema_version = meta.get("schemaVersion")
    if (
        isinstance(schema_version, str)
        and schema_version.strip()
        and schema_version not in SUPPORTED_PROTOTYPE_META_SCHEMA_VERSIONS
    ):
        _append_once(invalid, "schemaVersion")

    prototype_version = meta.get("prototypeVersion")
    if (
        isinstance(prototype_version, str)
        and prototype_version.strip()
        and not re.fullmatch(r"v\d+(?:\.\d+)+", prototype_version.strip())
    ):
        _append_once(invalid, "prototypeVersion")

    prototype_status = meta.get("prototypeStatus")
    if (
        isinstance(prototype_status, str)
        and prototype_status.strip()
        and prototype_status not in PROTOTYPE_META_STATUSES
    ):
        _append_once(invalid, "prototypeStatus")

    device = meta.get("device")
    if isinstance(device, dict):
        if "orientation" not in device:
            _append_once(missing, "device.orientation")
        elif device.get("orientation") not in PROTOTYPE_ORIENTATIONS:
            _append_once(invalid, "device.orientation")
        if "platform" not in device:
            _append_once(missing, "device.platform")
        else:
            _validate_meta_string_list(
                device.get("platform"),
                "device.platform",
                invalid,
                require_nonempty=True,
            )

    collections = (
        ("pages", meta.get("pages")),
        ("scenarios", meta.get("scenarios")),
        ("states", meta.get("states")),
        ("decisions", meta.get("decisions")),
    )
    for collection_name, items in collections:
        if not isinstance(items, list):
            continue
        seen: set[str] = set()
        for item in items:
            if isinstance(item, dict):
                _record_duplicate_id(
                    seen, item.get("id"), collection_name, duplicate_ids
                )

    decisions = meta.get("decisions")
    if isinstance(decisions, list):
        for index, decision in enumerate(decisions):
            if not isinstance(decision, dict):
                continue
            status = decision.get("status")
            if (
                isinstance(status, str)
                and status.strip()
                and status not in DECISION_STATUSES
            ):
                _append_once(invalid, f"decisions[{index}].status")

    if meta.get("prototypeStatus") == "Confirmed":
        if isinstance(meta.get("pages"), list) and not meta["pages"]:
            _append_once(invalid, "pages")
        if isinstance(meta.get("scenarios"), list) and not meta["scenarios"]:
            _append_once(invalid, "scenarios")
        if isinstance(meta.get("states"), list) and not meta["states"]:
            _append_once(invalid, "states")

        for field_name in ("requirementName", "module"):
            if _is_placeholder_meta_text(meta.get(field_name)):
                _append_once(invalid, field_name)

        device = meta.get("device")
        if isinstance(device, dict) and isinstance(device.get("platform"), list):
            for index, platform in enumerate(device["platform"]):
                if _is_placeholder_meta_text(platform):
                    _append_once(invalid, f"device.platform[{index}]")

        scope = meta.get("scope")
        if isinstance(scope, dict):
            for list_name in ("included", "excluded"):
                values = scope.get(list_name)
                if isinstance(values, list):
                    for index, value in enumerate(values):
                        if _is_placeholder_meta_text(value):
                            _append_once(
                                invalid, f"scope.{list_name}[{index}]"
                            )

        pages = meta.get("pages")
        if isinstance(pages, list):
            for index, page in enumerate(pages):
                if not isinstance(page, dict):
                    continue
                for field_name in ("id", "name"):
                    if _is_placeholder_meta_text(page.get(field_name)):
                        _append_once(invalid, f"pages[{index}].{field_name}")

        scenarios = meta.get("scenarios")
        if isinstance(scenarios, list):
            for index, scenario in enumerate(scenarios):
                if not isinstance(scenario, dict):
                    continue
                for field_name in ("id", "entry"):
                    if _is_placeholder_meta_text(scenario.get(field_name)):
                        _append_once(
                            invalid, f"scenarios[{index}].{field_name}"
                        )
                for list_name in ("flow", "result"):
                    value = scenario.get(list_name)
                    if _is_placeholder_meta_text(value):
                        _append_once(
                            invalid, f"scenarios[{index}].{list_name}"
                        )
                    elif isinstance(value, list):
                        for value_index, item in enumerate(value):
                            if _is_placeholder_meta_text(item):
                                _append_once(
                                    invalid,
                                    f"scenarios[{index}].{list_name}[{value_index}]",
                                )

        states = meta.get("states")
        if isinstance(states, list):
            for index, state in enumerate(states):
                if not isinstance(state, dict):
                    continue
                for field_name in ("id", "description"):
                    if _is_placeholder_meta_text(state.get(field_name)):
                        _append_once(invalid, f"states[{index}].{field_name}")

        decisions = meta.get("decisions")
        if isinstance(decisions, list):
            for index, decision in enumerate(decisions):
                if not isinstance(decision, dict):
                    continue
                if _is_placeholder_meta_text(decision.get("summary")):
                    _append_once(invalid, f"decisions[{index}].summary")

    return missing, invalid, duplicate_ids


def classify_prototype_meta(meta: dict[str, Any]) -> PrototypeMetaCheck:
    missing, invalid = validate_prototype_meta_fields(meta)
    semantic_missing, semantic_invalid, duplicate_ids = (
        validate_prototype_meta_semantics(meta)
    )
    for field_name in semantic_missing:
        _append_once(missing, field_name)
    for field_name in semantic_invalid:
        _append_once(invalid, field_name)

    return PrototypeMetaCheck(
        status=(
            "COMPLETE"
            if not missing and not invalid and not duplicate_ids
            else "INCOMPLETE"
        ),
        missing_fields=missing,
        invalid_fields=invalid,
        duplicate_ids=duplicate_ids,
    )


def extract_prototype_meta_json(path: Path) -> str:
    """Serialize only prototype metadata, never the surrounding HTML source."""
    return json.dumps(
        read_prototype_meta(path),
        ensure_ascii=False,
        separators=(",", ":"),
    )
