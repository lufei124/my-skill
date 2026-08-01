#!/usr/bin/env python3
"""初始化一个可被多个 AI Agent 协作开发的项目骨架。

从 assets/ 读取模板树（单一真相源），按探测到的技术栈渲染占位符并写入目标项目。
默认不覆盖已有文件。技术栈探测：package.json -> node；
pyproject.toml / requirements.txt -> python；否则 generic。
"""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import date
from pathlib import Path
from typing import Dict, Iterator, List, Tuple

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS = SKILL_ROOT / "assets"
SKELETON = ASSETS / "skeleton"
STACKS_DIR = ASSETS / "stacks"

STACKS = ("node", "python", "generic")
PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


def detect_stack(root: Path) -> str:
    """根据标记文件探测技术栈。"""
    if (root / "package.json").exists():
        return "node"
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists():
        return "python"
    return "generic"


def build_context(root: Path, stack: str) -> Dict[str, str]:
    """构造占位符上下文。"""
    ctx: Dict[str, str] = {
        "STACK": stack,
        "PROJECT_NAME": root.name,
        "INIT_DATE": date.today().isoformat(),
    }
    if stack == "node":
        if (root / "pnpm-lock.yaml").exists():
            pm = "pnpm"
        elif (root / "yarn.lock").exists():
            pm = "yarn"
        else:
            pm = "npm"
        ctx["INSTALL_COMMAND"] = {"npm": "npm ci", "pnpm": "pnpm install", "yarn": "yarn install"}[pm]
        ctx["TEST_COMMAND"] = "{0} test".format(pm)
        ctx["BUILD_COMMAND"] = "{0} run build".format(pm)
        ctx["LINT_COMMAND"] = "{0} run lint".format(pm)
    elif stack == "python":
        if (root / "requirements.txt").exists():
            ctx["INSTALL_COMMAND"] = "pip install -r requirements.txt"
        else:
            ctx["INSTALL_COMMAND"] = "pip install -e ."
        ctx["TEST_COMMAND"] = "pytest"
        ctx["BUILD_COMMAND"] = "# 项目特定，待填写"
        ctx["LINT_COMMAND"] = "ruff check ."
    else:
        ctx["INSTALL_COMMAND"] = "# 待填写"
        ctx["TEST_COMMAND"] = "# 待填写"
        ctx["BUILD_COMMAND"] = "# 待填写"
        ctx["LINT_COMMAND"] = "# 待填写"
    return ctx


def iter_templates(stack: str) -> Iterator[Tuple[Path, Path]]:
    """遍历 skeleton 与 stack 覆盖层，yield (源文件, 目标相对路径)。"""
    for base in (SKELETON, STACKS_DIR / stack):
        if not base.exists():
            continue
        for src in sorted(base.rglob("*")):
            if src.is_file():
                yield src, src.relative_to(base)


def render(text: str, ctx: Dict[str, str]) -> str:
    """替换 {{VAR}} 占位符；未知的占位符原样保留（写完后统一告警）。"""
    return PLACEHOLDER.sub(lambda m: ctx.get(m.group(1), m.group(0)), text)


def write_file(path: Path, content: str, force: bool, dry_run: bool) -> str:
    """写入文件，返回动作描述。"""
    verb_written = "将写入" if dry_run else "已写入"
    verb_kept = "将保留" if dry_run else "保留"
    if path.exists() and not force:
        return verb_kept
    if dry_run:
        return verb_written
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return verb_written


def check_git(root: Path, init_git: bool) -> str:
    """检测 Git 仓库状态；按需 git init。返回状态描述。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return "已是仓库"
    except FileNotFoundError:
        return "未检测到 git 命令（跳过 Git 检查）"

    if init_git:
        subprocess.run(["git", "init"], cwd=str(root), capture_output=True)
        return "已执行 git init"
    return "非 Git 仓库（建议 git init，或加 --init-git）"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--force", action="store_true", help="覆盖已有的受管模板文件")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不写入文件")
    parser.add_argument(
        "--stack",
        choices=["auto", "node", "python", "generic"],
        default="auto",
        help="指定技术栈，默认 auto（自动探测）",
    )
    parser.add_argument("--init-git", action="store_true", help="非 Git 仓库时执行 git init")
    args = parser.parse_args()

    root = Path(args.project_root).expanduser().resolve()
    created_root = False
    if not root.exists():
        root.mkdir(parents=True)
        created_root = True
    elif not root.is_dir():
        parser.error("目标路径不是目录：{0}".format(root))

    stack = args.stack if args.stack != "auto" else detect_stack(root)
    ctx = build_context(root, stack)

    if not SKELETON.exists():
        parser.error("未找到 assets/skeleton/，请确认 skill 安装完整：{0}".format(SKELETON))

    git_status = check_git(root, args.init_git)

    if created_root:
        print("已创建目录：{0}".format(root))
    print("技术栈：{0}{1}".format(stack, "（手动指定）" if args.stack != "auto" else "（自动探测）"))
    print("Git：{0}".format(git_status))
    print("已在 {0} 初始化多 Agent 项目骨架：".format(root))

    results: List[Tuple[Path, str]] = []
    written_files: List[Path] = []
    for src, rel in iter_templates(stack):
        content = render(src.read_text(encoding="utf-8"), ctx)
        dest = root / rel
        action = write_file(dest, content, args.force, args.dry_run)
        results.append((rel, action))
        if action in ("已写入", "将写入"):
            written_files.append(dest)

    written_count = sum(1 for _, a in results if a in ("已写入", "将写入"))
    kept_count = sum(1 for _, a in results if a in ("保留", "将保留"))

    for rel, action in results:
        print("- {0:8} {1}".format(action, rel))

    print("共 {0} 项：已写入 {1}，保留 {2}。".format(len(results), written_count, kept_count))
    if args.dry_run:
        print("（dry-run：未实际落盘）")

    # 写完后扫残留占位符，帮助模板作者发现拼写错误
    if not args.dry_run:
        leftover = []
        for dest in written_files:
            try:
                text = dest.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for m in PLACEHOLDER.finditer(text):
                leftover.append("{0}: {{{{{1}}}}}".format(dest.relative_to(root), m.group(1)))
        if leftover:
            print("警告：以下占位符未替换（可能是模板中新增的变量未在 build_context 提供）：")
            for item in leftover:
                print("  - {0}".format(item))

    print(
        "后续：填写 docs/PROJECT_CONTEXT.md 最小节（问题/用户/技术栈），"
        "在 .agent/AGENTS_REGISTRY.md 登记 Agent 身份，然后在 .agent/TASK_BOARD.md 创建首个任务。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
