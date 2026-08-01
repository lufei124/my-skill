#!/usr/bin/env python3
"""创建调研目录骨架（通用版，支持领域预设）。

用法：
    python create_research_skeleton.py <topic-name> [--preset game-mud|software-system|none] [--root <research-root>]

示例：
    python create_research_skeleton.py auth-module --preset software-system
    python create_research_skeleton.py combat-system --preset game-mud
    python create_research_skeleton.py data-pipeline
"""

import argparse
import re
import sys
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(".scratch/research")

DEFAULT_SUBDIRS = [
    "00-brief",
    "01-raw-findings",
    "02-perspectives",
    "03-design-options",
    "04-redteam-review",
    "05-synthesis",
]

# 领域预设：子目录集（默认同 DEFAULT_SUBDIRS）+ brief 增量片段文件名。
# 片段文件位于本脚本同目录的 ../references/domain-presets/ 下。
PRESETS = {
    "none": {
        "subdirs": DEFAULT_SUBDIRS,
        "brief_include": None,
    },
    "game-mud": {
        "subdirs": DEFAULT_SUBDIRS,
        "brief_include": "game-mud.brief.md",
    },
    "software-system": {
        "subdirs": DEFAULT_SUBDIRS,
        "brief_include": "software-system.brief.md",
    },
}

BRIEF_TEMPLATE = """# {topic_title} 调研总则

> 本次调研属于 `.scratch/research/` 下研究主题。基于当前仓库一手资料，对 {topic_title} 进行深度调研与设计批判，并引入批判性外部视角。

## 1. 调研目标

1. **忠实还原实现细节**：基于当前仓库一手源码/文档/数据，细致梳理 {topic_title} 的实现方式、数据结构、调用链与状态流转。
2. **提取设计灵感与风险警示**：从批判性外部视角出发，输出可参考的方向、应避免的反模式以及需警惕的风险。
3. **不输出可落地契约**：本次调研止步于设计输入层，具体的抽象与接口设计留待后续任务单独决策。

{preset_increment}

## 2. 范围边界

### 2.1 纳入范围

- 待 Grilling 阶段确认后填写。

### 2.2 不纳入范围

- 不做行为等价验证。
- 不把现有实现当作唯一正确形态反向脑补。
- 不依赖旧文档结论。
- 不输出可直接落地的代码或接口契约。

## 3. 调研团队与职责

见 research-workflow skill 的 `references/team-roles.md`；选用领域预设时见 `references/domain-presets/<preset>.md`。

## 4. 调研方法

### 4.1 多 Agent 并行 Workflow

- **Phase 1：并行初稿**：各角色同步阅读资料并产出指定章节初稿。
- **Phase 2：红队对抗**：横向对比验证员交叉检查，评审委员会组织质询，各角色回应并修订。
- **Phase 3：评审委员会汇总**：统一文风、消除矛盾、标注未决问题，生成最终报告。

### 4.2 资料来源优先级

1. 当前仓库根目录下源码（一手）。
2. 必要时查阅文档/配置/数据，作为补充。
3. 旧文档/外部资料仅作二手参考，并显式标注。

## 5. 输出目录结构

```
.scratch/research/{topic_dir}/
├── 00-brief/               # 本总则
├── 01-raw-findings/        # 一手资料：源码清单、调用链、数据结构、机制抽象
├── 02-perspectives/        # 视角化分析：actor / system / operator stories
├── 03-design-options/      # 设计可选方案、改进方向、风险警示
├── 04-redteam-review/      # 红队对抗记录
└── 05-synthesis/           # 评审委员会最终汇总
```

## 6. 关键约束

- **基于一手资料**：所有结论必须能从当前仓库源码/资料中找到证据。
- **全局与细节兼顾**：既要有宏观脉络，也要有代表性实例细节。
- **批判性外部视角**：对过时、不符合当代实践或不可持续的设计显式标注。
- **stories 完整**：覆盖所有可触达路径与视角。
"""


def to_title(topic: str) -> str:
    """将 kebab-case 主题名转为可读标题。"""
    return " ".join(word.capitalize() for word in topic.replace("_", "-").split("-"))


def find_next_index(root: Path) -> int:
    """根据已有主题目录确定下一个序号。"""
    if not root.exists():
        return 1
    indices = []
    for item in root.iterdir():
        if item.is_dir():
            match = re.match(r"^(\d+)-", item.name)
            if match:
                indices.append(int(match.group(1)))
    return max(indices, default=0) + 1


def load_brief_increment(preset_name: str) -> str:
    """读取领域预设的 brief 增量片段；无则返回空串。"""
    include = PRESETS[preset_name]["brief_include"]
    if not include:
        return ""
    preset_dir = Path(__file__).resolve().parent.parent / "references" / "domain-presets"
    fragment_path = preset_dir / include
    if not fragment_path.exists():
        return f"<!-- 警告：预设增量片段缺失：{fragment_path} -->\n"
    return fragment_path.read_text(encoding="utf-8").strip()


