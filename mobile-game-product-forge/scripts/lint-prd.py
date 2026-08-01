#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
lint-prd.py - 移动游戏 PRD 格式校验

校验 PRD markdown 的五类可机器校验格式（依据 references/prd-spec.md）：
  1. 配置表结构：表名 csv 命名、字段分组 N 个字段计数、字段四项、英文名大驼峰、禁横向字段说明表
  2. 埋点事件明细表：固定 12 列表头、snake_case 标识符、数据来源取值、版本字段
  3. 编号规则：文本或表格中的 R-NNN / AC-NNN 唯一性、关联规则存在性、规则-验收映射
  4. 结构：统一执行结构的核心章；L2/L3 需总体流程；历史 20 章结构兼容
  5. 数据来源：页面和交互章节须有数据来源映射表或行内标注
  6. 占位符：逐条列出「待补充截图」，结论降为有条件通过（交付前由发布门硬拦）

用法（脚本位于 skill 仓库 scripts/；从用户项目调用时用 skill 仓库根路径定位，见 game-prd-review 校验环节）：

  bash / Git Bash / WSL（macOS/Linux，Windows 上 Claude Code/Codex 走 Git Bash）：
    # MGPF 四级定位片段（环境变量 → CLAUDE_PLUGIN_ROOT → skills 目录 → 插件缓存）
    # 以 skills/game-prd-review/SKILL.md「校验」节为唯一权威，此处不再复制
    "$PY" "$MGPF/scripts/lint-prd.py" <prd.md> [-o 06-lint-report.md]

  Windows 原生 PowerShell（Cursor / 直接 pwsh）：
    # $MGPF 定位同上（pwsh 形式见 game-prd-review SKILL.md）
    python "$MGPF\scripts\lint-prd.py" <prd.md> [-o 06-lint-report.md]

  也可传工作目录自动取最新的 *-prd-*.md：
    "$PY" "$MGPF/scripts/lint-prd.py" <工作目录>

