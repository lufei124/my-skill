# Changelog

All notable changes to `multi-agent-project-skill`. The single version source is `package.json`; every other version field must match it and is checked by `scripts/validate.sh`.

## [Unreleased]

## [1.0.0] - 2026-08-01

### Added

- 初始化器 `scripts/init_workspace.py` 改为 **assets 驱动**：`assets/` 为模板唯一真相源，脚本零内嵌字符串；按技术栈探测（`package.json` -> node；`pyproject.toml`/`requirements.txt` -> python；否则 generic）渲染 `{{VAR}}` 占位符写入目标项目。CLI：`project_root`（默认 `.`）、`--dry-run`、`--stack {auto,node,python,generic}`、`--force`、`--init-git`、`--self-test`。
- `assets/skeleton/`：技术栈无关骨架，镜像目标项目路径--AGENTS.md（统一入口）、CLAUDE.md（极简指针）、README.md、docs/ 6 个（PROJECT_CONTEXT / ARCHITECTURE / DEVELOPMENT_RULES / TESTING / DECISIONS / GLOSSARY）、skills/ 5 个九段式（requirement-review / feature-development / bug-fix / test-and-verify / task-handoff）、`.agent/` 簿记（PROJECT_STATE / TASK_BOARD / FILE_LOCKS / TASK_HANDOFF / AGENTS_REGISTRY + decisions/ADR-0000-template + handoffs/HANDOFF-template + task-ids/.gitkeep）。
- `assets/stacks/{node,python,generic}/`：各栈 `.gitignore` 与 `.github/workflows/ci.yml`；三份 `.gitignore` 均不忽略 `.agent/`（簿记必须入库）。
- 协议补齐协作机制：Agent 注册与协调者（`.agent/AGENTS_REGISTRY.md`）、任务 ID 原子分配（`mkdir .agent/task-ids/TASK-NNN`，POSIX 原子）、worktree 操作约定（兄弟目录、命名规约）、`.agent/` 的 Git 策略（提交主分支、追加友好、冲突处理）、陈旧锁 TTL（4 小时检视信号，不自动释放）。
- 交接协议清单新增「已更新文档」「无需更新文档及理由」两节。
- **升级基础设施（镜像 mobile-game-product-forge 成熟度）**：
  - `package.json` 唯一版本源 + `npm run validate`。
  - `.claude-plugin/plugin.json`（根注册 `skills:["./"]`）+ `.claude-plugin/marketplace.json`（同仓自托单插件，`source:"./"`，不写 version）。
  - `agents/openai.yaml` 跨平台 adapter（interface + policy.allow_implicit_invocation）。
  - `AGENTS.md` 维护者手册（15 节，单编排器适配：职责/优先级/边界/修改流程/原则/Skill 开发/模板维护/同步清单/文档同步机制/检查表/一致性/验证矩阵/版本发布/多 Agent 协作/禁止/完成定义）。
  - `.agents/adr/` 追加式 ADR（README + 0001-0006：assets 单一真相源 / AGENTS.md 统一入口 / 任务 ID 原子分配 / 陈旧锁 TTL 不自动释放 / 插件形态发布 / package.json 唯一版本源）。
  - `scripts/validate.sh` 校验器（结构/版本一致/插件清单/marketplace/YAML 结构/引用解析/脚本存在/install-profiles/文档漂移/升级 SOP/ADR 索引/assets 完整性/栈 .gitignore 不忽略 .agent/占位符集合一致/Python self-test/shell 语法）。
  - `scripts/install.sh` + `scripts/install.ps1` 跨 Agent 安装器（codex/claude/cursor/all，整包软链，依赖体检）。
  - `scripts/release.sh` 发版入口（同步三处版本 + 断言 CHANGELOG + 全量校验）。
  - `scripts/githooks/pre-push` 推送门禁。
  - `scripts/doc-impact-check.sh` 文档影响预检（非阻断）。
  - `install-profiles/core.yaml` source_files 校验清单。
  - `operation-guide.md` 用户日常操作文档 + `install-guide.md` 安装升级指南。
  - `init_workspace.py --self-test` 回归（三栈 dry-run + 占位符 + 幂等 + 不覆盖）。

### Changed

- frontmatter `name` 由 `multi-agent-project-coordination` 改为 `multi-agent-project-skill`（与目录名一致）。
- SKILL.md「必需的项目状态」->「项目骨架」完整树；开工流程读取清单修正 `PROJECT_CONTEXT.md` -> `docs/PROJECT_CONTEXT.md`，新增 `docs/DEVELOPMENT_RULES.md`。
- README.md 加「安装」「升级」小节，内容表登记新增文件。

### Removed

- 旧的 `assets/project-state/` 目录（与 skeleton 双份维护，已被 `assets/skeleton/.agent/` 取代）。
