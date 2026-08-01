#!/usr/bin/env python3
"""Core validation logic for mobile-game-product-forge formal stage gates."""

from __future__ import annotations

import copy
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from prototype_meta import (
    classify_prototype_meta,
    extract_prototype_meta_json,
    read_prototype_meta,
)

PASS = 0
BLOCKED = 2
INVALID_STATE = 3
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "references" / "stage-state.schema.json"


@dataclass
class GateResult:
    result: str
    target: str
    current_stage: str
    missing_conditions: list[str] = field(default_factory=list)
    invalid_fields: list[str] = field(default_factory=list)
    return_to_stage: str = ""
    next_action: str = ""

    @property
    def exit_code(self) -> int:
        if self.result in {"PASS", "NOT_REQUIRED"}:
            return PASS
        if self.result == "BLOCKED":
            return BLOCKED
        return INVALID_STATE


def load_schema() -> dict[str, Any]:
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"阶段状态 Schema 无法读取: {exc}") from exc
    if not isinstance(schema, dict):
        raise ValueError("阶段状态 Schema 根节点必须是 JSON object")
    return schema


SCHEMA = load_schema()
RESEARCH_FILENAMES = frozenset(
    {"00-research-findings.md", "00-project-context.md"}
)
SUMMARY_FILENAMES = frozenset(
    {"01-requirement-summary.md", "01-requirement-decisions.md"}
)
RESEARCH_REQUIRED_HEADINGS = (
    "## 2. 当前现状",
    "## 3. 目标状态",
    "## 4. 当前状态与目标状态差异",
    "## 10. 风险",
    "## 11. 来源索引",
)


def complexity_policy(level: str) -> dict[str, Any]:
    policies = SCHEMA.get("x-complexityPolicies", {})
    policy = policies.get(level) if isinstance(policies, dict) else None
    if not isinstance(policy, dict):
        raise ValueError(f"未定义的复杂度策略: {level}")
    return policy


