# 游戏制作总控：安装与使用

入口是 [SKILL.md](SKILL.md)。保留原有六阶段、HTML/引擎原型、视觉交互与验收方法；增加两个按需子 Skill 和共享参考库。

## 目录与职责

- [目标澄清与设计追问](skills/game-intent-interview/SKILL.md)：关键目标不清或取舍冲突时使用，覆盖全过程，不把每次任务变成问卷。
- [核心玩法与长期体验设计](skills/gameplay-loop-design/SKILL.md)：设计、诊断、变更评审三种模式，主要介入原型前和试玩后。
- [专业方法](references/design-methods.md)、[13模式库](references/mode-library.md)、[来源](references/sources.md)：提供思路、边界与证据，不代表一套必然成功的公式。
- [专项交接](references/planning-handoff.md)、[持续参与与商业化](references/engagement-and-monetization.md)、[测试](references/testing-and-evidence.md)：衔接策划、UI、技术、广告与验证，不新增一个巨大留存总控。
- [决策](templates/decision-record.md)、[方案](templates/loop-design.md)、[实验](templates/experiment-plan.md)：可选模板，优先沿用目标项目已有记录。

## 安装边界

复制或安装整个 `game-production/` 文件夹，保留所有相对路径，不能只复制顶层文件。宿主支持 Skill 时安装根入口；不支持时直接让 Agent 读取根 `SKILL.md`。子模块由根入口显式按路径读取，不依赖递归自动注册，也不要求另起 Agent。

本包不强制依赖外部 `game-design-planner`、特定 MCP 或某一引擎。外部策划能力确实存在时才连接，缺失时按交接协议完成本轮必要设计。不改动目标工程的 `.agent/` 或全局设置，不自动推送代码；仓库写入仍需用户明确授权。

## 使用示例

“用 game-production 接手当前游戏，先读已有工程和决定。只解决这一轮最影响玩家体验的问题，关键取舍带建议来问，明确后推进到可检查的原型。”

“原型已经能玩，但人物传承没有感觉。用诊断模式分析已有证据，不直接新增签到或养成系统。”

“准备增加激励视频。按当前仅广告的商业模式评审，检查是否消除了资源取舍，再给最小接入与验证范围。”

示例不是任何项目的现状或已通过方案。参考库没有硬编码平台准入规则、广告安全次数或留存合格线；实施时查询当前官方资料。

## 检查

在仓库根目录运行（Python 3.9+，仅标准库，无网络请求）：

```bash
python3 game-production/scripts/validate_skill.py
python3 -m unittest discover -s game-production/tests -p 'test_*.py' -v
```

第一项检查入口、元数据、包内相对路径、模式完整性和场景格式；第二项验证校验器能拒绝坏包。它们不执行LLM，也不证明 Agent 在真实项目中一定遵守指令。

[行为回归场景](tests/scenarios.json)提供输入、预期路由、应做与不应做的行为。用实际目标宿主逐项执行时另存模型/版本、输出与人工判定，不把结构校验称作行为测试通过。

## 来源与更新

参考库对外部文章只保留简要归纳、工作化应用及来源，不附书籍全文、用户上传PDF或私人聊天记录。13模式作者表述与本包扩展分开；详见[来源边界](references/sources.md)和[更新记录](CHANGELOG.md)。
