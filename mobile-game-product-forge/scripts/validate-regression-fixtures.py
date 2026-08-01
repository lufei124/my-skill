#!/usr/bin/env python3
"""Validate routing and capability regression fixtures without third-party dependencies."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROUTING = ROOT / "fixtures" / "routing-regression-cases.json"
CAPABILITY = ROOT / "fixtures" / "capability-regression-cases.json"

SKILLS = {
    "mobile-game-product-forge",
    "setup-mobile-game-product-forge",
    "game-requirement-discovery",
    "game-prototype",
    "game-prd-writing",
    "game-prd-review",
    "game-prd-publish",
    "game-analytics-design",
    "game-knowledge-maintenance-proposal",
}
ROUTING_MODES = {"formal", "narrow_task", "explicit", "user_action_required"}
# 输入风格：真实用户很少说教科书式的完整句。全是 textbook 的夹具全绿，
# 只证明「说明书式表达」能被正确路由，掩盖窄任务与正式流程的边界判定。
ROUTING_STYLES = {"textbook", "colloquial", "mixed_language", "explicit_invocation"}
# 现状下限（当前 4 / 1 / 1）。目标见 docs/capability-regression.md：
# 非 textbook 样本占比逐步提高到 1/3；新增夹具时口语类不少于三分之一。
MIN_COLLOQUIAL = 4
MIN_MIXED_LANGUAGE = 1
MIN_AMBIGUOUS = 1
COMPLEXITIES = {"L1", "L2", "L3", "narrow_task"}
PROTOTYPE = {"required", "not_applicable", "unknown"}
REQUIRED_CAPABILITY_CATEGORIES = {
    "l1_config_change",
    "l2_new_ui",
    "l2_no_ui_backend_rule",
    "l3_payment_subscription",
    "historical_module_iteration",
    "source_conflict",
    "independent_prd_review",
    "historical_prototype_reuse",
    "multi_module_prd_structure",
    "diagram_selection",
    "config_without_ops_backend",
}
REQUIRED_METRICS = {
    "criticalRuleOmissions",
    "unsupportedInferences",
    "clarifyingQuestionQuality",
    "decisionRuleAcceptanceCoverage",
    "prototypePrdDrift",
    "reviewP0P1Findings",
    "inputTokens",
    "elapsedSeconds",
    "filesRead",
    "fullHtmlReads",
}


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        fail(f"missing fixture: {path.relative_to(ROOT)}")
        raise exc
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(data, dict):
        fail(f"fixture root must be object: {path.relative_to(ROOT)}")
    if data.get("schemaVersion") != "1.0":
        fail(f"unsupported schemaVersion in {path.relative_to(ROOT)}")
    return data


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_routing(data: dict[str, Any]) -> int:
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) < 15:
        fail("routing fixture must contain at least 15 cases")
    ids: set[str] = set()
    seen_skills: set[str] = set()
    seen_categories: set[str] = set()
    styles: dict[str, int] = {}
    broad_root = 0
    for i, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(f"routing case[{i}] must be object")
        cid = case.get("id")
        if not nonempty(cid) or cid in ids:
            fail(f"routing case[{i}] has missing/duplicate id")
        ids.add(cid)
        for key in ("category", "request", "expectedSkill", "executionMode", "reason", "style"):
            if not nonempty(case.get(key)):
                fail(f"{cid}: missing non-empty {key}")
        if case["style"] not in ROUTING_STYLES:
            fail(f"{cid}: invalid style {case['style']} (expected one of {sorted(ROUTING_STYLES)})")
        skill = case["expectedSkill"]
        if skill not in SKILLS:
            fail(f"{cid}: unknown expectedSkill {skill}")
        seen_skills.add(skill)
        seen_categories.add(case["category"])
        styles[case["style"]] = styles.get(case["style"], 0) + 1
        if case["executionMode"] not in ROUTING_MODES:
            fail(f"{cid}: invalid executionMode")
        if case["category"] == "broad_formal":
            broad_root += 1
            if skill != "mobile-game-product-forge" or case["executionMode"] != "formal":
                fail(f"{cid}: broad_formal must route to root formal workflow")
        if skill != "mobile-game-product-forge" and case["category"] not in {"setup", "publish_only"}:
            if case["executionMode"] != "narrow_task":
                fail(f"{cid}: independently routed stage skill must be narrow_task")
        # setup is disable-model-invocation: true, so it is only reachable by an
        # explicit user invocation. A natural-language init request must NOT expect
        # routing to setup; it belongs to setup_guarded and expects a handoff prompt.
        if case["category"] == "setup":
            if skill != "setup-mobile-game-product-forge" or case["executionMode"] != "explicit":
                fail(f"{cid}: setup case must expect explicit invocation of the setup skill")
            if not case["request"].lstrip().startswith(("$", "/")):
                fail(
                    f"{cid}: setup is user-invoked only; request must be an explicit "
                    "invocation ($/ prefixed), not natural language"
                )
        if case["category"] == "setup_guarded":
            if skill != "mobile-game-product-forge" or case["executionMode"] != "user_action_required":
                fail(f"{cid}: setup_guarded must expect the root orchestrator to hand off, not route to setup")
        if case["executionMode"] == "user_action_required" and not nonempty(case.get("expectedBehavior")):
            fail(f"{cid}: user_action_required needs a non-empty expectedBehavior")
    if broad_root < 5:
        fail("routing fixture needs at least five broad_formal root cases")
    if seen_skills != SKILLS:
        missing = sorted(SKILLS - seen_skills)
        fail(f"routing fixture does not cover all skills; missing {missing}")
    for required in ("setup", "setup_guarded"):
        if required not in seen_categories:
            fail(f"routing fixture must keep a '{required}' case (setup is user-invoked only)")
    if styles.get("colloquial", 0) < MIN_COLLOQUIAL:
        fail(
            f"routing fixture needs at least {MIN_COLLOQUIAL} colloquial cases "
            f"(got {styles.get('colloquial', 0)}); all-textbook inputs only prove that "
            "manual-style phrasing routes correctly"
        )
    if styles.get("mixed_language", 0) < MIN_MIXED_LANGUAGE:
        fail(f"routing fixture needs at least {MIN_MIXED_LANGUAGE} mixed_language case")
    if sum(1 for c in cases if c["category"] == "ambiguous_reference") < MIN_AMBIGUOUS:
        fail(
            "routing fixture needs at least one 'ambiguous_reference' case: the expected "
            "behavior is asking the owner to pick, not routing to a guessed requirement dir"
        )
    for case in cases:
        if case["category"] == "ambiguous_reference":
            if case["expectedSkill"] != "mobile-game-product-forge" or case["executionMode"] != "user_action_required":
                fail(f"{case['id']}: ambiguous_reference must expect a clarification, not a route")
    non_textbook = len(cases) - styles.get("textbook", 0)
    print(
        f"  routing input styles: {styles} "
        f"(non-textbook {non_textbook}/{len(cases)} = {non_textbook * 100 // len(cases)}%, target 33%)"
    )
    return len(cases)


def string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(nonempty(item) for item in value):
        fail(f"{label} must be a non-empty string array")
    return value


def validate_capability(data: dict[str, Any]) -> int:
    metrics = data.get("metrics")
    if not isinstance(metrics, list) or set(metrics) != REQUIRED_METRICS:
        fail("capability metrics must match the required measurement set")
    cases = data.get("cases")
    if not isinstance(cases, list) or len(cases) != 11:
        fail("capability fixture must contain exactly 11 cases")
    ids: set[str] = set()
    categories: set[str] = set()
    by_category: dict[str, dict[str, Any]] = {}
    for i, case in enumerate(cases):
        if not isinstance(case, dict):
            fail(f"capability case[{i}] must be object")
        cid = case.get("id")
        if not nonempty(cid) or cid in ids:
            fail(f"capability case[{i}] has missing/duplicate id")
        ids.add(cid)
        for key in ("category", "name", "request"):
            if not nonempty(case.get(key)):
                fail(f"{cid}: missing non-empty {key}")
        category = case["category"]
        categories.add(category)
        by_category[category] = case
        expected = case.get("expected")
        if not isinstance(expected, dict):
            fail(f"{cid}: expected must be object")
        if expected.get("entrySkill") not in SKILLS:
            fail(f"{cid}: invalid entrySkill")
        if expected.get("complexity") not in COMPLEXITIES:
            fail(f"{cid}: invalid complexity")
        if expected.get("prototypeApplicability") not in PROTOTYPE:
            fail(f"{cid}: invalid prototypeApplicability")
        string_list(expected.get("requiredEvidence"), f"{cid}.requiredEvidence")
        string_list(expected.get("requiredBehaviors"), f"{cid}.requiredBehaviors")
        string_list(expected.get("forbiddenBehaviors"), f"{cid}.forbiddenBehaviors")
    if categories != REQUIRED_CAPABILITY_CATEGORIES:
        fail(f"capability categories mismatch: {sorted(categories)}")

    if by_category["l2_new_ui"]["expected"]["prototypeApplicability"] != "required":
        fail("l2_new_ui must require prototype")
    if by_category["l2_no_ui_backend_rule"]["expected"]["prototypeApplicability"] != "not_applicable":
        fail("l2_no_ui_backend_rule must allow waiver path")
    payment = by_category["l3_payment_subscription"]["expected"]
    required_payment_evidence = {
        "currentIntegrationVersion",
        "targetVersion",
        "targetRegionPolicy",
        "targetReleaseDatePolicy",
        "sourceVersionDocs",
        "targetVersionDocs",
        "officialMigrationGuide",
    }
    if not required_payment_evidence.issubset(set(payment["requiredEvidence"])):
        fail("payment case lacks region/date/version-matched official evidence")
    review = by_category["independent_prd_review"]["expected"]
    if review["entrySkill"] != "game-prd-review" or review["complexity"] != "narrow_task":
        fail("independent review must route to game-prd-review narrow_task")
    multi = by_category["multi_module_prd_structure"]["expected"]
    if "splitByClientServerDatabase" not in multi["forbiddenBehaviors"]:
        fail("multi-module case must forbid technical-layer splitting")
    diagrams = by_category["diagram_selection"]["expected"]
    if "generateAllDiagramTypes" not in diagrams["forbiddenBehaviors"]:
        fail("diagram case must forbid mechanical all-diagram generation")
    config = by_category["config_without_ops_backend"]["expected"]
    if "generateOperationsBackend" not in config["forbiddenBehaviors"]:
        fail("config case must forbid operations-backend design")
    return len(cases)


def main() -> int:
    try:
        routing_count = validate_routing(load(ROUTING))
        capability_count = validate_capability(load(CAPABILITY))
    except ValueError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: {routing_count} routing cases + {capability_count} capability cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