def load_state(path: Path) -> dict[str, Any]:
    if path.suffix.lower() != ".json":
        raise ValueError(
            "旧状态格式：本脚本不解析 00-stage-state.yaml；"
            "历史需求可继续保留，新需求请创建 00-stage-state.json"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("状态文件根节点必须是 JSON object")
    return data


def _schema_for_property(name: str) -> dict[str, Any]:
    properties = SCHEMA.get("properties", {})
    raw = properties.get(name, {}) if isinstance(properties, dict) else {}
    if not isinstance(raw, dict):
        return {}
    merged: dict[str, Any] = {}
    ref = raw.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/$defs/"):
        definition_name = ref.rsplit("/", 1)[-1]
        definitions = SCHEMA.get("$defs", {})
        definition = (
            definitions.get(definition_name, {})
            if isinstance(definitions, dict)
            else {}
        )
        if isinstance(definition, dict):
            merged = copy.deepcopy(definition)
    for key, value in raw.items():
        if key == "properties" and isinstance(value, dict):
            base_properties = merged.setdefault("properties", {})
            if isinstance(base_properties, dict):
                base_properties.update(copy.deepcopy(value))
        elif key != "$ref":
            merged[key] = copy.deepcopy(value)
    return merged


def _matches_type(value: Any, expected: Any) -> bool:
    expected_types = expected if isinstance(expected, list) else [expected]
    for type_name in expected_types:
        if type_name == "object" and isinstance(value, dict):
            return True
        if type_name == "array" and isinstance(value, list):
            return True
        if type_name == "string" and isinstance(value, str):
            return True
        if type_name == "boolean" and isinstance(value, bool):
            return True
        if type_name == "integer" and isinstance(value, int) and not isinstance(value, bool):
            return True
        if type_name == "null" and value is None:
            return True
    return False


def _validate_value(path: str, value: Any, rule: dict[str, Any], invalid: list[str]) -> None:
    if "type" in rule and not _matches_type(value, rule["type"]):
        invalid.append(f"{path} 类型无效，必须为 {rule['type']}")
        return
    if "const" in rule and value != rule["const"]:
        invalid.append(f"{path} 必须为 {rule['const']}")
    enum = rule.get("enum")
    if isinstance(enum, list) and value not in enum:
        invalid.append(f"{path} 值无效：{value!r}；允许值={enum}")
    minimum = rule.get("minimum")
    if (
        isinstance(minimum, int)
        and isinstance(value, int)
        and not isinstance(value, bool)
        and value < minimum
    ):
        invalid.append(f"{path} 不得小于 {minimum}")


def validate_structure(state: dict[str, Any]) -> list[str]:
    invalid: list[str] = []
    for key in SCHEMA.get("required", []):
        if key not in state:
            invalid.append(f"缺失必需字段: {key}")

    root_properties = SCHEMA.get("properties", {})
    if not isinstance(root_properties, dict):
        return ["Schema properties 无效"]

    for name, value in state.items():
        if name not in root_properties:
            continue
        rule = _schema_for_property(name)
        _validate_value(name, value, rule, invalid)
        if not isinstance(value, dict):
            continue
        for field_name in rule.get("required", []):
            if field_name not in value:
                invalid.append(f"缺失必需字段: {name}.{field_name}")
        field_rules = rule.get("properties", {})
        if not isinstance(field_rules, dict):
            continue
        for field_name, field_value in value.items():
            field_rule = field_rules.get(field_name)
            if isinstance(field_rule, dict):
                _validate_value(
                    f"{name}.{field_name}", field_value, field_rule, invalid
                )

    schema_version_rule = root_properties.get("schemaVersion", {})
    if "schemaVersion" in state and isinstance(schema_version_rule, dict):
        _validate_value(
            "schemaVersion", state["schemaVersion"], schema_version_rule, invalid
        )
    return invalid


def _requirement_root(state_path: Path) -> Path | None:
    requirement_dir = state_path.parent.resolve()
    history_dir = requirement_dir.parent
    if history_dir.name.lower() == "history":
        return history_dir.parent.resolve()
    return None


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_file(
    state_path: Path, raw_path: Any
) -> tuple[Path | None, str | None]:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None, None
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = state_path.parent / candidate
    resolved = candidate.resolve()
    allowed_roots = [state_path.parent.resolve()]
    project_root = _requirement_root(state_path)
    if project_root is not None:
        allowed_roots.append(project_root)
    if not any(_is_within(resolved, root) for root in allowed_roots):
        return resolved, "文件路径必须位于当前需求目录或所属项目目录"
    return resolved, None


def _section(state: dict[str, Any], name: str) -> dict[str, Any]:
    value = state.get(name)
    return value if isinstance(value, dict) else {}


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _artifact_evidence(
    state_path: Path,
    section_name: str,
    section: dict[str, Any],
    *,
    require_file: bool,
    require_version: bool,
) -> tuple[list[str], list[str], Path | None]:
    missing: list[str] = []
    invalid: list[str] = []
    raw_file = section.get("file")
    resolved, path_error = resolve_file(state_path, raw_file)
    if path_error:
        invalid.append(f"{section_name}.file: {path_error}")
    if require_file and not _nonempty(raw_file):
        missing.append(f"{section_name}.file 必须记录文件路径")
    if resolved is not None and not resolved.is_file():
        missing.append(f"{section_name}.file 声明的文件不存在: {resolved}")
    if require_version and not _nonempty(section.get("version")):
        missing.append(f"{section_name}.version 不得为空")
    return missing, invalid, resolved


def validate_research_context(
    state_path: Path,
    project_context: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Validate the common formal-requirement research prerequisite."""
    missing: list[str] = []
    invalid: list[str] = []
    status = project_context.get("status")
    if status != "completed":
        missing.append("projectContext.status 必须为 completed")
        return missing, invalid

    raw_file = project_context.get("file")
    version = project_context.get("version")
    if not _nonempty(raw_file):
        invalid.append(
            "projectContext.status=completed 时 projectContext.file 不得为空"
        )
    if not _nonempty(version):
        invalid.append(
            "projectContext.status=completed 时 projectContext.version 不得为空"
        )
    if not _nonempty(raw_file):
        return missing, invalid

    relative_path = Path(raw_file)
    if relative_path.is_absolute():
        invalid.append("projectContext.file 必须使用当前需求目录下的相对路径")
        return missing, invalid
    if relative_path.name not in RESEARCH_FILENAMES:
        allowed = ", ".join(sorted(RESEARCH_FILENAMES))
        invalid.append(
            f"projectContext.file 必须是允许的调研产物：{allowed}"
        )

    requirement_dir = state_path.parent.resolve()
    resolved = (requirement_dir / relative_path).resolve()
    if not _is_within(resolved, requirement_dir):
        invalid.append("projectContext.file 必须位于当前需求目录内")
    elif not resolved.is_file():
        invalid.append(
            f"projectContext.status=completed 时调研文件必须存在: {resolved}"
        )
    else:
        try:
            content = resolved.read_text(encoding="utf-8")
        except OSError as exc:
            invalid.append(f"projectContext.file 无法读取: {exc}")
        else:
            if not content.strip():
                invalid.append("projectContext.file 调研产物不得为空")
            elif relative_path.name == "00-research-findings.md":
                for heading in RESEARCH_REQUIRED_HEADINGS:
                    if not re.search(
                        rf"(?m)^\s*{re.escape(heading)}\s*$", content
                    ):
                        invalid.append(
                            f"projectContext.file 缺少调研最低结构标题: {heading}"
                        )
    return missing, invalid


def _validate_declared_paths(
    state_path: Path, state: dict[str, Any]
) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    invalid: list[str] = []
    for section_name in (
        "projectContext",
        "requirementSummary",
        "prototype",
        "prd",
        "review",
        "validation",
        "delivery",
        "knowledgeProposal",
    ):
        section = _section(state, section_name)
        raw_file = section.get("file")
        if not _nonempty(raw_file):
            continue
        resolved, path_error = resolve_file(state_path, raw_file)
        if path_error:
            invalid.append(f"{section_name}.file: {path_error}")
        elif resolved is not None and not resolved.is_file():
            missing.append(f"{section_name}.file 声明的文件不存在: {resolved}")
    return missing, invalid


def _unresolved_major_review_disputes(state: dict[str, Any]) -> list[Any]:
    """Return explicit unresolved major-review-dispute markers from blockers."""
    unresolved: list[Any] = []
    blockers = state.get("blockers")
    if not isinstance(blockers, list):
        return unresolved
    for blocker in blockers:
        if isinstance(blocker, str):
            normalized = blocker.strip().lower()
            if normalized.startswith(
                ("[major_review_dispute]", "[重大评审争议]")
            ):
                unresolved.append(blocker)
            continue
        if not isinstance(blocker, dict):
            continue
        marker_type = blocker.get("type")
        if marker_type not in {"major_review_dispute", "重大评审争议"}:
            continue
        marker_status = str(blocker.get("status", "open")).strip().lower()
        if marker_status not in {"resolved", "closed", "decided", "已解决", "已裁定"}:
            unresolved.append(blocker)
    return unresolved


def _declared_file_exists(
    state_path: Path, section: dict[str, Any]
) -> bool:
    resolved, path_error = resolve_file(state_path, section.get("file"))
    return path_error is None and resolved is not None and resolved.is_file()


def _final_sync_evidence(
    state_path: Path, prd: dict[str, Any]
) -> tuple[list[str], list[str]]:
    """Machine-check completion condition 3: the frozen final PRD is synced.

    See references/stage-gates.md「正式 PRD 流程完成的唯一判定」. The
    orchestrator records the synced copy (docs/prd/<name>.md or the project's
    existing formal PRD directory) in prd.syncedTo before freezing final.
    """
    missing: list[str] = []
    invalid: list[str] = []
    raw = prd.get("syncedTo")
    if not _nonempty(raw):
        missing.append(
            "prd.syncedTo 必须记录正式终稿同步位置"
            "（docs/prd/<需求简称>.md 或项目既有正式 PRD 目录）"
        )
        return missing, invalid
    resolved, path_error = resolve_file(state_path, raw)
    if path_error:
        invalid.append(f"prd.syncedTo: {path_error}")
    elif resolved is not None and not resolved.is_file():
        missing.append(f"prd.syncedTo 声明的同步文件不存在: {resolved}")
    return missing, invalid


def validate_cross_field_consistency(
    state_path: Path, state: dict[str, Any]
) -> list[str]:
    """Reject internally contradictory states before evaluating a target gate."""
    invalid: list[str] = []
    prototype = _section(state, "prototype")
    prd = _section(state, "prd")
    review = _section(state, "review")
    validation = _section(state, "validation")
    delivery = _section(state, "delivery")

    if (
        prototype.get("applicability") == "required"
        and prototype.get("status") == "waived"
    ):
        invalid.append(
            "prototype.applicability=required 时 prototype.status 不得为 waived"
        )
    if (
        prototype.get("applicability") == "not_applicable"
        and prototype.get("status") == "confirmed"
    ):
        invalid.append(
            "prototype.applicability=not_applicable 时 prototype.status 不得为 confirmed"
        )

    if delivery.get("required") is False and delivery.get("status") != "not_required":
        invalid.append(
            "delivery.required=false 时 delivery.status 必须为 not_required"
        )
    if delivery.get("required") is True and delivery.get("status") == "not_required":
        invalid.append(
            "delivery.required=true 时 delivery.status 不得为 not_required"
        )

    if prd.get("status") == "final":
        if validation.get("status") != "passed":
            invalid.append("prd.status=final 时 validation.status 必须为 passed")
        if not _declared_file_exists(state_path, validation):
            invalid.append(
                "prd.status=final 时 validation.file 必须声明且文件存在"
            )
        if validation.get("targetPrdVersion") != prd.get("version"):
            invalid.append(
                "prd.status=final 时 validation.targetPrdVersion 必须与 prd.version 一致"
            )
        if not _declared_file_exists(state_path, prd):
            invalid.append("prd.status=final 时 prd.file 必须声明且文件存在")
        sync_missing, sync_invalid = _final_sync_evidence(state_path, prd)
        invalid.extend(f"prd.status=final 时 {item}" for item in sync_missing)
        invalid.extend(sync_invalid)

    unresolved_disputes = _unresolved_major_review_disputes(state)
    if unresolved_disputes and review.get("status") != "disputed":
        invalid.append(
            "存在未解决重大评审争议时 review.status 必须为 disputed"
        )
    if review.get("status") == "passed":
        open_p0 = review.get("openP0")
        if (
            not isinstance(open_p0, int)
            or isinstance(open_p0, bool)
            or open_p0 != 0
        ):
            invalid.append(
                "review.status=passed 时 review.openP0 必须显式为整数 0"
            )
        if not _declared_file_exists(state_path, review):
            invalid.append(
                "review.status=passed 时 review.file 必须声明且文件存在"
            )
    elif review.get("status") == "disputed" and not unresolved_disputes:
        invalid.append(
            "review.status=disputed 时 blockers 必须包含未解决的重大评审争议标记"
        )

    return invalid


def _review_and_validation_evidence(
    state_path: Path,
    state: dict[str, Any],
    *,
    require_validation_passed: bool,
) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    invalid: list[str] = []
    review = _section(state, "review")
    validation = _section(state, "validation")
    prd = _section(state, "prd")

    if review.get("status") != "passed":
        missing.append("review.status 必须为 passed")
    open_p0 = review.get("openP0")
    if not isinstance(open_p0, int) or isinstance(open_p0, bool):
        invalid.append("review.openP0 必须显式为整数")
    elif open_p0 != 0:
        missing.append("review.openP0 必须为 0")
    review_missing, review_invalid, _ = _artifact_evidence(
        state_path, "review", review, require_file=True, require_version=True
    )
    missing.extend(review_missing)
    invalid.extend(review_invalid)

    if require_validation_passed and validation.get("status") != "passed":
        missing.append("validation.status 必须为 passed")
    if validation.get("status") == "passed":
        validation_missing, validation_invalid, _ = _artifact_evidence(
            state_path,
            "validation",
            validation,
            require_file=True,
            require_version=False,
        )
        missing.extend(validation_missing)
        invalid.extend(validation_invalid)
        target_version = validation.get("targetPrdVersion")
        if not _nonempty(target_version):
            missing.append("validation.targetPrdVersion 不得为空")
        elif target_version != prd.get("version"):
            missing.append(
                "validation.targetPrdVersion 必须与 prd.version 一致"
            )
    return missing, invalid


def _validate_research_and_summary_prerequisites(
    state_path: Path,
    state: dict[str, Any],
) -> tuple[list[str], list[str], str | None]:
    """Validate formal research and confirmed requirement-summary evidence."""
    missing: list[str] = []
    invalid: list[str] = []
    return_stage: str | None = None

    research_missing, research_invalid = validate_research_context(
        state_path, _section(state, "projectContext")
    )
    missing.extend(research_missing)
    invalid.extend(research_invalid)
    if research_missing or research_invalid:
        return_stage = "requirement_discovery"

    summary = _section(state, "requirementSummary")
    summary_has_issue = summary.get("status") != "confirmed"
    if summary_has_issue:
        missing.append("requirementSummary.status 必须为 confirmed")
    artifact_missing, artifact_invalid, _ = _artifact_evidence(
        state_path,
        "requirementSummary",
        summary,
        require_file=True,
        require_version=True,
    )
    missing.extend(artifact_missing)
    invalid.extend(artifact_invalid)
    raw_summary_file = summary.get("file")
    summary_filename_invalid: list[str] = []
    if _nonempty(raw_summary_file) and Path(raw_summary_file).name not in SUMMARY_FILENAMES:
        allowed = ", ".join(sorted(SUMMARY_FILENAMES))
        summary_filename_invalid.append(
            f"requirementSummary.file 必须是允许的摘要产物：{allowed}"
        )
        invalid.extend(summary_filename_invalid)
    if return_stage is None and (
        summary_has_issue
        or artifact_missing
        or artifact_invalid
        or summary_filename_invalid
    ):
        return_stage = "requirement_confirmation"

    return missing, invalid, return_stage


def _validate_prototype_prd_prerequisite(
    state_path: Path,
    state: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Validate the required-or-waived prototype branch for formal PRD work."""
    missing: list[str] = []
    invalid: list[str] = []
    prototype = _section(state, "prototype")

    if prototype.get("applicability") == "required":
        if prototype.get("status") != "confirmed":
            missing.append("prototype.status 必须为 confirmed")
        artifact_missing, artifact_invalid, prototype_file = _artifact_evidence(
            state_path,
            "prototype",
            prototype,
            require_file=True,
            require_version=True,
        )
        missing.extend(artifact_missing)
        invalid.extend(artifact_invalid)
        if not _nonempty(prototype.get("confirmedAt")):
            missing.append("prototype.confirmedAt 不得为空")
        if prototype_file is not None and prototype_file.is_file():
            try:
                meta = read_prototype_meta(prototype_file)
                if meta.get("prototypeStatus") != "Confirmed":
                    missing.append(
                        "prototype-meta.prototypeStatus 必须为 Confirmed"
                    )
                if meta.get("prototypeVersion") != prototype.get("version"):
                    missing.append(
                        "prototype-meta.prototypeVersion 必须与 prototype.version 一致"
                    )
                meta_check = classify_prototype_meta(meta)
                if meta_check.status != "COMPLETE":
                    details = (
                        meta_check.missing_fields
                        + meta_check.invalid_fields
                        + meta_check.duplicate_ids
                    )
                    missing.append(
                        "prototype-meta 为 INCOMPLETE，"
                        "需定向回读相关 HTML 并补齐后重新分类: "
                        + ", ".join(details)
                    )
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                missing.append(
                    "prototype-meta 为 INVALID，"
                    f"需定向回读相关 HTML 并补齐: {exc}"
                )
    elif prototype.get("applicability") == "not_applicable":
        if prototype.get("status") != "waived":
            missing.append("prototype.status 必须为 waived")
        for field_name in ("waiverReason", "approvedBy", "approvedAt"):
            if not _nonempty(prototype.get(field_name)):
                missing.append(f"prototype.{field_name} 不得为空")

    return missing, invalid


def validate_formal_requirement_prerequisites(
    state_path: Path,
    state: dict[str, Any],
) -> tuple[list[str], list[str], str | None]:
    """Validate prerequisites inherited by every formal downstream gate."""
    missing, invalid, return_stage = _validate_research_and_summary_prerequisites(
        state_path, state
    )
    prototype_missing, prototype_invalid = _validate_prototype_prd_prerequisite(
        state_path, state
    )
    missing.extend(prototype_missing)
    invalid.extend(prototype_invalid)
    if return_stage is None and (prototype_missing or prototype_invalid):
        return_stage = "prototype"
    return missing, invalid, return_stage


FORMAL_DOWNSTREAM_TARGETS = frozenset(
    {"prd", "review", "validation", "final", "publish", "delivery"}
)


RETURN_STAGES = {
    "prototype": "requirement_confirmation",
    "prd": "prototype",
    "review": "prd",
    "validation": "review",
    "final": "validation",
    "publish": "final",
    "delivery": "delivery",
}


def validate_gate(state_path: Path, target: str) -> GateResult:
    state = load_state(state_path)
    requirement = _section(state, "requirement")
    current_stage = str(requirement.get("currentStage", ""))
    return_stage = RETURN_STAGES[target]
    result = GateResult(
        result="PASS",
        target=target,
        current_stage=current_stage,
        return_to_stage=return_stage,
    )

    result.invalid_fields.extend(validate_structure(state))
    declared_missing, declared_invalid = _validate_declared_paths(state_path, state)
    result.missing_conditions.extend(declared_missing)
    result.invalid_fields.extend(declared_invalid)
    result.invalid_fields.extend(validate_cross_field_consistency(state_path, state))
    research_has_missing = False
    research_has_invalid = False
    if target == "prototype":
        prerequisite_missing, prerequisite_invalid, prerequisite_return = (
            _validate_research_and_summary_prerequisites(state_path, state)
        )
    elif target in FORMAL_DOWNSTREAM_TARGETS:
        prerequisite_missing, prerequisite_invalid, prerequisite_return = (
            validate_formal_requirement_prerequisites(state_path, state)
        )
    else:
        prerequisite_missing, prerequisite_invalid, prerequisite_return = [], [], None

    research_missing, research_invalid = validate_research_context(
        state_path, _section(state, "projectContext")
    )
    research_has_missing = bool(research_missing) and (
        target == "prototype" or target in FORMAL_DOWNSTREAM_TARGETS
    )
    research_has_invalid = bool(research_invalid) and (
        target == "prototype" or target in FORMAL_DOWNSTREAM_TARGETS
    )
    result.missing_conditions.extend(prerequisite_missing)
    result.invalid_fields.extend(prerequisite_invalid)
    if prerequisite_return is not None:
        result.return_to_stage = prerequisite_return

    if result.invalid_fields:
        result.result = "INVALID_STATE"
        result.next_action = "修复状态结构或非法字段后重新运行门禁。"
        return result

    summary = _section(state, "requirementSummary")
    prototype = _section(state, "prototype")
    prd = _section(state, "prd")
    validation = _section(state, "validation")
    delivery = _section(state, "delivery")

    if target == "prototype":
        if prototype.get("applicability") != "required":
            result.missing_conditions.append(
                "prototype.applicability 必须为 required；"
                "not_applicable 路径不得进入原型生成"
            )

    elif target == "prd":
        # Common formal prerequisites were checked before target-specific rules.
        pass

    elif target == "review":
        if prd.get("status") not in {"draft", "in_review"}:
            result.missing_conditions.append(
                "prd.status 必须为 draft 或 in_review"
            )
        missing, invalid, _ = _artifact_evidence(
            state_path, "prd", prd, require_file=True, require_version=True
        )
        result.missing_conditions.extend(missing)
        result.invalid_fields.extend(invalid)

    elif target == "validation":
        missing, invalid = _review_and_validation_evidence(
            state_path, state, require_validation_passed=False
        )
        result.missing_conditions.extend(missing)
        result.invalid_fields.extend(invalid)
        prd_missing, prd_invalid, _ = _artifact_evidence(
            state_path, "prd", prd, require_file=True, require_version=True
        )
        result.missing_conditions.extend(prd_missing)
        result.invalid_fields.extend(prd_invalid)

    elif target == "final":
        missing, invalid = _review_and_validation_evidence(
            state_path, state, require_validation_passed=True
        )
        result.missing_conditions.extend(missing)
        result.invalid_fields.extend(invalid)
        prd_missing, prd_invalid, _ = _artifact_evidence(
            state_path, "prd", prd, require_file=True, require_version=True
        )
        result.missing_conditions.extend(prd_missing)
        result.invalid_fields.extend(prd_invalid)
        sync_missing, sync_invalid = _final_sync_evidence(state_path, prd)
        result.missing_conditions.extend(sync_missing)
        result.invalid_fields.extend(sync_invalid)

    elif target in {"publish", "delivery"}:
        if prd.get("status") != "final":
            result.missing_conditions.append("prd.status 必须为 final")
        prd_missing, prd_invalid, _ = _artifact_evidence(
            state_path, "prd", prd, require_file=True, require_version=True
        )
        result.missing_conditions.extend(prd_missing)
        result.invalid_fields.extend(prd_invalid)
        missing, invalid = _review_and_validation_evidence(
            state_path, state, require_validation_passed=True
        )
        result.missing_conditions.extend(missing)
        result.invalid_fields.extend(invalid)

        if (
            delivery.get("required") is False
            and not result.missing_conditions
            and not result.invalid_fields
        ):
            result.result = "NOT_REQUIRED"
            result.next_action = "项目未要求飞书交付；PRD 正式流程已完成。"
            return result
        if target == "delivery":
            if delivery.get("status") != "published":
                result.missing_conditions.append(
                    "delivery.status 必须为 published；交付未完成不回退 PRD"
                )
            delivery_missing, delivery_invalid, _ = _artifact_evidence(
                state_path,
                "delivery",
                delivery,
                require_file=True,
                require_version=False,
            )
            result.missing_conditions.extend(delivery_missing)
            result.invalid_fields.extend(delivery_invalid)
            if not _nonempty(delivery.get("publishedAt")):
                result.missing_conditions.append("delivery.publishedAt 不得为空")

    if result.invalid_fields:
        result.result = "INVALID_STATE"
        if research_has_invalid:
            result.return_to_stage = "requirement_discovery"
            result.next_action = "返回 requirement_discovery 修复调研状态或证据后重新运行门禁。"
        else:
            result.next_action = "修复状态结构或非法字段后重新运行门禁。"
    elif result.missing_conditions:
        result.result = "BLOCKED"
        if research_has_missing:
            result.return_to_stage = "requirement_discovery"
        result.next_action = (
            f"返回 {result.return_to_stage} 补齐缺失条件，再重跑 "
            f"check-stage-gate.py --target {target}。"
        )
    else:
        result.next_action = "允许进入目标阶段。"
    return result


def emit(result: GateResult, state_path: Path, as_json: bool) -> int:
    payload = {
        "result": result.result,
        "target": result.target,
        "currentStage": result.current_stage,
        "missingConditions": result.missing_conditions,
        "invalidFields": result.invalid_fields,
        "returnToStage": result.return_to_stage,
        "nextAction": result.next_action,
        "state": str(state_path),
    }
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return result.exit_code

    print(result.result)
    print(f"target: {result.target}")
    print(f"currentStage: {result.current_stage}")
    print("missingConditions:")
    for item in result.missing_conditions:
        print(f"- {item}")
    print("invalidFields:")
    for item in result.invalid_fields:
        print(f"- {item}")
    print(f"returnToStage: {result.return_to_stage}")
    print(f"nextAction: {result.next_action}")
    return result.exit_code


def invalid_result(target: str, message: str) -> GateResult:
    return GateResult(
        result="INVALID_STATE",
        target=target,
        current_stage="",
        invalid_fields=[message],
        return_to_stage="state_repair",
        next_action="修复状态文件后重新运行门禁。",
    )


