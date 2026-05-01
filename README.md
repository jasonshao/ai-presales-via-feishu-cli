# 飞书 CLI 售前 Skill

> 🌏 Languages: **中文** · [English](README.en.md)

> 30 分钟内，把飞书里的一条销售报备转成一份可对客户讲的《客户解决方案》初稿。所有飞书读写都走 `lark-cli`，所有推理都由一个 Claude Code Skill（`SKILL.md`）驱动。

本仓库是 [飞书 CLI 创作者大赛](https://www.feishu.cn/community/article/event?id=7629204812755635148) GitHub 赛道的参赛作品，主攻 **最佳实践奖**。它把内部已经在用的 AI 售前工作流，打包成一个开源、可直接跑通的 Skill —— 任何接好 `lark-cli` 的 Agent 都能拿来就用。

---

## 这个 Skill 能干什么

[`skills/ai-presales/SKILL.md`](skills/ai-presales/SKILL.md) 是整个仓库的核心。它会指挥 Agent 完成下面这套售前闭环：

1. **读取销售报备**：通过 `lark-cli base +record-list`，从飞书多维表格里读出销售报备、场景包、产品能力、案例库等参考资料。
2. **场景识别**：判断该销售机会属于哪个售前场景，给出置信度和命中关键词。
3. **缺口诊断**：自动整理出一份 5–8 项的「待销售确认清单」，把销售必须回答的问题挑出来。
4. **方案撰写**：以 Markdown 格式起草一份对客解决方案 —— 包含客户背景、推荐方案、相似案例、待澄清事项四个部分。
5. **写回飞书**：通过 `lark-cli docs +create` 把方案落到飞书云文档，并通过 `lark-cli base +record-upsert` 更新项目状态。

两种运行模式：

- **离线模式（Offline）**：不需要任何飞书凭证，直接跑 `examples/offline/` 下打包好的样例数据。适合 CI、Demo 和评委复现。
- **在线模式（Live）**：通过 `examples/live/env.example` 里的环境变量指向真实的飞书多维表格。

## 快速上手

### 30 秒离线 Demo

```bash
python skills/ai-presales/scripts/validate_sample_data.py examples/offline
python skills/ai-presales/scripts/collect_context.py --offline examples/offline --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md
```

第三条命令产出的文件，会跟 [examples/offline/expected-output.md](examples/offline/expected-output.md) 完全一致 —— 包括项目识别卡 + 待确认清单 + 客户解决方案初稿三大产物。

### 在线飞书 Demo

```bash
# 1. 确认 lark-cli 已经登录
lark-cli auth status   # tokenStatus: valid

# 2. 配置 Demo 用的多维表格
cp examples/live/env.example ~/.presales.env
# 把 6 个 PRESALES_* 变量填上真实值，然后：
set -a; source ~/.presales.env; set +a

# 3. 用同一套脚本跑在线模式
python skills/ai-presales/scripts/collect_context.py --live --out /tmp/presales-context.json
python skills/ai-presales/scripts/render_solution.py --context /tmp/presales-context.json --out /tmp/customer-solution.md

# 4. 把方案草稿写进 Demo 用的飞书云文档目录
lark-cli docs +create \
  --folder-token "$PRESALES_OUTPUT_FOLDER_TOKEN" \
  --title "Customer Solution Draft (demo)" \
  --markdown @/tmp/customer-solution.md
```

完整的在线模式 runbook 见 [`examples/live/feishu-command-examples.md`](examples/live/feishu-command-examples.md)。

## 为什么这是一个真正的「飞书 CLI Skill」，而不是一段通用 Prompt

| 飞书 CLI 集成点 | 在仓库里的位置 |
|---|---|
| 鉴权检查 `lark-cli auth status` | [`SKILL.md`](skills/ai-presales/SKILL.md) 在线流程第 1 步 |
| 多维表格读 `lark-cli base +record-list` | [`collect_context.py`](skills/ai-presales/scripts/collect_context.py) 的 `load_live` 函数 |
| 多维表格写 `lark-cli base +record-upsert` | 在线 runbook 第 6 步 |
| 云文档创建 `lark-cli docs +create` | 在线 runbook 第 5 步 |
| Wiki/Docx 拉取 `lark-cli docs +fetch` | `SKILL.md` 中可选的决策指南读取 |
| Schema 发现 `lark-cli schema …` | `SKILL.md` 排障章节 |

Skill 里明确告诉 Agent：遇到不确定的命令形态，**优先 `lark-cli --help` 和 `lark-cli schema`**，而不是凭记忆猜参数。这样即使飞书 CLI 升级，整套流程也不容易腐烂。

## 仓库结构

```text
ai-presales-via-feishu-cli/
  README.md                            # 你正在看的中文版
  README.en.md                         # 英文版
  LICENSE
  pyproject.toml
  skills/ai-presales/
    SKILL.md                           # Skill 本体 —— 整个项目的心脏
    references/
      solution-template.md             # 客户方案模板
      scenario-package-schema.md       # 场景包 schema
      base-schema.md                   # 飞书多维表格字段映射
      privacy-rules.md                 # 公开安全规则
    scripts/
      validate_sample_data.py          # 样例数据校验
      collect_context.py               # 上下文收集（离线 + 在线）
      render_solution.py               # Markdown 方案渲染
  examples/
    offline/                           # 公开安全的虚构样例数据
    live/                              # 环境变量模板 + lark-cli runbook
  docs/
    architecture.md                    # 架构速读
    demo-script.md                     # 2-3 分钟 Demo 解说稿
    contest-submission.md              # 参赛说明
    superpowers/specs/                 # 完整设计文档
  tests/                               # pytest，含全仓库隐私扫描
```

## Demo 数据全部虚构

`examples/` 下所有数据都是**虚构**的。Demo 客户「Beanlight Tea」不存在，仓库内不包含任何真实的客户名称、内部案例、飞书 Token 或私有飞书链接 —— 详见 [`skills/ai-presales/references/privacy-rules.md`](skills/ai-presales/references/privacy-rules.md)。隐私扫描测试 [`tests/test_privacy_scan.py`](tests/test_privacy_scan.py) 会在每次 `pytest` 时把关，防止泄漏。

## 运行测试

```bash
python -m pytest -q
```

测试覆盖：

- 样例数据通过 schema 校验。
- 上下文收集器对 Demo 报备给出预期的场景匹配结果。
- 渲染器输出包含设计文档 §10.3 中要求的全部章节。
- 隐私扫描在全仓库范围内捕捉违禁 Token、被赋值的密钥、以及私有飞书 URL（黑名单详见 [`privacy-rules.md`](skills/ai-presales/references/privacy-rules.md)）。

## 设计文档（唯一事实源）

完整设计文档位于 [`docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md`](docs/superpowers/specs/2026-05-01-ai-presales-feishu-cli-skill-design.md)。文档分别讲解了 Skill / 鉴权 / 知识访问 / 工作流编排 / 人机协同 / 输出资产 / 度量 这 7 个层面，是扩展或 Fork 本 Skill 的权威参考。

## 贡献

欢迎 Issue 和 PR，尤其是：

- 新的场景包（请遵守 [`scenario-package-schema.md`](skills/ai-presales/references/scenario-package-schema.md)）。
- Skill 应该知道的新 `lark-cli` 集成点。
- 更聪明的确定性场景匹配算法（当前实现刻意保持简单）。

提交 PR 即视为同意：贡献内容以 MIT 协议开源，且不包含任何内部客户数据。

## License

MIT。详见 [`LICENSE`](LICENSE)。
