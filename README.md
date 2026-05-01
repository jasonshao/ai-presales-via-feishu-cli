# 飞书 CLI 售前 Skill

> 🌏 Languages: **中文** · [English](README.en.md)
>
> 把飞书里的一条销售报备，30 分钟内变成一份可对客户讲的《客户解决方案》初稿 —— 全程通过 `lark-cli` 读写飞书，由一个 **可移植的 Agent Skill 文档** 驱动推理。

这是一个开源的 **AI 售前工作流 Skill**：把内部跑通的售前流程，封装成一份可移植的 `SKILL.md` + 三个轻量 Python 脚本 + 一套虚构 Demo 数据。任何接好 `lark-cli`、能读文件、能调用 shell 的 Agent 都能拿来就用：**Claude Code、Codex、OpenClaw、Cursor、自研 Agent SDK 通吃**。

---

## 目录

- [为什么要做这个](#为什么要做这个)
- [这个 Skill 干什么](#这个-skill-干什么)
- [支持哪些 Agent](#支持哪些-agent)
- [一个完整的 Demo 走查](#一个完整的-demo-走查)
- [30 秒离线 Demo](#30-秒离线-demo)
- [在线飞书 Demo](#在线飞书-demo)
- [架构与设计原则](#架构与设计原则)
- [飞书 CLI 集成点](#飞书-cli-集成点)
- [扩展性：怎么加一个新场景](#扩展性怎么加一个新场景)
- [测试与隐私扫描](#测试与隐私扫描)
- [仓库结构](#仓库结构)
- [5 分钟快速验证](#5-分钟快速验证)
- [设计文档](#设计文档唯一事实源)
- [贡献 / License](#贡献)

---

## 为什么要做这个

B2B 售前有一个高频且耗时的环节：**销售报备进来 → 售前要在 30 分钟到 2 小时内，给销售一份能对客户讲的《客户解决方案》初稿**。

实操中常见的痛点：

1. **场景识别凭经验**。同一份报备，新人可能识别成 A 场景，老人识别成 B 场景，结论差很远。
2. **报备信息不全**。销售常漏问关键信息（主体一致性、并发量、对账格式等），售前要往返追问 3-5 轮才能起草。
3. **方案模板散落各处**。客户背景、推荐方案、相似案例、待澄清事项分散在十几个 Wiki/文档里，每次都要手动拼。
4. **案例库没用起来**。历史成功案例多数躺在群聊截图和邮件里，新人根本搜不到。

结果就是：**售前是一线最贵的瓶颈之一**。一个初级售前一天能产出 3-5 份方案就算高产，且质量参差不齐。

这个 Skill 想做的事很具体：**把售前从「经验驱动的手工活」变成「Skill 驱动的协作流」**。

- 销售报备一进飞书多维表格 → Agent 自动识别场景 + 找出缺口 + 给销售一份「待确认清单」 + 起草客户方案
- 售前的角色从「写初稿」变成「审稿和定调」，单份方案产出时间目标 ≤ 30 分钟
- 知识沉淀：场景包、产品能力、案例库都进飞书多维表格，每次新场景上线只需要加几行数据，不改代码

## 这个 Skill 干什么

[`skills/ai-presales/SKILL.md`](skills/ai-presales/SKILL.md) 是整个仓库的核心。它会指挥 Agent 完成下面这套售前闭环：

```
飞书销售报备进表
        │
        ▼
[1] 读取报备 + 场景包/产品能力/案例库
        │     (lark-cli base +record-list)
        ▼
[2] 场景识别（关键词匹配 → 置信度 + 命中关键词）
        │
        ▼
[3] 缺口诊断（5-8 项「待销售确认清单」）
        │
        ▼
[4] 方案撰写（Markdown：背景 / 推荐方案 / 相似案例 / 待澄清）
        │
        ▼
[5] 写回飞书云文档 + 更新项目状态
              (lark-cli docs +create / base +record-upsert)
```

两种运行模式：

- **离线模式（Offline）**：不需要任何飞书凭证，跑 `examples/offline/` 下打包好的虚构样例数据。适合 CI、二次开发、跨环境验证。
- **在线模式（Live）**：通过 `examples/live/env.example` 里的环境变量指向真实的飞书多维表格。

## 支持哪些 Agent

[`SKILL.md`](skills/ai-presales/SKILL.md) 是一份 **静态的、可移植的 Agent 指令文档**。它的格式（YAML frontmatter + Markdown 正文）是 Claude Code 推广开来的约定，**但正文是 agent-neutral 的** —— 任何能「读文件 + 跑 shell」的 Agent 平台都能直接驱动这套工作流。

| Agent 平台 | 怎么接入 | 备注 |
|---|---|---|
| **Claude Code** | 把 `skills/ai-presales/` 软链到 `~/.claude/skills/`，或者直接在仓库里用 | 原生格式，触发词命中后自动加载 |
| **Codex**（Anthropic） | Clone 仓库后给 Codex 一个 prompt，例如「请按照 `skills/ai-presales/SKILL.md` 处理客户 X 的报备」 | Codex 会自己读 SKILL.md 并按步骤执行 |
| **OpenClaw** | 把 SKILL.md 作为 system instruction 加载，或当成插件 / 工作流文档 | 同 Codex 模式 |
| **Cursor / Continue** | 把 SKILL.md 内容作为 `.cursorrules` 或 prompt 模板的一部分 | 推理由 IDE 内 Agent 完成，shell 命令在终端里跑 |
| **自研 Agent SDK** | 把 SKILL.md 当 system prompt + 给 Agent 一个 `bash` 工具 | 最通用方案，几行代码就能跑 |
| **任何能力相当的 LLM Agent** | 同上 | 模型推荐能力 ≥ Claude Sonnet 4.5 / GPT-4 级别 |

唯一硬性依赖只有两个：

1. Agent 能读取本仓库的文件
2. Agent 能调用 `lark-cli`（或者退化为离线模式，只读本地 JSON）

**为什么不写死一个 agent 平台**：售前是一个非常实际的业务场景，不同公司用的 Agent 平台不一样。这个 Skill 的价值在于「飞书 + 售前业务流程」的封装，不在于绑定某一个 Agent 厂商。仓库的 `examples/offline/expected-output.md` 是确定性 Golden file，**任何 agent 跑出来的最终方案都应该跟这份基准接近**，差异只来自 agent 自己的语言润色。

## 一个完整的 Demo 走查

仓库里打包了一份虚构案例 —— 茶饮连锁品牌「Beanlight Tea」想接小程序支付。

**输入**：[`examples/offline/sales-report.json`](examples/offline/sales-report.json)（节选）

```text
客户：Beanlight Tea（虚构 Demo 公司）
行业：餐饮 / 茶饮连锁
报备摘要：约 120 家商场柜台店，想做带支付的品牌小程序，会员预订、积分。
         已有 POS 但没有线上点单。希望 6-8 周上线。
现状系统：自建 POS。无电商。财务每天 Excel 导出对账。
交易规模：旺季约 60,000 单/日，客单 28 元。
预期方案：自有 WeChat Pay 商户号下的小程序 + 支付，财务对账文件每日推送。
报备时间：软目标 2026-07-15 上线。
```

**Skill 跑完之后产出**（节选，下方为中文意译；完整原文见 [`examples/offline/expected-output.md`](examples/offline/expected-output.md)）：

```markdown
# 项目识别卡

- 客户：Beanlight Tea（虚构 Demo 公司）
- 候选场景：小程序支付 · API 接入（PAY_API_MINIPROGRAM）
- 置信度：高（命中分数：6）
- 命中关键词：小程序、微信小程序、应用内支付、API 接入、预订、品牌小程序
- 完整度：86%（7 项确认清单已覆盖 6 项）
- 期限：软目标 2026-07-15 上线

---

# 待销售确认清单
_7 项中，已覆盖 6 项，待确认 1 项。_

## 待确认 —— 起草前先问销售
- v1 是否需要支持退款、部分退款、售后工单？

---

# Beanlight Tea × [贵司] 客户解决方案初稿

> Demo 数据 —— 虚构客户。发出前请人工 Review。

## 1. 客户背景与需求
   ...
## 2. 推荐方案
   - 小程序支付 SDK + API：客户保留完整 UI 控制权，我方负责
     订单创建 / 拉起支付 / 异步回调 / 对账 等支付链路。
       - 约束：主体一致性必须满足。
   - 每日对账与财务导出：T+1 SFTP 推送。
       - 约束：对账文件格式需在 Discovery 阶段谈定。
## 3. 相似案例
   - CASE-DEMO-A1（茶饮连锁，约 80 家店，对账走 SFTP，7 周上线）
   - CASE-DEMO-B2（咖啡连锁，约 200 家店，复用手机号会员体系）
## 4. 假设与待澄清
   - v1 是否需要支持退款、部分退款、售后工单？
   - 主体一致性提示：签约主体 = 微信支付商户主体
```

> 上面是中文意译，方便中文读者快速读懂结构。仓库内的 Golden file（`expected-output.md`）和渲染器输出当前是英文，因为示例数据走的是 B2B 售前常见的英文术语；改成中文输出只需要替换 `render_solution.py` 里的章节标题模板，不影响整体设计。

整个过程对人的要求只剩三件事：

1. 把销售报备写进多维表格（销售本来就要做的事）
2. 看一眼 Agent 给的「待确认清单」，回去问销售
3. 看一眼 Agent 起草的方案，调整措辞，发给客户

## 30 秒离线 Demo

```bash
python skills/ai-presales/scripts/validate_sample_data.py examples/offline
python skills/ai-presales/scripts/collect_context.py --offline examples/offline --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md
```

第三条命令产出的文件，会跟 [`examples/offline/expected-output.md`](examples/offline/expected-output.md) 完全一致 —— 包括项目识别卡 + 待确认清单 + 客户方案初稿三大产物。

> 不需要飞书账号、不需要 lark-cli、不需要 Token。打开仓库就能跑。

## 在线飞书 Demo

```bash
# 1. 确认 lark-cli 已经登录
lark-cli auth status   # tokenStatus: valid

# 2. 配置 Demo 用的多维表格
cp examples/live/env.example ~/.presales.env
# 填写 6 个 PRESALES_* 变量后：
set -a; source ~/.presales.env; set +a

# 3. 用同一套脚本跑在线模式
python skills/ai-presales/scripts/collect_context.py --live --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md

# 4. 把方案草稿写进 Demo 用的飞书云文档目录
lark-cli docs +create \
  --folder-token "$PRESALES_OUTPUT_FOLDER_TOKEN" \
  --title "Customer Solution Draft (demo)" \
  --markdown @/tmp/customer-solution.md

# 5. 更新项目状态
lark-cli base +record-upsert \
  --base-token "$PRESALES_BASE_TOKEN" \
  --table-id "$PRESALES_STATUS_TABLE" \
  --json '{"project_id":"demo-2026-001","status":"draft_generated","confidence":"high"}'
```

完整的在线 runbook 见 [`examples/live/feishu-command-examples.md`](examples/live/feishu-command-examples.md)。

## 架构与设计原则

```
┌──────────────────────────┐
│  飞书多维表格销售报备    │
└────────────┬─────────────┘
             │  lark-cli base +record-list
             ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│  collect_context.py      │ ◄─── │  examples/offline/*.json │
│  （离线 │ 在线 双模式）  │      │  （离线兜底数据）        │
└────────────┬─────────────┘      └──────────────────────────┘
             │  context.json（确定性结构化上下文）
             ▼
┌──────────────────────────┐
│  render_solution.py      │  ← Skill 让 Agent 在这一步上面再做推理
│  → Markdown              │     - 项目识别卡
│                          │     - 待销售确认清单
│                          │     - 客户解决方案初稿
└────────────┬─────────────┘
             │  lark-cli docs +create
             │  lark-cli base +record-upsert
             ▼
┌──────────────────────────┐
│  飞书云文档（方案初稿）  │
│  + 项目状态表更新        │
└──────────────────────────┘
```

**核心设计原则：脚本做确定性，Skill 做推理**

- **脚本是确定性的**。同一份输入，每次跑结果都一样。这让测试、CI、Diff 校验成为可能。
- **Skill 拥有推理权**。场景识别的细微差别、案例匹配的取舍、客户措辞的语气 —— 都需要 Agent 真正动脑，硬塞进脚本只会变成脆弱的模板。
- **添加场景不改代码**。多一个场景？多维表格里加一行就行，渲染器不需要改。

**为什么用 `lark-cli` 而不是直接写 SDK**

- 鉴权直接复用用户已有的飞书 CLI 登录态，不需要单独跑 OAuth
- CLI 表层比底层 API 稳定得多，飞书 API 升级不会动到 Skill
- 不熟悉的命令时，Agent 可以 `lark-cli --help` / `lark-cli schema` 自我发现，而不是凭空猜参数
- 飞书官方主推的标准接入方式，未来跨语言/跨平台都有保障

## 飞书 CLI 集成点

| 飞书 CLI 集成点 | 在仓库里的位置 |
|---|---|
| 鉴权检查 `lark-cli auth status` | [`SKILL.md`](skills/ai-presales/SKILL.md) 在线流程第 1 步 |
| 多维表格读 `lark-cli base +record-list` | [`collect_context.py`](skills/ai-presales/scripts/collect_context.py) 的 `load_live` 函数 |
| 多维表格表列举 `lark-cli base +table-list` | [`feishu-command-examples.md`](examples/live/feishu-command-examples.md) §2 |
| 多维表格写 `lark-cli base +record-upsert` | 在线 runbook 第 5 步 |
| 云文档创建 `lark-cli docs +create` | 在线 runbook 第 4 步 |
| Wiki/Docx 拉取 `lark-cli docs +fetch` | `SKILL.md` 中的可选决策指南读取 |
| Schema 发现 `lark-cli schema …` | `SKILL.md` 排障章节 |

Skill 里明确告诉 Agent：遇到不确定的命令形态，**优先 `lark-cli --help` / `lark-cli schema`**，而不是凭记忆猜参数。这样飞书 CLI 升级时整套流程不容易腐烂。

## 扩展性：怎么加一个新场景

假设你想加一个「门店收银设备升级评估」场景，步骤就 3 步：

1. 在 [`examples/offline/scenario-packages.json`](examples/offline/scenario-packages.json) 里加一条记录（schema 见 [`scenario-package-schema.md`](skills/ai-presales/references/scenario-package-schema.md)）：
   ```json
   {
     "scenario_id": "POS_UPGRADE_ASSESS",
     "scenario_name": "Store POS upgrade assessment",
     "trigger_keywords": ["POS upgrade", "替换收银", "门店升级", "..."],
     "entry_conditions": ["..."],
     "confirmation_checklist": ["...", "..."],
     "decision_rules": ["if X then Y"],
     "supported_outputs": ["recognition card", "follow-up checklist"],
     "fallback_message": "..."
   }
   ```
2. 在 [`product-capabilities.json`](examples/offline/product-capabilities.json) 里把适配该场景的能力 `applicable_scenarios` 加上 `"POS_UPGRADE_ASSESS"`
3. 加一条虚构案例到 [`case-library.json`](examples/offline/case-library.json)，`scenario_tags` 含 `"POS_UPGRADE_ASSESS"`，`public_safe: true`

`pytest` 自动覆盖你新增的场景。**不需要改 Python 代码、不需要改 Skill、不需要改渲染器**。

线上版本同理 —— 直接在飞书多维表格里加一行就行。

## 测试与隐私扫描

```bash
python -m pytest -q
```

13 项测试覆盖：

- ✅ 样例数据通过 schema 校验
- ✅ 上下文收集器对 Demo 报备给出预期的 `PAY_API_MINIPROGRAM` 高置信匹配
- ✅ 渲染器输出包含设计文档 §10.3 要求的全部章节
- ✅ 渲染器输出与打包好的 [`expected-output.md`](examples/offline/expected-output.md) **逐字符相等**（Golden file 对比）
- ✅ 隐私扫描在全仓库范围内捕捉违禁 Token、被赋值的密钥、私有飞书 URL（黑名单详见 [`privacy-rules.md`](skills/ai-presales/references/privacy-rules.md)）

**隐私扫描尤其重要**：开源项目一旦有真凭实据漏进 commit（Token、生产客户的名字、内部链接……），git 历史就再也抹不干净。所以这条扫描是 CI 的拦门关，宁可严不可松。

## 仓库结构

```text
ai-presales-via-feishu-cli/
  README.md                            # 你正在看的中文版
  README.en.md                         # 英文版
  LICENSE                              # MIT
  pyproject.toml                       # Python 3.10+，唯一依赖：pytest
  skills/ai-presales/
    SKILL.md                           # ⭐ Skill 本体 —— 整个项目的心脏
    references/
      solution-template.md             # 客户方案 Markdown 模板
      scenario-package-schema.md       # 场景包字段规范
      base-schema.md                   # 飞书多维表格字段映射
      privacy-rules.md                 # 公开安全规则
    scripts/
      validate_sample_data.py          # 样例数据校验
      collect_context.py               # 上下文收集（离线 + 在线 双模式）
      render_solution.py               # Markdown 方案渲染（确定性）
  examples/
    offline/                           # 公开安全的虚构样例数据
      sales-report.json                #   销售报备（Beanlight Tea）
      scenario-packages.json           #   2 个场景包
      product-capabilities.json        #   3 个产品能力
      case-library.json                #   3 条虚构案例
      expected-output.md               #   Golden file（渲染器输出）
    live/                              # 在线模式
      env.example                      #   环境变量模板
      feishu-command-examples.md       #   完整 lark-cli runbook
  docs/
    architecture.md                    # 架构速读
    demo-script.md                     # 2-3 分钟 Demo 解说稿
    contest-submission.md              # 项目摘要 / 提交说明
    superpowers/specs/                 # 完整设计文档（约 600 行）
  tests/                               # pytest，含全仓库隐私扫描
```

## 5 分钟快速验证

5 分钟内完整跑一遍这个项目的最短路径：

```bash
# 1. clone
git clone https://github.com/jasonshao/ai-presales-via-feishu-cli
cd ai-presales-via-feishu-cli

# 2. 装依赖（仅 pytest）
python -m pip install --user pytest

# 3. 跑测试 —— 13 项全绿（约 0.5 秒）
python -m pytest -q

# 4. 跑离线 Demo
python skills/ai-presales/scripts/collect_context.py --offline examples/offline --out /tmp/c.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/c.json --out /tmp/s.md

# 5. 对比生成结果与 Golden file（应完全一致）
diff /tmp/s.md examples/offline/expected-output.md && echo "GOLDEN MATCH"

# 6. （可选）检查飞书 CLI 集成点
grep -rE "lark-cli" skills/ examples/ README.md | wc -l   # 至少 30+ 处
```

看代码的优先级建议：

1. [`skills/ai-presales/SKILL.md`](skills/ai-presales/SKILL.md) —— Skill 本体，10 分钟读完
2. [`docs/architecture.md`](docs/architecture.md) —— 架构速读
3. [`examples/offline/expected-output.md`](examples/offline/expected-output.md) —— 看 Skill 跑完长什么样
4. [`docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md`](docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md) —— 完整设计文档（深度阅读）

## 设计文档（唯一事实源）

完整设计文档位于 [`docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md`](docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md)。文档分别讲解了 Skill / 鉴权 / 知识访问 / 工作流编排 / 人机协同 / 输出资产 / 度量 7 个层面，是扩展或 Fork 本 Skill 的权威参考。

## 贡献

欢迎 Issue 和 PR，尤其是：

- 新的场景包（请遵守 [`scenario-package-schema.md`](skills/ai-presales/references/scenario-package-schema.md)）
- Skill 应该知道的新 `lark-cli` 集成点
- 更聪明的确定性场景匹配算法（当前刻意保持简单）
- 在线模式下的更多端到端 Demo 视频

提交 PR 即视为同意：贡献内容以 MIT 协议开源，且不包含任何内部客户数据。

## License

MIT。详见 [`LICENSE`](LICENSE)。
