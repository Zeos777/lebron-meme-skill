# AGENTS.md — 给接手本项目的 AI Agent

本项目是纯 Markdown 的 Agent Skill（`lebron-meme`，v0.2.1），没有运行时依赖。改动前先读完本页，再按需读 README.md 和 CONTRIBUTING.md。用户使用简体中文，回复也用简体中文。

## 目录速查

- `.agents/skills/lebron-meme/`：可移植的 Skill 包。SKILL.md 是入口（保持在 500 行以内），`references/` 是按需加载的资料。
  - `meme-catalog.md`：素材，ID 为 `LM-xxx`，快速索引表和正文记录必须一一对应。
  - `source-notes.md`：来源，ID 为 `S0xx`，素材里出现的每个 URL 都必须在这里登记。
  - `image-index.md`：媒体线索，ID 为 `V0x`，全部标“否（尚无明确授权）”。
  - `humor-guide.md`：场景到幽默机制的映射。
- `tests/validate.py`：静态校验，只用标准库，不调用模型。
- `tests/run_chat_checks.py`：调用 Codex CLI 做真实多轮采样，**会消耗额度**。
- `tests/*-results.md`、`chat-output.md`、`chat-evidence.json`：各版本的历史测试证据，**不要改写旧结论**。
- `.tmp/`：被 git 忽略，存放原始 CLI 日志和 v0.2 改动前的基线快照。

## 必须遵守

1. 证据分级：A 级要有可读的官方或可靠采访来源，B 级要有可读的社区用法证据，C 级只放待核验区，不进生成池。不得编造原话、时间戳、作者、授权或“最早出处”。
2. 仓库里不放图片、GIF、视频二进制文件，校验会拦截。
3. commit、push、发布、删除重要文件之前，先向用户说明影响并等待确认。
4. 只有实际跑过的才能写“已验证”；单次样本不能写成“稳定通过”。

## 修改流程

1. 改素材或 Skill 文本。
2. 运行 `python tests/validate.py`，必须 PASS。
   - 出现 `WARNING: chat evidence predates edits` 是正常的：它表示行为证据描述的是旧文件，不算失败。
   - README 里手写的计数（候选数、A/B/C、来源数、媒体数）由校验器核对；改了数据要同步改 README。
3. 如果改动影响行为（SKILL.md、humor-guide.md 的规则或机制），发布前需要重新采样：
   `python tests/run_chat_checks.py --output-dir .tmp/<新目录>`
   必须用新目录，脚本拒绝覆盖旧证据。采样完成后，新建对应版本的结果文档，再运行 `python tests/validate.py --strict-evidence`，确认 PASS。
4. 版本号写在 SKILL.md 的 `metadata.version` 和 README 标题里，两处同步修改。

## 待办（按优先级）

- **P1**：README 里的计数目前要手动同步，需要的话可以改成从校验结果自动生成。
- **P2**：扩大行为采样：再做 2–3 段不同话题的多轮会话，加上若干“不该触发”的反例（普通代码问题、严肃求助）。
- **P2**：LM-012、LM-021 现为 B 级，但各只有一个可读例证；LM-012为夸赞性的社区修辞，S059是约2025年抓取的旧缓存，用户2026-10-17实时复审403。独立补源S062—S064失败，继续补独立来源及B站评论；原声、原图人物、授权和最早出处仍有缺口。LM-022、LM-027 已升 A（S057、S039）。浏览器连不上可直接HTTP读取；摘要不算正文，缓存须注明。
- **发布前**：v0.2.1 已另存当前版本行为证据（tests/chat-v0.2.1-evidence.json），完成六轮续接和一组11项探针，严格检查通过；之后再改Skill素材仍须重采样。历史证据不覆盖，结果见 tests/chat-v0.2.1-results.md。
- **P3**：精简测试文档，在首页放一张“当前状态”总表，过程细节移到附录。
- **P3**：媒体内容的实际核对和授权确认（不确认授权就不下载）。

`run_chat_checks.py` 和 `validate.py` 里把证据模型固定写成 `gpt-6.1-sol` / `high`。如果要换模型，两处要一起改，并在结果文档里写明。

当前版本用例可通过 `run_chat_checks.py --case-file tests/chat-v0.2.1-cases.md` 指定。新采样证据和回答须另存为版本文件；校验器优先检查当前版本，不覆盖旧测试结论。确定性回归测试：`python -m unittest discover -s tests -p test_evidence_validation.py -v`。
