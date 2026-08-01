# ADR-0005: 子 Skill 用 ../../references/ 相对路径，要求整仓符号链接

- 状态：已采纳
- 日期：2026-07-25
- 影响：安装结构（难逆）

## 背景

子 Skill 须共享 `references/` 领域规范与 `scripts/`。若每个子 Skill 内联规范，会随主规范演进漂移；若用绝对路径，换机/换目录即失效。

## 决策

子 Skill 以 `../../references/`、`../../scripts/` 相对路径引用共享规范与脚本。`install.sh` 以整仓符号链接安装（非仅 `SKILL.md`），使相对路径在目标项目可解析。

## 备选方案

- **内联规范到每个子 Skill**：多份副本随演进漂移，校验无法发现。被否。
- **绝对路径**：换目录/换机即失效。被否。
- **仅装 SKILL.md**：子 Skill 相对引用无法解析，fan-out 断链。被否。

## 后果

- 单一权威源在 `references/` 与 `scripts/`，子 Skill 只引用不复制。
- 安装须整仓符号链接（`install.sh` 已如此）；`validate.sh` 校验子 Skill 相对引用解析。可变规则见 `AGENTS.md`「安装边界」与 `scripts/install.sh`。
