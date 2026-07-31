# Workflow 脚本模板（通用）

本文件提供一个可直接改编的 JavaScript Workflow 脚本结构。使用时根据具体研究对象与领域预设替换占位符：

- `<RESEARCH_DIR>`：实际调研目录，例如 `/home/user/project/.scratch/research/01-auth-module`
- `<BRIEF_PATH>`：`00-brief/brief.md` 路径
- `<SOURCE_FILES>`：研究对象相关的源码/资料文件清单（只列关键路径，不要放完整内容）
- `<ROLES>`：实际启用的角色与对应产出文件（按 `team-roles.md` 原型 + 领域预设确定）

## 脚本结构

```javascript
export const meta = {
  name: '<topic>-research',
  description: '多 Agent 并行调研 <topic>',
  phases: [
    { title: 'Phase 1: 并行初稿' },
    { title: 'Phase 2: 红队对抗' },
    { title: 'Phase 3: 评审委员会汇总' },
  ],
};

const RESEARCH_DIR = '<RESEARCH_DIR>';
const BRIEF_PATH = `${RESEARCH_DIR}/00-brief/brief.md`;

// Phase 1: 并行初稿
phase('Phase 1: 并行初稿');

const p1Agents = [
  {
    label: '<角色名>',
    prompt: `你是本次调研的 <角色名>。请基于 <SOURCE_FILES> 进行调研。

输出要求：
1. 使用 Write 工具写入文件：${RESEARCH_DIR}/<output-path>.md
2. 内容结构：...
3. 每条结论必须标注证据来源（文件路径 + 函数/对象名）。
4. 先阅读 ${BRIEF_PATH} 了解调研总则。

最终回复只需确认文件已写入，并给出 3-5 句话摘要。`,
  },
  // ... 更多角色
];

await parallel(p1Agents.map(a => () => agent(a.prompt, {
  label: a.label,
  phase: 'Phase 1: 并行初稿',
  effort: 'high',
})));

log('Phase 1 初稿完成');

// Phase 2: 红队对抗
phase('Phase 2: 红队对抗');

const p2Agents = [
  {
    label: '<红队角色名>',
    prompt: `你是红队中的 <角色名>。请阅读 Phase 1 已产出的文件：...

输出要求：
1. 使用 Write 工具写入文件：${RESEARCH_DIR}/04-redteam-review/<output>.md
2. ...
3. 每条质疑必须具体，并引用被质疑的文件与段落。`,
  },
  // ... 更多红队角色
];

await parallel(p2Agents.map(a => () => agent(a.prompt, {
  label: a.label,
  phase: 'Phase 2: 红队对抗',
  effort: 'high',
})));

log('Phase 2 红队对抗完成');

// Phase 3: 评审委员会汇总
phase('Phase 3: 评审委员会汇总');

const synthesisPrompt = `你是本次调研的评审委员会。请阅读 Phase 1 和 Phase 2 的所有产出文件：...

输出要求：
1. 使用 Write 工具写入文件：${RESEARCH_DIR}/05-synthesis/final-report.md
2. 文件结构：执行摘要、范围与方法、现状总览、关键发现、stories 汇总、设计建议、未决问题、附录。
3. 统一文风，消除矛盾。
4. 对红队质疑给出裁决。`;

await agent(synthesisPrompt, {
  label: '评审委员会汇总',
  phase: 'Phase 3: 评审委员会汇总',
  effort: 'xhigh',
});

log('Phase 3 评审委员会汇总完成');

return { status: 'completed', researchDir: RESEARCH_DIR };
```

## 关键设计点

1. **让 agent 自己写文件**：每个 agent 的 prompt 明确要求使用 Write 工具写入指定路径。
2. **Phase 1 使用 parallel**：所有初稿角色同时运行。
3. **Phase 2 依赖 Phase 1 文件**：由于 `parallel` 是 barrier，Phase 1 全部完成后才进入 Phase 2。
4. **Phase 3 单 agent 汇总**：由一个高 effort agent 统一审阅并产出最终报告。
5. **失败处理**：Workflow 完成后检查失败 agent，单独重新运行补全（见 SKILL.md 阶段 3）。

## 常见角色 prompt 模板（通用原型）

### 资料考古员

```
你是资料考古员。请对 <topic> 相关源码/资料做完整盘点。
必须覆盖：<SOURCE_FILES>
输出：${RESEARCH_DIR}/01-raw-findings/source-inventory.md
包含：总体分布、关键文件清单表、调用链/数据结构、关键词索引、待深入文件清单。
每条结论标注证据来源。
```

### 场景切片员

```
你是场景切片员。请从 <topic> 资料中挑选 4-6 类代表性实例，做成使用者视角 + 数据流切片。
输出：${RESEARCH_DIR}/01-raw-findings/usage-slices.md
同时产出 actor 视角 stories：${RESEARCH_DIR}/02-perspectives/actor-stories.md
```

### 现代实践评审员

```
你是现代实践评审员。请对标当前主流做法，评估 <topic> 的当代适用性与过时风险。
输出：${RESEARCH_DIR}/03-design-options/modern-practice-review.md
```

> 选用领域预设时，把上述通用角色名替换为预设中的特化角色名（见 `domain-presets/`），产出文件路径按预设映射表调整。

## 注意事项

- 不要把完整源码清单放进 prompt，只列出关键文件路径。
- 每个 agent 的 prompt 末尾要求"最终回复只需确认文件已写入，并给出 3-5 句话摘要"，避免 agent 在最终回复中重复全文。
- 如果某个 agent 经常 429 失败，可以降低并行度或在 Phase 1 中分批运行。
- 批判性外部视角角色按 grilling 确认的视角范围启用，不必全部启用。
