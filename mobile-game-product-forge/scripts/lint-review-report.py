#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lint-review-report.py - 评审报告角色版本头一致性校验

把 references/context-loading.md「角色切片、版本一致性与冲突汇总」和
references/templates.md 第 6 节要求的「合并前版本一致性检查」从模型自觉
下沉为脚本判定：

  1. 每个角色段的五个版本追踪字段（reviewRole / snapshotVersion /
     prdVersion / prototypeVersion / reviewedAt）齐全且非空；
  2. 所有角色使用相同 snapshotVersion 和 prdVersion；
  3. required 路径的相关角色使用相同 prototypeVersion。
     waived 路径的 `waived:<批准时间>`、无原型窄任务的
     `not_applicable:narrow_task` 以及「无 / 不适用」按 templates.md 第 6 节
     视为豁免值，不参与实版本比对；但实版本之间仍必须一致。

协调 Agent 在把角色分段写入 04-review-report.md 后、收口 `review.status=passed`
前运行本脚本；退出码非 0 时不得进入 `passed`（见 game-prd-review「评审状态收口」）。

用法（从用户项目调用时用 MGPF 片段定位 skill 仓库根，见 game-prd-review 校验环节）：

    "$PY" "$MGPF/scripts/lint-review-report.py" <04-review-report.md 或工作目录>

退出码：0 = 一致；1 = 缺字段或版本不一致；2 = 找不到文件或无法解析出任何角色段。
"""
from __future__ import annotations

import argparse
import os
import re
import sys

FIELDS = ("reviewRole", "snapshotVersion", "prdVersion", "prototypeVersion", "reviewedAt")
# 字段行：字段名 + 全角或半角冒号 + 值（templates.md 第 6 节格式）
FIELD_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(reviewRole|snapshotVersion|prdVersion|prototypeVersion|reviewedAt)\s*[：:]\s*(.*?)\s*$"
)
# prototypeVersion 的豁免值（waived 路径 / 无原型窄任务），不参与实版本比对
PROTO_EXEMPT_PREFIXES = ("waived:", "waived：")
PROTO_EXEMPT_VALUES = {"not_applicable:narrow_task", "not_applicable：narrow_task", "无", "不适用", "无/不适用"}
DEFAULT_BASENAME = "04-review-report.md"


def parse_role_records(text: str) -> list[dict[str, str]]:
    """按 reviewRole 出现次数切分角色段，收集每段的五个版本头字段。"""
    records: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        m = FIELD_RE.match(line)
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        if key == "reviewRole":
            current = {"reviewRole": value}
            records.append(current)
        elif current is not None and key not in current:
            # 只取本段首次出现，防止后续问题条目里的同名字段串段
            current[key] = value
    return records


def proto_is_exempt(value: str) -> bool:
    v = value.strip()
    return v in PROTO_EXEMPT_VALUES or any(v.startswith(p) for p in PROTO_EXEMPT_PREFIXES)


def lint(text: str) -> tuple[int, list[str]]:
    records = parse_role_records(text)
    if not records:
        return 2, ["无法解析出任何角色段（未找到 reviewRole 字段行；格式见 templates.md 第 6 节）"]

    problems: list[str] = []
    for i, rec in enumerate(records, 1):
        role = rec.get("reviewRole") or f"<第 {i} 段>"
        if not rec.get("reviewRole"):
            problems.append(f"第 {i} 段：reviewRole 为空")
        for key in FIELDS[1:]:
            if key not in rec:
                problems.append(f"角色「{role}」：缺少字段 {key}")
            elif not rec[key].strip():
                problems.append(f"角色「{role}」：字段 {key} 为空")

    def check_uniform(key: str) -> None:
        values = {rec[key].strip() for rec in records if rec.get(key, "").strip()}
        if len(values) > 1:
            detail = "；".join(
                f"{rec.get('reviewRole', '?')}={rec.get(key, '').strip()}"
                for rec in records
                if rec.get(key, "").strip()
            )
            problems.append(f"{key} 不一致（不得直接汇总为 passed，先只重审过期角色）：{detail}")

    check_uniform("snapshotVersion")
    check_uniform("prdVersion")

    proto_real = {
        rec["prototypeVersion"].strip()
        for rec in records
        if rec.get("prototypeVersion", "").strip() and not proto_is_exempt(rec["prototypeVersion"])
    }
    if len(proto_real) > 1:
        detail = "；".join(
            f"{rec.get('reviewRole', '?')}={rec.get('prototypeVersion', '').strip()}"
            for rec in records
            if rec.get("prototypeVersion", "").strip() and not proto_is_exempt(rec["prototypeVersion"])
        )
        problems.append(f"prototypeVersion 不一致（required 路径相关角色必须使用同一原型版本）：{detail}")

    return (1 if problems else 0), problems


def resolve_target(path: str) -> str | None:
    if os.path.isdir(path):
        candidate = os.path.join(path, DEFAULT_BASENAME)
        return candidate if os.path.isfile(candidate) else None
    return path if os.path.isfile(path) else None


SELF_TEST_CASES: list[tuple[str, str, int]] = [
    (
        "consistent",
        """## 产品负责人
