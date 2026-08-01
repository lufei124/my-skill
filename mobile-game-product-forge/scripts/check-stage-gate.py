#!/usr/bin/env python3
"""Validate mobile-game-product-forge formal workflow stage gates.

New formal requirements use references/stage-state.schema.json and
00-stage-state.json. Only Python's standard library is required. Historical
00-stage-state.yaml files are not modified or parsed by this validator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from stage_gate_core import (
    BLOCKED,
    INVALID_STATE,
    PASS,
    classify_prototype_meta,
    emit,
    invalid_result,
    read_prototype_meta,
    validate_gate,
)
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, help="Path to 00-stage-state.json")
    parser.add_argument(
        "--target",
        choices=[
            "prototype",
            "prd",
            "review",
            "validation",
            "final",
            "publish",
            "delivery",
        ],
        help="Target stage or delivery completion to validate",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--self-test", action="store_true", help="Run built-in tests")
    parser.add_argument(
        "--extract-prototype-meta",
        type=Path,
        metavar="INDEX_HTML",
        help="Classify prototype-meta and emit compact JSON without HTML source",
    )
    args = parser.parse_args()

    if args.self_test and args.extract_prototype_meta is not None:
        parser.error("--self-test and --extract-prototype-meta are mutually exclusive")
    if args.self_test:
        from stage_gate_selftest import self_test

        return self_test()
    if args.extract_prototype_meta is not None:
        if args.state is not None or args.target is not None:
            parser.error(
                "--extract-prototype-meta cannot be combined with --state/--target"
            )
        try:
            meta = read_prototype_meta(args.extract_prototype_meta.resolve())
            check = classify_prototype_meta(meta)
            payload = check.as_payload()
            if check.status == "COMPLETE":
                payload["metadata"] = meta
            print(
                json.dumps(
                    payload,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
            )
            return PASS if check.status == "COMPLETE" else BLOCKED
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(
                json.dumps(
                    {
                        "status": "INVALID",
                        "error": str(exc),
                        "nextAction": "read_relevant_html",
                    },
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
            )
            return INVALID_STATE
    if args.state is None or args.target is None:
        parser.error(
            "--state and --target are required unless --self-test or "
            "--extract-prototype-meta is used"
        )
    if not args.state.is_file():
        return emit(
            invalid_result(args.target, f"状态文件不存在: {args.state}"),
            args.state,
            args.json,
        )

    state_path = args.state.resolve()
    try:
        result = validate_gate(state_path, args.target)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        result = invalid_result(args.target, str(exc))
    return emit(result, state_path, args.json)


if __name__ == "__main__":
    raise SystemExit(main())
