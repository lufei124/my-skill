# ADR-0002：编号主题目录 + 固定 6 层结构

状态：已采纳

## 背景

一次调研会产出大量异构文件（一手清单、视角化 stories、设计选项、红队记录、最终汇总）。若无统一目录约定，不同主题、不同 agent 产出的文件散落各处，无法机械校验完整性，也无法横向复用。同时同一项目可能先后调研多个主题，需要主题间互不覆盖、可按序追溯。

## 决策

所有调研产物落在 `.scratch/research/NN-topic-name/` 下：`NN` 是按已有主题目录递增的两位序号（`find_next_index`），`topic-name` 是 kebab-case 主题名。目录下默认 6 层固定子目录：`00-brief`（总则）/ `01-raw-findings`（一手资料）/ `02-perspectives`（视角化 stories）/ `03-design-options`（设计选项）/ `04-redteam-review`（红队）/ `05-synthesis`（评审汇总）。`scripts/create_research_skeleton.py` 自动创建该骨架并写入 `00-brief/brief.md` 总则。各层语义见 `references/output-structure.md`。

## 备选方案

- 扁平存放，靠文件名前缀区分类型：被否，文件多了不可读，且无法表达层级依赖（synthesis 依赖前面四层）。
- 由用户每次自定义目录结构：被否，破坏机械校验与跨主题复用，Workflow 脚本模板也无法假设路径。
- 不编号、用时间戳命名主题目录：被否，时间戳不可读、不可排序追溯；递增序号在 `find_next_index` 下天然单调。
- 固定更多/更少层级：6 层是「对齐 -> 一手 -> 视角 -> 方案 -> 对抗 -> 汇总」方法论的完整闭环，少则缺对抗或汇总，多则强加未必需要的粒度。领域预设可重命名或增删层级（见 [ADR-0004](0004-pluggable-domain-presets.md)），但通用默认保持 6 层。

## 后果

- `grade_research_init.py` 的 `creates_structured_research_directory` 断言按序号主题目录 + 期望子目录集合校验（期望集合可由 eval 元数据覆盖）。
- `create_research_skeleton.py --self-test` 断言每个 preset 都生成 6 层 + brief.md。
- Workflow 脚本模板（`references/workflow-template.md`）可假设固定路径，各 agent 读写路径确定。
- `find_next_index` 在并发创建主题时理论上有竞态，但调研主题创建频率极低且由人/协调者驱动，不引入锁；若未来需要可在调用方串行化。