退出码：0 = 无 error（可有 warning）；1 = 存在 error；2 = 找不到 PRD 文件。
"""
import sys
import os
import re
import argparse

# 事件明细表固定 12 列（顺序不可改，见 prd-spec.md「埋点和指标」）
EVENT_COLS = [
    "事件分类", "事件名称", "事件标识符", "数据来源", "埋点触发时机",
    "属性名称", "属性标识符", "属性含义", "上线版本", "下线版本", "类型", "值含义",
]
# 公共属性表固定 6 列
COMMON_PROP_COLS = ["属性标识符", "属性名称", "属性含义", "上线版本", "下线版本", "负责人"]
# 数据来源合法原子取值（可多端用 / 组合）
DATA_SRC_ATOMS = {"客户端", "服务端", "lua"}
VALID_DATA_SRC = {"待确认"} | DATA_SRC_ATOMS

SNAKE = re.compile(r"^[a-z][a-z0-9_]*$")
PASCAL = re.compile(r"^[A-Z][A-Za-z0-9]*$")
VERSION = re.compile(r"^v?\d+(\.\d+){1,2}$")
CSV_NAME = re.compile(r"^[a-z][a-z0-9_]*\.csv$")
FIELD_ITEMS = ("类型", "作用", "为空时填写", "配置说明")

# 「为空时填写」合法取值：可空字段填 0；必填字段含下列关键词。其余取值提示修正
EMPTY_FILL_REQUIRED_KW = ("不可为空", "必填", "非空")

# 配置表结构正则（括号兼容全角／半角）
TABLE_HDR = re.compile(r"^(.+?)[（(]([A-Za-z0-9_]+\.csv)[）)]\s*$")
MODULE_HDR = re.compile(r"^(.+?)[（(](\d+)\s*个字段[）)]\s*$")
FIELD_HDR = re.compile(r"^(.+?)[（(]([A-Za-z][A-Za-z0-9_]*)[）)]\s*$")
RULE_DEF = re.compile(r"^\s*(?:\|\s*)?R-(\d+)(?:\s+|\s*\|)")
RULE_REF = re.compile(r"\bR-(\d+)\b")
CASE_DEF = re.compile(r"(?:Case\s*ID\s*[:：]\s*AC-(\d+)|^\s*\|\s*AC-(\d+)\s*\|)")

CAT_LABEL = {"config": "配置表", "analytics": "埋点", "numbering": "编号", "structure": "结构",
             "data_source": "数据来源", "placeholder": "占位符"}
CAT_ORDER = ("config", "analytics", "numbering", "structure", "data_source", "placeholder")

# 截图占位符：未提供截图处写「待补充截图：<页面>-<状态>」（见 CHANGELOG 3.1.x 原型截图改由用户提供）。
# 缺图不阻塞研发理解，因此按提示处理（有条件通过）；但交付前必须由产品负责人显式确认，
# 硬拦在发布门（见 skills/game-prd-publish/SKILL.md 前置条件）。
PLACEHOLDER_SHOT = re.compile(r"待补充截图\s*[：:]?\s*([^\n]*)")


class Issue:
    def __init__(self, category, severity, where, msg):
        self.category = category  # config / analytics / numbering
        self.severity = severity  # error / warning
        self.where = where
        self.msg = msg


ISSUES = []


def err(category, where, msg):
    ISSUES.append(Issue(category, "error", where, msg))


def warn(category, where, msg):
    ISSUES.append(Issue(category, "warning", where, msg))


# ---------- 定位 PRD ----------
def resolve_prd(path):
    if os.path.isdir(path):
        cands = [fn for fn in os.listdir(path)
                 if fn.endswith(".md") and "prd" in fn.lower()]
        cands.sort()
        if not cands:
            return None
        return os.path.join(path, cands[-1])
    return path if os.path.isfile(path) else None


# ---------- 配置表 ----------
def lint_config_tables(lines, label):
    i, n = 0, len(lines)
    in_fence = False
    cur_table = None
    cur_module = None  # [name, expected, actual, lineno]
    while i < n:
        line = lines[i]
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            i += 1
            continue
        # fence 外的标题关闭当前配置表上下文
        if not in_fence and line.startswith("#"):
            cur_module = _close_module(label, cur_table, cur_module)
            cur_table = None
            i += 1
            continue
        mt = TABLE_HDR.match(line)
        if mt:
            cur_module = _close_module(label, cur_table, cur_module)
            cur_table = mt.group(2)
            if not CSV_NAME.match(cur_table):
                err("config", f"{label}:{i+1}",
                    f"配置表文件名「{cur_table}」不符合全小写下划线规范（如 ad_configuration.csv）")
            i += 1
            continue
        mm = MODULE_HDR.match(line)
        if mm:
            cur_module = _close_module(label, cur_table, cur_module)
            cur_module = [mm.group(1).strip(), int(mm.group(2)), 0, i + 1]
            i += 1
            continue
        if cur_table is not None:
            mf = FIELD_HDR.match(line)
            if mf:
                items = _scan_field_items(lines, i + 1)
                if items and any(k in items for k in FIELD_ITEMS):
                    if cur_module is None:
                        err("config", f"{label}:{i+1}",
                            f"字段「{mf.group(2)}」不属于任何模块声明（缺少「<模块名>（N个字段）」标题）")
                    else:
                        cur_module[2] += 1
                    eng = mf.group(2)
                    if not PASCAL.match(eng):
                        err("config", f"{label}:{i+1}",
                            f"字段英文名「{eng}」不符合大驼峰 PascalCase（如 DailyLimit）")
                    missing = [k for k in FIELD_ITEMS if k not in items]
                    if missing:
                        err("config", f"{label}:{i+1}",
                            f"字段「{eng}」缺少说明项：{', '.join(missing)}")
                    ev = items.get("为空时填写")
                    if ev is not None and ev != "0" and not any(k in ev for k in EMPTY_FILL_REQUIRED_KW):
                        warn("config", f"{label}:{i+1}",
                             f"字段「{eng}」的「为空时填写」为「{ev}」：可空字段填 0，必填字段写「不可为空」；不得留空或写其他兜底值（见 prd-spec.md「配置」）")
                    i = items["_end"]
                    continue
            # 横向字段表检测
            if stripped.startswith("|"):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                if ({"字段", "类型"} <= set(cells)) or ({"字段名", "类型"} <= set(cells)):
                    err("config", f"{label}:{i+1}",
                        "配置表不得使用横向字段表格，须用纵向字段说明结构（见 prd-spec.md「配置」）")
        i += 1
    _close_module(label, cur_table, cur_module)


def _scan_field_items(lines, start):
    """从 start 向下扫描字段四项，遇到下一个结构行停止。返回 {项: 值, _end: 行索引}。"""
    found = {}
    j, n = start, len(lines)
    while j < n:
        ln = lines[j]
        if TABLE_HDR.match(ln) or MODULE_HDR.match(ln) or FIELD_HDR.match(ln):
            break
        m = re.match(r"^\s*-\s*(类型|作用|为空时填写|配置说明)\s*[:：]\s*(.*)$", ln)
        if m:
            found[m.group(1)] = m.group(2).strip()
            j += 1
            continue
        if ln.strip().startswith("-"):  # 复杂字段补充项（使用范围/校验规则等）
            j += 1
            continue
        if ln.strip() == "":
            if found:
                break
            j += 1
            continue
        break
    found["_end"] = j
    return found


def _close_module(label, cur_table, cur_module):
    if cur_table is not None and cur_module is not None:
        name, expected, actual, lineno = cur_module
        if actual != expected:
            err("config", f"{label}:{lineno}",
                f"模块「{name}」声明 {expected} 个字段，实际列出 {actual} 个")
    return None


# ---------- 埋点 ----------
def lint_analytics(lines, label):
    tables = _extract_markdown_tables(lines)
    found_event_table = False
    for t in tables:
        header = t["header"]
        if "事件标识符" in header and "事件分类" in header:
            found_event_table = True
            _lint_event_table(t, label)
        elif "属性标识符" in header and "负责人" in header:
            _lint_common_prop_table(t, label)
    if not found_event_table and _has_section(lines, "埋点"):
        err("analytics", label,
            "埋点章节存在但未找到 12 列事件明细表（表头须含「事件分类｜事件名称｜事件标识符｜…」12 列）")


def _extract_markdown_tables(lines):
    tables = []
    i, n = 0, len(lines)
    while i < n:
        if lines[i].lstrip().startswith("|"):
            start = i
            block = []
            while i < n and lines[i].lstrip().startswith("|"):
                block.append(lines[i])
                i += 1
            if len(block) >= 2 and _is_separator(block[1]):
                header = [c.strip() for c in block[0].strip().strip("|").split("|")]
                rows = [[c.strip() for c in r.strip().strip("|").split("|")]
                        for r in block[2:]]
                tables.append({"header": header, "rows": rows, "lineno": start + 1})
        else:
            i += 1
    return tables


def _is_separator(line):
    parts = [p.strip() for p in line.strip().strip("|").split("|")]
    return len(parts) >= 1 and all(re.match(r"^:?-+:?$", p) for p in parts)


def _lint_event_table(t, label):
    header, lineno = t["header"], t["lineno"]
    if len(header) != 12:
        err("analytics", f"{label}:{lineno}",
            f"事件明细表须为固定 12 列，当前 {len(header)} 列")
        return
    for a, b in zip(header, EVENT_COLS):
        if a != b:
            err("analytics", f"{label}:{lineno}",
                f"事件明细表列名/顺序错误：应为「{b}」，实际「{a}」")
    for ri, row in enumerate(t["rows"]):
        rl = lineno + 2 + ri
        if all(c == "" for c in row):
            continue
        if len(row) != 12:
            err("analytics", f"{label}:{rl}",
                f"第 {ri+1} 行数据须为 12 列，当前 {len(row)} 列")
            continue
        _, _, eid, src, _, _, pid, _, online, offline, _, _ = row
        if eid and not SNAKE.match(eid):
            warn("analytics", f"{label}:{rl}",
                 f"事件标识符「{eid}」非小写 snake_case；若为历史保留请确认")
        if pid and not SNAKE.match(pid):
            warn("analytics", f"{label}:{rl}",
                 f"属性标识符「{pid}」非小写 snake_case；若为历史保留请确认")
        if src and not _valid_data_src(src):
            err("analytics", f"{label}:{rl}",
                f"数据来源「{src}」非法；须为 客户端/服务端/lua 或其 / 组合，或「待确认」")
        if online and online != "待确认" and not VERSION.match(online):
            err("analytics", f"{label}:{rl}",
                f"上线版本「{online}」格式异常；未知须写「待确认」，否则如 v1.0.5")
        if offline:
            if offline == "-":
                warn("analytics", f"{label}:{rl}",
                     "下线版本在事件明细表中应留空（有效事件），而非「-」")
            elif not VERSION.match(offline):
                err("analytics", f"{label}:{rl}",
                    f"下线版本「{offline}」格式异常；有效事件应留空")


def _valid_data_src(src):
    if src in VALID_DATA_SRC:
        return True
    parts = [p.strip() for p in src.split("/")]
    return bool(parts) and all(p in DATA_SRC_ATOMS for p in parts)


def _lint_common_prop_table(t, label):
    header, lineno = t["header"], t["lineno"]
    if len(header) != 6:
        err("analytics", f"{label}:{lineno}",
            f"公共属性表须为固定 6 列，当前 {len(header)} 列")
        return
    for a, b in zip(header, COMMON_PROP_COLS):
        if a != b:
            err("analytics", f"{label}:{lineno}",
                f"公共属性表列名/顺序错误：应为「{b}」，实际「{a}」")


def _has_section(lines, keyword):
    in_fence = False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and ln.startswith("#") and keyword in ln:
            return True
    return False


# ---------- 编号 ----------
def lint_numbering(lines, label):
    rule_defs = {}
    case_defs = {}
    cases = []  # [ac_num, lineno, set(referenced rule nums)]
    cur_case = None
    for i, ln in enumerate(lines):
        m = RULE_DEF.match(ln)
        if m:
            rule_defs.setdefault(m.group(1), []).append(i + 1)
        m2 = CASE_DEF.search(ln)
        if m2:
            if cur_case:
                cases.append(cur_case)
            case_num = m2.group(1) or m2.group(2)
            cur_case = [case_num, i + 1, set()]
            case_defs.setdefault(case_num, []).append(i + 1)
        if cur_case:
            for r in RULE_REF.findall(ln):
                cur_case[2].add(r)
    if cur_case:
        cases.append(cur_case)

    for num, lns in rule_defs.items():
        if len(lns) > 1:
            err("numbering", f"{label}:{lns[1]}",
                f"规则编号 R-{num} 重复定义（首次在第 {lns[0]} 行）")
    for num, lns in case_defs.items():
        if len(lns) > 1:
            err("numbering", f"{label}:{lns[1]}",
                f"验收编号 AC-{num} 重复定义（首次在第 {lns[0]} 行）")
    for ac_num, lineno, refs in cases:
        for r in refs:
            if r not in rule_defs:
                err("numbering", f"{label}:{lineno}",
                    f"验收 AC-{ac_num} 关联规则 R-{r} 不存在")
    referenced = set()
    for _, _, refs in cases:
        referenced |= refs
    for num in rule_defs:
        if num not in referenced:
            warn("numbering", f"{label}:{rule_defs[num][0]}",
                 f"规则 R-{num} 未被任何验收 Case 引用（疑似规则与验收映射缺口）")


# ---------- 结构 ----------
# 新 PRD 统一执行结构；历史 20 章按语义标题兼容。
CORE_CHAPTERS = [
    (("功能说明", "需求背景", "需求目标"), "功能说明"),
    (("功能规则",), "功能规则"),
    (("异常和边界",), "异常和边界"),
    (("验收标准", "验收"), "验收标准"),
]
FLOW_CHAPTERS = ("总体流程", "用户流程")


def _headings_outside_fence(lines):
    """返回 fence 外的标题行列表。"""
    headings = []
    in_fence = False
    for ln in lines:
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and ln.startswith("#"):
            headings.append(ln)
    return headings


def lint_structure(lines, label):
    level = None
    for ln in lines:
        m = re.search(r"复杂度(?:分级)?[：:]\s*(L[123]|待确认)", ln)
        if m:
            level = m.group(1)
            break
    if level is None:
        warn("structure", label,
             "未声明复杂度（L1/L2/L3），无法按分级断言必含章；在文档信息区声明「复杂度：L2」（兼容「复杂度分级：L2」）")
    headings = _headings_outside_fence(lines)
    for keywords, name in CORE_CHAPTERS:
        if not any(any(kw in h for kw in keywords) for h in headings):
            err("structure", label,
                f"缺少核心执行章「{name}」标题（见 prd-spec.md「主结构与复杂度」）")
    if level in {"L2", "L3"} and not any(any(kw in h for kw in FLOW_CHAPTERS) for h in headings):
        err("structure", label,
            "L2/L3 缺少「总体流程」标题；历史结构可使用「用户流程」")

    new_style = any("功能说明" in h for h in headings)
    if new_style:
        for h in headings:
            title = re.sub(r"^#+\s*", "", h).strip()
            if "运营后台" in title:
                err("structure", label,
                    "新结构不得包含「运营后台」章节；运营控制应写入配置表合同")
            if re.search(r"^(?:(客户端|服务端|数据库|埋点)(模块|逻辑|设计)?|配置模块)$", title):
                warn("structure", label,
                     f"标题「{title}」疑似按技术层拆功能模块；应按统一流程/R-### 组织，必要时按业务能力分组")
        if not any(ln.strip().startswith("生成记录：") for ln in lines):
            err("structure", label,
                "新结构 PRD 缺少文末紧凑生成记录（格式见主 SKILL.md「文档来源信息」）")
        mermaid_count = sum(1 for ln in lines if ln.strip().lower() == "```mermaid")
        if level == "L2" and mermaid_count > 3:
            warn("structure", label,
                 f"L2 PRD 包含 {mermaid_count} 张 Mermaid 图；建议确认每张图是否解决独立问题，普通 L2 通常不超过 2–3 张")


# ---------- 数据来源 ----------
def lint_data_source(lines, label):
    # 页面和交互章节须标注数据来源（见 prd-spec.md「数据来源」）。
    if not _has_section(lines, "页面和交互"):
        return
    if _has_section(lines, "数据来源映射"):
        return
    if any("数据来源" in ln for ln in lines):
        return
    warn("data_source", label,
         "页面和交互章节存在但未见「数据来源映射」表或行内数据来源标注（见 prd-spec.md「数据来源」）")


# ---------- 占位符 ----------
def lint_placeholders(lines, label):
    """逐条列出终稿里的截图占位符：结论按有条件通过，交付前由发布门硬拦。"""
    in_fence = False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = PLACEHOLDER_SHOT.search(ln)
        if m:
            target = m.group(1).strip().strip("」》)）") or "未标注页面-状态"
            warn("placeholder", f"{label}:{i+1}",
                 f"待补充截图「{target}」：缺图不阻塞研发理解，本次按有条件通过；"
                 "交付前必须补图或由产品负责人显式确认按现状发布（见 game-prd-publish 前置条件）")


# ---------- 报告 ----------
def render_report(label, issues):
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    out = ["# PRD 格式校验报告", "", f"校验对象：{label}", ""]
    if not issues:
        out.append("校验结论：通过（未发现格式问题）")
        return "\n".join(out) + "\n"
    out.append("## 格式问题")
    out.append("")
    by_cat = {}
    for iss in issues:
        by_cat.setdefault(iss.category, []).append(iss)
    for cat in CAT_ORDER:
        items = by_cat.get(cat, [])
        if not items:
            continue
        out.append(f"### {CAT_LABEL[cat]}（{len(items)}）")
        out.append("")
        for iss in items:
            sev = "错误" if iss.severity == "error" else "提示"
            out.append(f"- [{sev}] {iss.where}: {iss.msg}")
        out.append("")
    placeholders = [i for i in issues if i.category == "placeholder"]
    if errors:
        conclusion = "不通过"
    elif placeholders:
        conclusion = f"有条件通过（存在 {len(placeholders)} 处待补充截图，交付前须确认）"
    else:
        conclusion = "有条件通过（仅提示，无错误）"
    out.append(f"校验结论：{conclusion}")
    out.append("")
    out.append(f"统计：错误 {len(errors)}，提示 {len(warnings)}")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description="移动游戏 PRD 格式校验")
    ap.add_argument("path", help="PRD markdown 文件或工作目录")
    ap.add_argument("-o", "--output", help="写入报告到文件（默认输出到 stdout）")
    args = ap.parse_args()
    prd = resolve_prd(args.path)
    if not prd or not os.path.isfile(prd):
        sys.stderr.write(f"找不到 PRD 文件：{args.path}\n")
        sys.exit(2)
    with open(prd, encoding="utf-8") as f:
        lines = f.read().split("\n")
    label = os.path.basename(prd)
    lint_config_tables(lines, label)
    lint_analytics(lines, label)
    lint_numbering(lines, label)
    lint_structure(lines, label)
    lint_data_source(lines, label)
    lint_placeholders(lines, label)
    report = render_report(label, ISSUES)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        errors = sum(1 for i in ISSUES if i.severity == "error")
        sys.stderr.write(f"报告已写入 {args.output}（错误 {errors}）\n")
    else:
        sys.stdout.write(report)
    sys.exit(1 if any(i.severity == "error" for i in ISSUES) else 0)


if __name__ == "__main__":
    main()