def create_skeleton(topic: str, root: Path, preset: str) -> Path:
    """创建调研目录骨架并返回目录路径。"""
    subdirs = PRESETS[preset]["subdirs"]
    next_index = find_next_index(root)
    topic_dir = root / f"{next_index:02d}-{topic}"
    topic_dir.mkdir(parents=True, exist_ok=False)

    for subdir in subdirs:
        (topic_dir / subdir).mkdir(parents=True, exist_ok=False)

    increment = load_brief_increment(preset)
    brief_path = topic_dir / "00-brief" / "brief.md"
    brief_content = BRIEF_TEMPLATE.format(
        topic_title=to_title(topic),
        topic_dir=topic_dir.name,
        preset_increment=increment,
    )
    brief_path.write_text(brief_content, encoding="utf-8")

    return topic_dir


def self_test() -> int:
    """回归自检：在临时目录为每个 preset 生成骨架，断言 6 层 + brief、preset
    增量注入、标题派生、序号递增、无残留占位符。成功返回 0，失败返回 1。"""
    failures = []

    def check(cond, msg):
        if cond:
            print(f"[OK] {msg}")
        else:
            print(f"[FAIL] {msg}")
            failures.append(msg)

    # 各预设 brief 增量里独有的内容短语（none 不得出现任何一个）。
    preset_markers = {
        "game-mud": "现代玩法设计",
        "software-system": "现代工程实践对照",
    }
    unformatted = ["{topic_title}", "{topic_dir}", "{preset_increment}"]
    key_sections = ["调研目标", "范围边界", "调研团队", "调研方法", "输出目录结构", "关键约束"]

    with tempfile.TemporaryDirectory(prefix="rw-skeleton-selftest-") as tmp:
        root = Path(tmp) / "research"

        # 1. 每个 preset：6 层 + brief + 无残留占位符 + preset 注入 + 章节齐全。
        for preset in PRESETS:
            topic = f"topic-{preset}"
            topic_dir = create_skeleton(topic, root, preset)
            for sd in PRESETS[preset]["subdirs"]:
                check((topic_dir / sd).is_dir(), f"{preset}: 子目录 {sd} 生成")
            brief = topic_dir / "00-brief" / "brief.md"
            check(brief.is_file(), f"{preset}: brief.md 生成")
            content = brief.read_text(encoding="utf-8") if brief.is_file() else ""
            check(not any(f in content for f in unformatted), f"{preset}: brief 无残留占位符")
            check("警告：预设增量片段缺失" not in content, f"{preset}: 无预设片段缺失警告")
            check(to_title(topic) in content, f"{preset}: 标题由 topic 派生（{to_title(topic)}）")
            if preset == "none":
                for m in preset_markers.values():
                    check(m not in content, f"none: 不注入预设增量（无 {m}）")
            else:
                check(preset_markers[preset] in content, f"{preset}: 注入了 brief 增量（{preset_markers[preset]}）")
            for sec in key_sections:
                check(sec in content, f"{preset}: brief 含章节 {sec}")

        # 2. 序号递增：首个 01-、第二个 02-、第三个 03-（按 PRESETS 插入序）。
        dirs = sorted(d.name for d in root.iterdir() if d.is_dir())
        check(len(dirs) == len(PRESETS), f"生成主题目录数 = preset 数（{len(dirs)}）")
        for i, name in enumerate(dirs, start=1):
            check(name.startswith(f"{i:02d}-"), f"序号递增：第 {i} 个为 {i:02d}-（实际 {name}）")

        # 3. find_next_index 反映已有目录数。
        check(find_next_index(root) == len(PRESETS) + 1, "find_next_index 反映已有目录数")

        # 4. --root 覆盖已由自定义 root 验证；同 topic 名再创建得到下一序号（不覆盖）。
        again = create_skeleton("topic-none", root, "none")
        check(again.name.startswith(f"{len(PRESETS)+1:02d}-"), "同 topic 名再创建取下一序号（不覆盖既有目录）")

    if failures:
        print(f"\nself-test: {len(failures)} 项失败")
        return 1
    print("\nself-test: 全部通过")
    return 0


def main():
    parser = argparse.ArgumentParser(description="创建调研目录骨架（通用版）")
    parser.add_argument(
        "topic",
        nargs="?",
        default=None,
        help="主题名，例如 auth-module / combat-system（--self-test 时可省略）",
    )
    parser.add_argument(
        "--preset",
        default="none",
        choices=list(PRESETS.keys()),
        help="领域预设：game-mud / software-system / none（默认，纯通用）",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help=f"研究根目录，默认 {DEFAULT_ROOT}",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="运行回归自检（在临时目录为每个 preset 生成骨架并断言），不创建真实目录",
    )
    args = parser.parse_args()

    if args.self_test:
        sys.exit(self_test())

    if args.topic is None:
        parser.error("topic 是必需的（除非用 --self-test）")

    topic = args.topic.strip().lower().replace(" ", "-")
    try:
        topic_dir = create_skeleton(topic, args.root, args.preset)
    except FileExistsError:
        print(f"错误：目录已存在，请检查 {args.root}", file=sys.stderr)
        sys.exit(1)

    print(f"Created: {topic_dir}")
    print(f"Brief:   {topic_dir / '00-brief' / 'brief.md'}")
    print(f"Preset:  {args.preset}")


if __name__ == "__main__":
    main()