reviewRole：产品负责人
snapshotVersion：v1.2
prdVersion：v0.2
prototypeVersion：v1.0
reviewedAt：2026-07-27T10:00:00+08:00

问题编号：P1-001
风险等级：P1

## 测试负责人
reviewRole：测试负责人
snapshotVersion：v1.2
prdVersion：v0.2
prototypeVersion：v1.0
reviewedAt：2026-07-27T10:05:00+08:00
""",
        0,
    ),
    (
        "prd version drift",
        """reviewRole：产品负责人
snapshotVersion：v1.2
prdVersion：v0.2
prototypeVersion：v1.0
reviewedAt：2026-07-27T10:00:00+08:00

reviewRole：服务端负责人
snapshotVersion：v1.2
prdVersion：v0.1
prototypeVersion：v1.0
reviewedAt：2026-07-27T10:05:00+08:00
""",
        1,
    ),
    (
        "missing field",
        """reviewRole：数据负责人
snapshotVersion：v1.2
prdVersion：v0.2
reviewedAt：2026-07-27T10:00:00+08:00
""",
        1,
    ),
    (
        "waived exempt value ok",
        """reviewRole：产品负责人
snapshotVersion：v1.2
prdVersion：v0.2
prototypeVersion：waived:2026-07-26T18:00:00+08:00
reviewedAt：2026-07-27T10:00:00+08:00

reviewRole：服务端负责人
snapshotVersion: v1.2
prdVersion: v0.2
prototypeVersion: waived:2026-07-26T18:00:00+08:00
reviewedAt: 2026-07-27T10:05:00+08:00
""",
        0,
    ),
    (
        "real prototype version drift",
        """reviewRole：交互负责人
snapshotVersion：v1.2
prdVersion：v0.2
prototypeVersion：v1.0
reviewedAt：2026-07-27T10:00:00+08:00

reviewRole：客户端负责人
snapshotVersion：v1.2
prdVersion：v0.2
prototypeVersion：v1.1
reviewedAt：2026-07-27T10:05:00+08:00
""",
        1,
    ),
    ("unparseable", "# 评审报告\n\n没有任何角色版本头。\n", 2),
]


def self_test() -> int:
    failed = 0
    for name, text, expected in SELF_TEST_CASES:
        code, problems = lint(text)
        if code != expected:
            failed += 1
            print(f"SELF-TEST FAIL [{name}]: expected exit {expected}, got {code}")
            for p in problems:
                print(f"  - {p}")
    if failed:
        print(f"self-test: {failed}/{len(SELF_TEST_CASES)} cases failed")
        return 1
    print(f"self-test: {len(SELF_TEST_CASES)} cases OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="评审报告角色版本头一致性校验")
    parser.add_argument("target", nargs="?", help=f"评审报告文件或工作目录（目录时取 {DEFAULT_BASENAME}）")
    parser.add_argument("--self-test", action="store_true", help="运行内置自测")
    args = parser.parse_args()

    if args.self_test:
        return self_test()
    if not args.target:
        parser.error("缺少评审报告文件或工作目录参数（或使用 --self-test）")

    path = resolve_target(args.target)
    if path is None:
        print(f"找不到评审报告文件：{args.target}", file=sys.stderr)
        return 2

    try:
        text = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"无法读取评审报告：{exc}", file=sys.stderr)
        return 2

    code, problems = lint(text)
    records = parse_role_records(text)
    if code == 0:
        print(f"PASS：{len(records)} 个角色段版本头齐全且一致（{os.path.basename(path)}）")
    else:
        head = "版本头不一致或缺失" if code == 1 else "无法解析"
        print(f"FAIL（{head}）：{os.path.basename(path)}")
        for p in problems:
            print(f"  - {p}")
        if code == 1:
            print("处理：向过期角色提供当前输入并只重审受影响部分；版本一致前不得写 review.status=passed。")
    return code


if __name__ == "__main__":
    sys.exit(main())
