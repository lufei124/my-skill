#!/usr/bin/env python3
"""Self-tests for the mobile-game-product-forge stage-gate runtime."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from stage_gate_core import (
    PASS,
    classify_prototype_meta,
    complexity_policy,
    extract_prototype_meta_json,
    validate_gate,
)

def self_test() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        prototype_dir = root / "02-prototype"
        prototype_dir.mkdir()
        prototype = prototype_dir / "index.html"
        complete_meta: dict[str, Any] = {
            "schemaVersion": "1.0",
            "requirementName": "测试需求",
            "module": "测试模块",
            "prototypeVersion": "v1.0",
            "prototypeStatus": "Confirmed",
            "device": {"orientation": "portrait", "platform": ["iOS", "Android"]},
            "scope": {"included": ["主流程"], "excluded": ["后台配置"]},
            "pages": [{"id": "home", "name": "主页"}],
            "scenarios": [
                {
                    "id": "main_flow",
                    "entry": "home",
                    "flow": ["点击开始", "展示结果"],
                }
            ],
            "states": [{"id": "ready", "description": "可开始"}],
            "decisions": [
                {"id": "D-001", "status": "已确认", "summary": "使用主流程"}
            ],
        }
        prototype.write_text(
            '<script id="prototype-meta" type="application/json">'
            + json.dumps(complete_meta, ensure_ascii=False)
            + "</script>",
            encoding="utf-8",
        )
        artifacts = {
            "00-research-findings.md": (
                "# 需求调研结论\n\n"
                "## 2. 当前现状\n\n当前实现已核验。\n\n"
                "## 3. 目标状态\n\n目标规则已记录。\n\n"
                "## 4. 当前状态与目标状态差异\n\n存在一项规则调整。\n\n"
                "## 10. 风险\n\n当前无未暴露高风险。\n\n"
                "## 11. 来源索引\n\n| 结论 | 来源 |\n|---|---|\n"
                "| 当前实现 | 测试环境 |\n"
            ),
            "00-project-context.md": "# Legacy Project Context\n",
            "01-requirement-summary.md": "# 需求理解与方案摘要\n",
            "01-requirement-decisions.md": "# Requirement Summary\n",
            "03-prd-v0.1.md": "# PRD\n",
            "04-review-report.md": "# Review\n",
            "06-lint-report.md": "# Validation\n",
            "08-delivery-record.md": "# Delivery\n",
        }
        for filename, content in artifacts.items():
            (root / filename).write_text(content, encoding="utf-8")
        docs_prd_dir = root / "docs" / "prd"
        docs_prd_dir.mkdir(parents=True)
        synced_final = "docs/prd/测试需求.md"
        (root / synced_final).write_text("# PRD final synced\n", encoding="utf-8")
        state_path = root / "00-stage-state.json"

        base_state: dict[str, Any] = {
            "schemaVersion": "1.1",
            "requirement": {
                "name": "测试需求",
                "mode": "existing_module",
                "complexity": "L2",
                "owner": "产品负责人",
                "currentStage": "prd",
            },
            "projectContext": {
                "status": "completed",
                "file": "00-research-findings.md",
                "version": "v1.0",
            },
            "requirementSummary": {
                "status": "confirmed",
                "file": "01-requirement-summary.md",
                "version": "v1.0",
            },
            "prototype": {
                "applicability": "required",
                "status": "confirmed",
                "file": "02-prototype/index.html",
                "version": "v1.0",
                "confirmedAt": "2026-07-26T10:00:00+08:00",
                "waiverReason": "",
                "approvedBy": "",
                "approvedAt": "",
            },
            "prd": {"status": "draft", "file": "03-prd-v0.1.md", "version": "v0.1"},
            "review": {
                "status": "passed",
                "file": "04-review-report.md",
                "version": "v1.0",
                "openP0": 0,
            },
            "validation": {
                "status": "passed",
                "file": "06-lint-report.md",
                "targetPrdVersion": "v0.1",
            },
            "delivery": {
                "required": False,
                "channel": "feishu",
                "status": "not_required",
                "file": "",
                "publishedAt": "",
            },
            "knowledgeProposal": {"status": "not_evaluated", "file": ""},
            "blockers": [],
            "nextAction": "",
            "updatedAt": "2026-07-26T10:00:00+08:00",
        }

        def run_case(
            label: str, target: str, expected: str, state: dict[str, Any]
        ) -> bool:
            state_path.write_text(
                json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            result = validate_gate(state_path, target)
            if result.result != expected:
                print(
                    f"self-test failed [{label}]: expected={expected} "
                    f"actual={result.result} missing={result.missing_conditions} "
                    f"invalid={result.invalid_fields}",
                    file=sys.stderr,
                )
                return False
            return True

        cases: list[tuple[str, str, str, dict[str, Any]]] = [
            ("required prototype confirmed", "prd", "PASS", copy.deepcopy(base_state)),
            ("research complete before prototype", "prototype", "PASS", copy.deepcopy(base_state)),
        ]

        research_not_started = copy.deepcopy(base_state)
        research_not_started["projectContext"] = {
            "status": "not_started",
            "file": "",
            "version": "",
        }
        cases.append(
            ("research not started blocks prototype", "prototype", "BLOCKED", research_not_started)
        )

        research_file_empty = copy.deepcopy(base_state)
        research_file_empty["projectContext"]["file"] = ""
        cases.append(
            ("completed research file empty", "prototype", "INVALID_STATE", research_file_empty)
        )

        research_file_missing = copy.deepcopy(base_state)
        research_file_missing["projectContext"]["file"] = "missing/00-research-findings.md"
        cases.append(
            ("completed research file missing", "prototype", "INVALID_STATE", research_file_missing)
        )

        research_version_empty = copy.deepcopy(base_state)
        research_version_empty["projectContext"]["version"] = ""
        cases.append(
            ("completed research version empty", "prd", "INVALID_STATE", research_version_empty)
        )

        legacy_research = copy.deepcopy(base_state)
        legacy_research["projectContext"]["file"] = "00-project-context.md"
        cases.append(("legacy research artifact", "prototype", "PASS", legacy_research))

        empty_research_dir = root / "empty-research"
        empty_research_dir.mkdir()
        (empty_research_dir / "00-research-findings.md").write_text(
            "", encoding="utf-8"
        )
        empty_research = copy.deepcopy(base_state)
        empty_research["projectContext"]["file"] = (
            "empty-research/00-research-findings.md"
        )
        cases.append(
            (
                "empty research artifact",
                "prototype",
                "INVALID_STATE",
                empty_research,
            )
        )

        incomplete_research_dir = root / "incomplete-research"
        incomplete_research_dir.mkdir()
        (incomplete_research_dir / "00-research-findings.md").write_text(
            "# 需求调研结论\n\n## 2. 当前现状\n\n只有现状。\n",
            encoding="utf-8",
        )
        incomplete_research = copy.deepcopy(base_state)
        incomplete_research["projectContext"]["file"] = (
            "incomplete-research/00-research-findings.md"
        )
        cases.append(
            (
                "research artifact missing minimum headings",
                "prd",
                "INVALID_STATE",
                incomplete_research,
            )
        )

        empty_legacy_dir = root / "empty-legacy"
        empty_legacy_dir.mkdir()
        (empty_legacy_dir / "00-project-context.md").write_text(
            "", encoding="utf-8"
        )
        empty_legacy = copy.deepcopy(base_state)
        empty_legacy["projectContext"]["file"] = (
            "empty-legacy/00-project-context.md"
        )
        cases.append(
            (
                "empty legacy research artifact",
                "prototype",
                "INVALID_STATE",
                empty_legacy,
            )
        )

        unrelated_research_file = root / "notes.md"
        unrelated_research_file.write_text("# Notes\n", encoding="utf-8")
        unrelated_research = copy.deepcopy(base_state)
        unrelated_research["projectContext"]["file"] = "notes.md"
        cases.append(
            ("unrelated research filename", "prd", "INVALID_STATE", unrelated_research)
        )

        l1_research = copy.deepcopy(base_state)
        l1_research["requirement"]["complexity"] = "L1"
        cases.append(("L1 compact research", "prd", "PASS", l1_research))

        l1_without_research = copy.deepcopy(l1_research)
        l1_without_research["projectContext"] = {
            "status": "not_started",
            "file": "",
            "version": "",
        }
        cases.append(("L1 cannot skip research", "prd", "BLOCKED", l1_without_research))

        not_applicable_prototype_target = copy.deepcopy(base_state)
        not_applicable_prototype_target["prototype"].update(
            {
                "applicability": "not_applicable",
                "status": "not_started",
                "file": "",
                "version": "",
                "confirmedAt": "",
            }
        )
        cases.append(
            (
                "not applicable does not enter prototype generation",
                "prototype",
                "BLOCKED",
                not_applicable_prototype_target,
            )
        )

        required_missing = copy.deepcopy(base_state)
        required_missing["prototype"]["file"] = ""
        cases.append(("required prototype missing", "prd", "BLOCKED", required_missing))

        version_mismatch = copy.deepcopy(base_state)
        version_mismatch["prototype"]["version"] = "v1.1"
        cases.append(("prototype version mismatch", "prd", "BLOCKED", version_mismatch))

        incomplete_prototype = prototype_dir / "incomplete.html"
        incomplete_meta = copy.deepcopy(complete_meta)
        del incomplete_meta["module"]
        incomplete_prototype.write_text(
            '<script id="prototype-meta" type="application/json">'
            + json.dumps(incomplete_meta, ensure_ascii=False)
            + "</script>",
            encoding="utf-8",
        )
        incomplete_state = copy.deepcopy(base_state)
        incomplete_state["prototype"]["file"] = "02-prototype/incomplete.html"
        cases.append(
            ("new prototype metadata incomplete", "prd", "BLOCKED", incomplete_state)
        )

        invalid_prototype = prototype_dir / "invalid.html"
        invalid_prototype.write_text(
            '<script id="prototype-meta" type="application/json">{bad json</script>',
            encoding="utf-8",
        )
        invalid_prototype_state = copy.deepcopy(base_state)
        invalid_prototype_state["prototype"]["file"] = "02-prototype/invalid.html"
        cases.append(
            ("required invalid metadata", "prd", "BLOCKED", invalid_prototype_state)
        )

        legacy_prototype = prototype_dir / "legacy.html"
        legacy_prototype.write_text(
            '<script id="prototype-meta" type="application/json">'
            '{"prototypeStatus":"Confirmed","prototypeVersion":"v1.0"}'
            "</script>",
            encoding="utf-8",
        )
        legacy_state = copy.deepcopy(base_state)
        legacy_state["prototype"]["file"] = "02-prototype/legacy.html"
        cases.append(
            ("legacy minimal metadata requires compatibility review", "prd", "BLOCKED", legacy_state)
        )

        waived = copy.deepcopy(base_state)
        waived["prototype"].update(
            {
                "applicability": "not_applicable",
                "status": "waived",
                "file": "",
                "version": "",
                "confirmedAt": "",
                "waiverReason": "仅调整服务端频控，无 UI 或交互变化",
                "approvedBy": "产品负责人",
                "approvedAt": "2026-07-26T10:00:00+08:00",
            }
        )
        cases.append(("prototype waiver", "prd", "PASS", waived))

        waiver_missing = copy.deepcopy(waived)
        waiver_missing["prototype"]["waiverReason"] = ""
        cases.append(("waiver reason missing", "prd", "BLOCKED", waiver_missing))

        waiver_approver_missing = copy.deepcopy(waived)
        waiver_approver_missing["prototype"]["approvedBy"] = ""
        cases.append(
            ("waiver approver missing", "prd", "BLOCKED", waiver_approver_missing)
        )

        waiver_time_missing = copy.deepcopy(waived)
        waiver_time_missing["prototype"]["approvedAt"] = ""
        cases.append(
            ("waiver approval time missing", "prd", "BLOCKED", waiver_time_missing)
        )

        open_p0_missing = copy.deepcopy(base_state)
        del open_p0_missing["review"]["openP0"]
        cases.append(
            ("review.openP0 missing", "validation", "INVALID_STATE", open_p0_missing)
        )
        cases.append(
            (
                "review passed without dispute and openP0 zero",
                "validation",
                "PASS",
                copy.deepcopy(base_state),
            )
        )

        passed_with_open_p0 = copy.deepcopy(base_state)
        passed_with_open_p0["review"]["openP0"] = 1
        cases.append(
            (
                "review passed with openP0",
                "validation",
                "INVALID_STATE",
                passed_with_open_p0,
            )
        )

        passed_with_dispute = copy.deepcopy(base_state)
        passed_with_dispute["blockers"] = [
            {
                "type": "major_review_dispute",
                "description": "两个合理商业化方案待产品负责人裁定",
                "status": "open",
            }
        ]
        cases.append(
            (
                "major dispute cannot be passed",
                "validation",
                "INVALID_STATE",
                passed_with_dispute,
            )
        )

        disputed = copy.deepcopy(base_state)
        disputed["review"]["status"] = "disputed"
        disputed["blockers"] = [
            {
                "type": "major_review_dispute",
                "description": "主流程变化待产品负责人裁定",
                "status": "open",
            }
        ]
        cases.append(
            (
                "disputed review cannot enter validation",
                "validation",
                "BLOCKED",
                disputed,
            )
        )
        cases.append(
            (
                "disputed review cannot enter final",
                "final",
                "BLOCKED",
                copy.deepcopy(disputed),
            )
        )

        disputed_without_marker = copy.deepcopy(base_state)
        disputed_without_marker["review"]["status"] = "disputed"
        cases.append(
            (
                "disputed review requires marker",
                "validation",
                "INVALID_STATE",
                disputed_without_marker,
            )
        )

        required_waived = copy.deepcopy(base_state)
        required_waived["prototype"]["status"] = "waived"
        cases.append(
            (
                "required prototype cannot be waived",
                "prd",
                "INVALID_STATE",
                required_waived,
            )
        )

        not_applicable_confirmed = copy.deepcopy(waived)
        not_applicable_confirmed["prototype"]["status"] = "confirmed"
        cases.append(
            (
                "not applicable prototype cannot be confirmed",
                "prd",
                "INVALID_STATE",
                not_applicable_confirmed,
            )
        )

        validation_mismatch = copy.deepcopy(base_state)
        validation_mismatch["prd"]["status"] = "final"
        validation_mismatch["validation"]["targetPrdVersion"] = "v0.2"
        cases.append(
            ("validation version mismatch", "final", "INVALID_STATE", validation_mismatch)
        )

        final_without_validation = copy.deepcopy(base_state)
        final_without_validation["prd"]["status"] = "final"
        final_without_validation["validation"]["status"] = "failed"
        cases.append(
            (
                "final PRD requires passed validation",
                "final",
                "INVALID_STATE",
                final_without_validation,
            )
        )

        final_locked = copy.deepcopy(base_state)
        final_locked["prd"]["status"] = "final"
        final_locked["prd"]["syncedTo"] = synced_final
        cases.append(
            (
                "final PRD blocks review gate until reopened",
                "review",
                "BLOCKED",
                final_locked,
            )
        )

        final_synced = copy.deepcopy(base_state)
        final_synced["prd"]["syncedTo"] = synced_final
        cases.append(
            ("final gate passes with synced final copy", "final", "PASS", final_synced)
        )

        final_without_sync = copy.deepcopy(base_state)
        cases.append(
            (
                "final gate requires synced final copy",
                "final",
                "BLOCKED",
                final_without_sync,
            )
        )

        final_sync_missing_file = copy.deepcopy(base_state)
        final_sync_missing_file["prd"]["syncedTo"] = "docs/prd/不存在.md"
        cases.append(
            (
                "final synced file must exist",
                "final",
                "BLOCKED",
                final_sync_missing_file,
            )
        )

        final_sync_escape = copy.deepcopy(base_state)
        final_sync_escape["prd"]["syncedTo"] = "/etc/passwd"
        cases.append(
            (
                "final synced file must stay within allowed roots",
                "final",
                "INVALID_STATE",
                final_sync_escape,
            )
        )

        final_status_without_sync = copy.deepcopy(base_state)
        final_status_without_sync["prd"]["status"] = "final"
        cases.append(
            (
                "final status requires synced evidence",
                "delivery",
                "INVALID_STATE",
                final_status_without_sync,
            )
        )

        reopened_final = copy.deepcopy(base_state)
        reopened_final["prd"]["status"] = "in_review"
        reopened_final["prd"]["version"] = "v0.2"
        reopened_final["validation"] = {
            "status": "not_started",
            "file": "",
            "targetPrdVersion": "",
        }
        cases.append(
            (
                "reopened final passes review gate",
                "review",
                "PASS",
                reopened_final,
            )
        )

        legacy_summary = copy.deepcopy(base_state)
        legacy_summary["requirementSummary"]["file"] = "01-requirement-decisions.md"
        cases.append(
            ("legacy summary artifact", "prd", "PASS", legacy_summary)
        )

        summary_wrong_file = copy.deepcopy(base_state)
        summary_wrong_file["requirementSummary"]["file"] = "03-prd-v0.1.md"
        cases.append(
            (
                "summary file must use allowed filenames",
                "prd",
                "INVALID_STATE",
                summary_wrong_file,
            )
        )

        delivery_false_published = copy.deepcopy(base_state)
        delivery_false_published["delivery"]["status"] = "published"
        cases.append(
            (
                "delivery false requires not_required",
                "delivery",
                "INVALID_STATE",
                delivery_false_published,
            )
        )

        delivery_true_not_required = copy.deepcopy(base_state)
        delivery_true_not_required["delivery"]["required"] = True
        cases.append(
            (
                "delivery true cannot be not_required",
                "delivery",
                "INVALID_STATE",
                delivery_true_not_required,
            )
        )

        not_required_before_final = copy.deepcopy(base_state)
        cases.append(
            (
                "delivery not required before final",
                "delivery",
                "BLOCKED",
                not_required_before_final,
            )
        )

        delivery_not_required = copy.deepcopy(base_state)
        delivery_not_required["prd"]["status"] = "final"
        delivery_not_required["prd"]["syncedTo"] = synced_final
        cases.append(
            (
                "delivery not required after final",
                "delivery",
                "NOT_REQUIRED",
                delivery_not_required,
            )
        )

        delivery_required = copy.deepcopy(base_state)
        delivery_required["prd"]["status"] = "final"
        delivery_required["prd"]["syncedTo"] = synced_final
        delivery_required["delivery"].update(
            {"required": True, "status": "not_started"}
        )
        cases.append(
            ("required delivery unpublished", "delivery", "BLOCKED", delivery_required)
        )

        delivery_published = copy.deepcopy(delivery_required)
        delivery_published["delivery"].update(
            {
                "status": "published",
                "file": "08-delivery-record.md",
                "publishedAt": "2026-07-26T10:30:00+08:00",
            }
        )
        cases.append(("required delivery published", "delivery", "PASS", delivery_published))

        downstream_without_research = copy.deepcopy(base_state)
        downstream_without_research["projectContext"] = {
            "status": "not_started",
            "file": "",
            "version": "",
        }
        for downstream_target in ("review", "validation", "final", "publish", "delivery"):
            cases.append(
                (
                    f"formal {downstream_target} inherits research prerequisite",
                    downstream_target,
                    "BLOCKED",
                    copy.deepcopy(downstream_without_research),
                )
            )

        cases.append(
            (
                "formal review accepts complete not_applicable waiver",
                "review",
                "PASS",
                copy.deepcopy(waived),
            )
        )
        cases.append(
            (
                "formal review inherits required metadata completeness",
                "review",
                "BLOCKED",
                copy.deepcopy(incomplete_state),
            )
        )

        for label, target, expected, state in cases:
            if not run_case(label, target, expected, state):
                return 1

        meta_output = extract_prototype_meta_json(prototype)
        extracted_meta = json.loads(meta_output)
        if extracted_meta.get("prototypeVersion") != "v1.0":
            print(
                "self-test failed: metadata extraction lost prototypeVersion",
                file=sys.stderr,
            )
            return 1

        complete_check = classify_prototype_meta(extracted_meta)
        if (
            complete_check.status != "COMPLETE"
            or complete_check.missing_fields
            or complete_check.invalid_fields
            or complete_check.duplicate_ids
        ):
            print(
                "self-test failed: complete metadata must classify COMPLETE",
                file=sys.stderr,
            )
            return 1

        missing_field_meta = copy.deepcopy(complete_meta)
        del missing_field_meta["module"]
        missing_check = classify_prototype_meta(missing_field_meta)
        if (
            missing_check.status != "INCOMPLETE"
            or missing_check.missing_fields != ["module"]
        ):
            print(
                "self-test failed: missing module must classify INCOMPLETE",
                file=sys.stderr,
            )
            return 1

        wrong_type_meta = copy.deepcopy(complete_meta)
        wrong_type_meta["scope"]["included"] = "主流程"
        wrong_type_check = classify_prototype_meta(wrong_type_meta)
        if (
            wrong_type_check.status != "INCOMPLETE"
            or "scope.included" not in wrong_type_check.invalid_fields
        ):
            print(
                "self-test failed: wrong scope.included type must be reported",
                file=sys.stderr,
            )
            return 1

        semantic_cases: list[tuple[str, dict[str, Any], str]] = []

        bad_schema_meta = copy.deepcopy(complete_meta)
        bad_schema_meta["schemaVersion"] = "nonsense"
        semantic_cases.append(("unsupported schemaVersion", bad_schema_meta, "schemaVersion"))

        bad_status_meta = copy.deepcopy(complete_meta)
        bad_status_meta["prototypeStatus"] = "Whatever"
        semantic_cases.append(("unsupported prototypeStatus", bad_status_meta, "prototypeStatus"))

        bad_orientation_meta = copy.deepcopy(complete_meta)
        bad_orientation_meta["device"]["orientation"] = "diagonal"
        semantic_cases.append(("invalid orientation", bad_orientation_meta, "device.orientation"))

        empty_platform_meta = copy.deepcopy(complete_meta)
        empty_platform_meta["device"]["platform"] = []
        semantic_cases.append(("empty platform", empty_platform_meta, "device.platform"))

        blank_scope_meta = copy.deepcopy(complete_meta)
        blank_scope_meta["scope"]["included"] = [" "]
        semantic_cases.append(("blank scope item", blank_scope_meta, "scope.included[0]"))

        bad_decision_status_meta = copy.deepcopy(complete_meta)
        bad_decision_status_meta["decisions"][0]["status"] = "Whatever"
        semantic_cases.append(
            ("invalid decision status", bad_decision_status_meta, "decisions[0].status")
        )

        empty_pages_meta = copy.deepcopy(complete_meta)
        empty_pages_meta["pages"] = []
        semantic_cases.append(("confirmed pages empty", empty_pages_meta, "pages"))

        empty_scenarios_meta = copy.deepcopy(complete_meta)
        empty_scenarios_meta["scenarios"] = []
        semantic_cases.append(("confirmed scenarios empty", empty_scenarios_meta, "scenarios"))

        empty_states_meta = copy.deepcopy(complete_meta)
        empty_states_meta["states"] = []
        semantic_cases.append(("confirmed states empty", empty_states_meta, "states"))

        blank_flow_meta = copy.deepcopy(complete_meta)
        blank_flow_meta["scenarios"][0]["flow"] = ["点击开始", " "]
        semantic_cases.append(
            ("blank scenario flow item", blank_flow_meta, "scenarios[0].flow[1]")
        )

        for label, semantic_meta, expected_invalid in semantic_cases:
            semantic_check = classify_prototype_meta(semantic_meta)
            if (
                semantic_check.status != "INCOMPLETE"
                or expected_invalid not in semantic_check.invalid_fields
                or semantic_check.as_payload().get("nextAction") != "read_relevant_html"
            ):
                print(
                    f"self-test failed: {label} must classify INCOMPLETE "
                    f"with invalid field {expected_invalid}; "
                    f"actual={semantic_check.as_payload()}",
                    file=sys.stderr,
                )
                return 1

        placeholder_cases: list[tuple[str, dict[str, Any], str]] = []

        placeholder_requirement_meta = copy.deepcopy(complete_meta)
        placeholder_requirement_meta["requirementName"] = "待补充"
        placeholder_cases.append(
            (
                "placeholder requirementName",
                placeholder_requirement_meta,
                "requirementName",
            )
        )

        placeholder_module_meta = copy.deepcopy(complete_meta)
        placeholder_module_meta["module"] = "TODO"
        placeholder_cases.append(
            ("placeholder module", placeholder_module_meta, "module")
        )

        placeholder_scope_meta = copy.deepcopy(complete_meta)
        placeholder_scope_meta["scope"]["included"] = ["TBD"]
        placeholder_cases.append(
            (
                "placeholder scope item",
                placeholder_scope_meta,
                "scope.included[0]",
            )
        )

        placeholder_page_meta = copy.deepcopy(complete_meta)
        placeholder_page_meta["pages"][0]["id"] = "示例"
        placeholder_cases.append(
            ("placeholder page id", placeholder_page_meta, "pages[0].id")
        )

        placeholder_scenario_meta = copy.deepcopy(complete_meta)
        placeholder_scenario_meta["scenarios"][0]["flow"] = ["待补充"]
        placeholder_cases.append(
            (
                "placeholder scenario flow",
                placeholder_scenario_meta,
                "scenarios[0].flow[0]",
            )
        )

        placeholder_state_meta = copy.deepcopy(complete_meta)
        placeholder_state_meta["states"][0]["description"] = "PLACEHOLDER"
        placeholder_cases.append(
            (
                "placeholder state description",
                placeholder_state_meta,
                "states[0].description",
            )
        )

        placeholder_decision_meta = copy.deepcopy(complete_meta)
        placeholder_decision_meta["decisions"][0]["summary"] = "待确认"
        placeholder_cases.append(
            (
                "placeholder decision summary",
                placeholder_decision_meta,
                "decisions[0].summary",
            )
        )

        for label, placeholder_meta, expected_invalid in placeholder_cases:
            placeholder_check = classify_prototype_meta(placeholder_meta)
            if (
                placeholder_check.status != "INCOMPLETE"
                or expected_invalid not in placeholder_check.invalid_fields
            ):
                print(
                    f"self-test failed: {label} must classify INCOMPLETE "
                    f"with invalid field {expected_invalid}; "
                    f"actual={placeholder_check.as_payload()}",
                    file=sys.stderr,
                )
                return 1

        pending_decision_meta = copy.deepcopy(complete_meta)
        pending_decision_meta["decisions"][0]["status"] = "待确认"
        pending_decision_check = classify_prototype_meta(pending_decision_meta)
        if pending_decision_check.status != "COMPLETE":
            print(
                "self-test failed: decision status 待确认 remains a legal enum; "
                f"actual={pending_decision_check.as_payload()}",
                file=sys.stderr,
            )
            return 1

        empty_device_meta = copy.deepcopy(complete_meta)
        empty_device_meta["device"] = {}
        empty_device_check = classify_prototype_meta(empty_device_meta)
        if (
            empty_device_check.status != "INCOMPLETE"
            or "device.orientation" not in empty_device_check.missing_fields
            or "device.platform" not in empty_device_check.missing_fields
        ):
            print(
                "self-test failed: empty device must report missing nested fields; "
                f"actual={empty_device_check.as_payload()}",
                file=sys.stderr,
            )
            return 1

        decisions_empty_meta = copy.deepcopy(complete_meta)
        decisions_empty_meta["decisions"] = []
        decisions_empty_check = classify_prototype_meta(decisions_empty_meta)
        if decisions_empty_check.status != "COMPLETE":
            print(
                "self-test failed: decisions may be explicitly empty; "
                f"actual={decisions_empty_check.as_payload()}",
                file=sys.stderr,
            )
            return 1

        duplicate_cases: list[tuple[str, dict[str, Any], str]] = []
        duplicate_page_meta = copy.deepcopy(complete_meta)
        duplicate_page_meta["pages"].append({"id": "home", "name": "重复主页"})
        duplicate_cases.append(("duplicate page id", duplicate_page_meta, "pages.id:home"))

        duplicate_scenario_meta = copy.deepcopy(complete_meta)
        duplicate_scenario_meta["scenarios"].append(
            {
                "id": "main_flow",
                "entry": "home",
                "flow": ["重复流程"],
            }
        )
        duplicate_cases.append(
            ("duplicate scenario id", duplicate_scenario_meta, "scenarios.id:main_flow")
        )

        duplicate_state_meta = copy.deepcopy(complete_meta)
        duplicate_state_meta["states"].append(
            {"id": "ready", "description": "重复状态"}
        )
        duplicate_cases.append(("duplicate state id", duplicate_state_meta, "states.id:ready"))

        duplicate_decision_meta = copy.deepcopy(complete_meta)
        duplicate_decision_meta["decisions"].append(
            {"id": "D-001", "status": "已确认", "summary": "重复决策"}
        )
        duplicate_cases.append(
            ("duplicate decision id", duplicate_decision_meta, "decisions.id:D-001")
        )

        for label, duplicate_meta, expected_duplicate in duplicate_cases:
            duplicate_check = classify_prototype_meta(duplicate_meta)
            if (
                duplicate_check.status != "INCOMPLETE"
                or expected_duplicate not in duplicate_check.duplicate_ids
                or expected_duplicate
                not in duplicate_check.as_payload().get("duplicateIds", [])
            ):
                print(
                    f"self-test failed: {label} must report {expected_duplicate}; "
                    f"actual={duplicate_check.as_payload()}",
                    file=sys.stderr,
                )
                return 1

        bad_decision_meta = copy.deepcopy(complete_meta)
        bad_decision_meta["decisions"][0]["id"] = "DECISION-1"
        bad_decision_check = classify_prototype_meta(bad_decision_meta)
        if (
            bad_decision_check.status != "INCOMPLETE"
            or "decisions[0].id" not in bad_decision_check.invalid_fields
        ):
            print(
                "self-test failed: invalid D-### must be reported",
                file=sys.stderr,
            )
            return 1

        legacy_minimal_meta = {
            "prototypeStatus": "Confirmed",
            "prototypeVersion": "v0.9",
        }
        legacy_check = classify_prototype_meta(legacy_minimal_meta)
        if (
            legacy_check.status != "INCOMPLETE"
            or "schemaVersion" not in legacy_check.missing_fields
        ):
            print(
                "self-test failed: legacy minimal metadata must use fallback",
                file=sys.stderr,
            )
            return 1
        if any(
            raw_marker in meta_output.lower()
            for raw_marker in ("<script", "<style", "<html", "function(")
        ):
            print(
                "self-test failed: metadata extraction leaked HTML/CSS/JavaScript",
                file=sys.stderr,
            )
            return 1

        missing_meta = root / "missing-meta.html"
        missing_meta.write_text("<html><body>No metadata</body></html>", encoding="utf-8")
        try:
            extract_prototype_meta_json(missing_meta)
        except ValueError:
            pass
        else:
            print(
                "self-test failed: missing prototype-meta must raise",
                file=sys.stderr,
            )
            return 1

        invalid_meta = root / "invalid-meta.html"
        invalid_meta.write_text(
            '<script id="prototype-meta" type="application/json">{bad json</script>',
            encoding="utf-8",
        )
        try:
            extract_prototype_meta_json(invalid_meta)
        except json.JSONDecodeError:
            pass
        else:
            print(
                "self-test failed: invalid prototype-meta JSON must raise",
                file=sys.stderr,
            )
            return 1

        non_object_meta = root / "non-object-meta.html"
        non_object_meta.write_text(
            '<script id="prototype-meta" type="application/json">[]</script>',
            encoding="utf-8",
        )
        try:
            extract_prototype_meta_json(non_object_meta)
        except ValueError:
            pass
        else:
            print(
                "self-test failed: non-object prototype-meta must raise",
                file=sys.stderr,
            )
            return 1

        state_path.write_text("{bad json", encoding="utf-8")
        try:
            validate_gate(state_path, "prd")
        except json.JSONDecodeError:
            pass
        else:
            print("self-test failed: invalid JSON must raise", file=sys.stderr)
            return 1

        for level, expected_review in (
            ("L1", "focused"),
            ("L2", "dynamic"),
            ("L3", "full"),
        ):
            policy = complexity_policy(level)
            if policy.get("review") != expected_review:
                print(
                    f"self-test failed: {level} review policy must be {expected_review}",
                    file=sys.stderr,
                )
                return 1

    metadata_case_count = (
        13
        + len(semantic_cases)
        + len(placeholder_cases)
        + len(duplicate_cases)
    )
    total_case_count = len(cases) + metadata_case_count + 1 + 3
    print(
        "check-stage-gate self-test: PASS "
        f"({len(cases)} gate cases + {metadata_case_count} metadata cases "
        f"+ 1 invalid-state JSON case + 3 complexity policies "
        f"= {total_case_count} cases)"
    )
    return PASS


