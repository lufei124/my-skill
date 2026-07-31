#!/usr/bin/env python3
"""评分脚本：检查调研初始化输出是否满足断言（通用版）。

用法：
    python grade_research_init.py <eval-dir>

其中 <eval-dir> 是包含 with_skill/ 或 without_skill/ 的 eval 目录。
脚本会读取 eval 元数据中的断言定义，并输出 grading.json。

元数据来源（按优先级）：
    1. <eval-dir>/eval_metadata.json
    2. <eval-dir>/evals.json 中按 run 目录名或 eval_name 匹配的条目

每个 eval 条目可选字段：
    - perspective_keywords: list[str]  批判性视角关键词（缺失时用通用回退集）
    - expected_subdirs: list[str]      期望的子目录（缺失时用通用 6 层）
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


DEFAULT_SUBDIRS = [
    "00-brief",
    "01-raw-findings",
    "02-perspectives",
    "03-design-options",
    "04-redteam-review",
    "05-synthesis",
]

DEFAULT_PERSPECTIVE_KEYWORDS = [
    "现代",
    "批判",
    "过时",
    "风险",
    "改进",
    "替代",
    "最佳实践",
]


def _find_brief(eval_dir: Path) -> Path | None:
    outputs_dir = eval_dir / "outputs"
    if not outputs_dir.exists():
        return None
    brief_files = list(outputs_dir.rglob("00-brief/brief.md"))
    return brief_files[0] if brief_files else None


def _find_topic_dir(eval_dir: Path) -> Path | None:
    outputs_dir = eval_dir / "outputs"
    if not outputs_dir.exists():
        return None
    research_dirs = list(outputs_dir.rglob(".scratch/research/*"))
    topic_dirs = [d for d in research_dirs if d.is_dir() and re.match(r"^\d{2}-", d.name)]
    return topic_dirs[0] if topic_dirs else None


def check_directory_structure(eval_dir: Path, expected_subdirs: list[str]) -> tuple[bool, str]:
    """检查是否创建了结构化调研目录。"""
    topic_dir = _find_topic_dir(eval_dir)
    if not topic_dir:
        return False, "未找到带序号主题目录（如 01-topic-name）"

    missing = [d for d in expected_subdirs if not (topic_dir / d).is_dir()]
    if missing:
        return False, f"主题目录 {topic_dir.name} 缺少子目录: {', '.join(missing)}"

    return True, f"找到完整目录结构: {topic_dir.name}"


def check_brief_exists(eval_dir: Path) -> tuple[bool, str]:
    """检查是否生成了 brief.md。"""
    brief = _find_brief(eval_dir)
    if not brief:
        return False, "未找到 00-brief/brief.md"
    return True, f"找到 brief.md: {brief}"


def check_workflow_mention(eval_dir: Path) -> tuple[bool, str]:
    """检查输出中是否提到 Workflow / 多 Agent 并行。"""
    brief = _find_brief(eval_dir)
    if not brief:
        return False, "未找到 brief.md"

    content = brief.read_text(encoding="utf-8")
    patterns = [r"workflow", r"多\s*agent", r"并行", r"phase\s*1", r"红队", r"评审委员会"]
    matched = [p for p in patterns if re.search(p, content, re.IGNORECASE)]

    if not matched:
        return False, "brief.md 未提到 Workflow / 多 Agent / 红队 / 评审委员会"

    return True, f"brief.md 提到: {', '.join(matched)}"


def check_critical_perspectives(
    eval_dir: Path, keywords: list[str]
) -> tuple[bool, str]:
    """检查是否提到足够的批判性视角关键词（关键词来自 eval 元数据，缺失时回退通用集）。"""
    brief = _find_brief(eval_dir)
    if not brief:
        return False, "未找到 brief.md"

    content = brief.read_text(encoding="utf-8")
    kws = keywords or DEFAULT_PERSPECTIVE_KEYWORDS
    matched = [kw for kw in kws if kw.lower() in content.lower()]

    if len(matched) < 2:
        return False, f"brief.md 批判性视角关键词不足（仅匹配: {', '.join(matched)}）"

    return True, f"brief.md 包含批判性视角关键词: {', '.join(matched)}"


def check_no_premature_source_dive(eval_dir: Path) -> tuple[bool, str]:
    """检查 brief.md 是否以方法论/范围为主，而非直接深入源码细节。"""
    brief = _find_brief(eval_dir)
    if not brief:
        return False, "未找到 brief.md"

    content = brief.read_text(encoding="utf-8")
    required_sections = ["范围", "目标", "团队", "方法", "产出"]
    matched_sections = [s for s in required_sections if s in content]

    if len(matched_sections) < 3:
        return False, f"brief.md 缺少必要方法论章节（仅含: {', '.join(matched_sections)}）"

    # 通用启发式：行号引用密度（去掉原脚本中 LPC 特有的 ::xxx / .c 第 等模式）
    code_reference_pattern = re.compile(r"第?\s*\d+\s*行|line\s*\d+|:\d+(?::\d+)?")
    code_refs = len(code_reference_pattern.findall(content))
    if code_refs > 10:
        return False, f"brief.md 出现过多源码细节引用（{code_refs} 处），可能过早深入源码"

    return True, "brief.md 以方法论和范围为主，未过早深入源码"


def check_grilling_alignment(eval_dir: Path) -> tuple[bool, str]:
    """检查 brief 是否覆盖 grilling 对齐的核心要素：范围、目标、团队、方法/执行方式、约束。"""
    brief = _find_brief(eval_dir)
    if not brief:
        return False, "未找到 brief.md"

    content = brief.read_text(encoding="utf-8").lower()
    required = {
        "范围": "范围" in content,
        "目标": "目标" in content,
        "团队": "团队" in content or "角色" in content,
        "方法/执行方式": "方法" in content or "执行方式" in content or "workflow" in content,
        "约束": "约束" in content or "不纳入" in content,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        return False, f"brief.md 缺少 grilling 对齐要素: {', '.join(missing)}"
    return True, "brief.md 覆盖 grilling 对齐要素: 范围、目标、团队、方法/执行方式、约束"


# 通用断言检查器。evals.json 中的 assertion.name 映射到这里。
# includes_modern_perspectives / emphasizes_modern_and_commercial_perspectives 保留为
# check_critical_perspectives 的别名，兼容从原 skill 迁移的 eval。
ASSERTION_CHECKS = {
    "starts_with_grilling_or_alignment": check_grilling_alignment,
    "creates_structured_research_directory": check_directory_structure,
    "generates_brief_md": check_brief_exists,
    "proposes_multi_agent_workflow": check_workflow_mention,
    "includes_critical_perspectives": check_critical_perspectives,
    "includes_modern_perspectives": check_critical_perspectives,
    "emphasizes_modern_and_commercial_perspectives": check_critical_perspectives,
    "no_premature_source_dive": check_no_premature_source_dive,
}


def load_metadata(eval_dir: Path) -> dict:
    """加载 eval 元数据：优先 eval_metadata.json，否则从同级 evals.json 按 run 名匹配。"""
    metadata_path = eval_dir.parent / "eval_metadata.json"
    if metadata_path.exists():
        return json.loads(metadata_path.read_text(encoding="utf-8"))

    evals_path = eval_dir.parent / "evals.json"
    if evals_path.exists():
        data = json.loads(evals_path.read_text(encoding="utf-8"))
        evals = data.get("evals", []) if isinstance(data, dict) else data
        run_name = eval_dir.name  # with_skill / without_skill
        for ev in evals:
            ev_name = ev.get("eval_name", "")
            if ev_name and ev_name in str(eval_dir) or run_name in ev_name:
                return ev
        # 退化：取第一条
        if evals:
            return evals[0]

    return {}


def grade_eval(eval_dir: Path) -> dict:
    """对一个 eval 目录下的 with_skill 或 without_skill run 进行评分。"""
    metadata = load_metadata(eval_dir)
    assertions = metadata.get("assertions", [])
    perspective_keywords = metadata.get("perspective_keywords", [])
    expected_subdirs = metadata.get("expected_subdirs", DEFAULT_SUBDIRS)

    results = []
    for assertion in assertions:
        name = assertion["name"]
        description = assertion["description"]
        checker = ASSERTION_CHECKS.get(name)

        if checker is None:
            results.append({
                "text": description,
                "passed": False,
                "evidence": f"未知的断言检查器: {name}",
            })
            continue

        # 按检查器注入对应参数
        if checker is check_directory_structure:
            passed, evidence = checker(eval_dir, expected_subdirs)
        elif checker is check_critical_perspectives:
            passed, evidence = checker(eval_dir, perspective_keywords)
        else:
            passed, evidence = checker(eval_dir)

        results.append({
            "text": description,
            "passed": passed,
            "evidence": evidence,
        })

    total = len(results)
    passed = sum(1 for r in results if r["passed"])

    return {
        "eval_id": metadata.get("eval_id") or metadata.get("id"),
        "eval_name": metadata.get("eval_name"),
        "prompt": metadata.get("prompt"),
        "run_type": eval_dir.name,
        "pass_rate": passed / total if total > 0 else 0,
        "assertions": results,
    }


def main():
    if len(sys.argv) != 2:
        print(f"用法: {sys.argv[0]} <eval-dir>", file=sys.stderr)
        sys.exit(1)

    eval_dir = Path(sys.argv[1])
    if not eval_dir.exists():
        print(f"目录不存在: {eval_dir}", file=sys.stderr)
        sys.exit(1)

    if eval_dir.name in ("with_skill", "without_skill"):
        result = grade_eval(eval_dir)
        output_path = eval_dir / "grading.json"
        output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Grading saved to: {output_path}")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for run_type in ("with_skill", "without_skill"):
            run_dir = eval_dir / run_type
            if run_dir.exists():
                result = grade_eval(run_dir)
                output_path = run_dir / "grading.json"
                output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"Grading saved to: {output_path}")


if __name__ == "__main__":
    main()
