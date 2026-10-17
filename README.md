# LeBron Meme Skill · v0.2.1

面向简体中文篮球社区的詹式幽默、梗百科与历史言论反差核验。用日常场景的反差制造笑点，同时分清真实采访、球迷戏仿和来源不完整的说法。

这是一个以Markdown为核心的Agent Skill，不需要前端、数据库、API服务或运行时依赖。AI回答仍有波动，来源记录用于约束事实，不能保证每次回答都好笑。

## 可以怎么用

下面是项目原创演示，**不是詹姆斯原话**：

> 我换了三款笔记软件，最后又用了记事本。  
> 三次转会，零次出场。先打开第一页，合同细节晚点再谈。

> 组队作业最后只剩我在写。  
> 手套上已经集齐写作、排版、查重和答辩四颗宝石，最后一颗叫“队友已读”。

三个核心模式：

| 模式 | 示例请求 |
| --- | --- |
| 幽默生成 | 用一句詹式幽默调侃项目延期；轻一点／火力足一点 |
| 梗百科 | “你知道的，某某是我兄弟”整段是原话吗？ |
| 反差核验 | 不止一个不止两个的豪言后来和什么结果形成反差？ |

也可以请求找图或视频来源。普通代码问题、严肃求助和未建立玩梗语境的聊天不应触发。

v0.2更重视聊天：先选评价对象与矛盾，默认一个主机制；用户要接梗就顺着推进，要换角度才切换。加入扉页战神、预测80分回忆、标签长推和三个篮筐四个素材方向，每条配多种原创改写与反例。事实边界保持明确，不用增加称号代替笑点。

## 安装与调用

**在这个项目中使用：**把完整项目放到本地，在项目根目录打开Codex。仓库级技能位于 `.agents/skills/lebron-meme/`，不需要执行安装脚本。用技能列表或输入 `$` 查找 `lebron-meme`，例如：

```text
$lebron-meme 用一句话调侃：我又把DDL记错了。
$lebron-meme 解释“智能腹股沟”，哪些是事实，哪些是网友的说法？
$lebron-meme 对比2014回家公开信与2018加盟湖人，先核实再说笑点。
```

自然请求“讲讲詹姆斯这个梗的出处”也可匹配。若新建文件后没有出现在技能列表，重新打开项目或重启Codex。目录发现与实际行为的本次测试证据见[测试记录](tests/test-results.md)，格式校验通过不等于所有行为已通过。

**给其他项目使用：**只复制整个 `lebron-meme` 目录（含LICENSE.txt和references），放到目标项目的 `.agents/skills/`，或个人技能目录 `~/.agents/skills/`。不要只复制SKILL.md，也不要覆盖已有同名技能。

从本项目根目录执行的Windows个人安装示例（由你自行执行）：

```powershell
$skillSource = Join-Path (Get-Location) '.agents\skills\lebron-meme'
$skillParent = Join-Path $env:USERPROFILE '.agents\skills'
$skillTarget = Join-Path $skillParent 'lebron-meme'
if (Test-Path -LiteralPath $skillTarget) { throw '已有同名技能，请先比较内容。' }
New-Item -ItemType Directory -Path $skillParent -Force | Out-Null
Copy-Item -LiteralPath $skillSource -Destination $skillTarget -Recurse
```

其他支持[Agent Skills标准](https://agentskills.io/specification)的Agent可按其宿主要求安装同一个目录；`agents/openai.yaml`是可选的Codex界面元数据。Codex发现和调用依据[官方说明](https://learn.chatgpt.com/docs/build-skills)。

## 素材与证据

核查日期为2026-10-16，2026-10-17补核四条。共34条候选，**默认可用34条**；这些条目不等于34种完全独立的幽默机制：

| 级别 | 数量 | 含义 |
| --- | --- | --- |
| A | 19 | 明确列出的历史事实或短引语有官方记录、原始文献或可靠采访报道支持 |
| B | 15 | 有可读社区证据的修辞、戏仿、话术和表情用法，不能当本人发言 |
| C | 0 | 待核验候选，排除于默认生成池 |

“最高的山，最长的河”（LM-012）和香蕉船兄弟（LM-021）在v0.2.1补读B站视频页标题、贴吧单帖后升为B，仅确认社区文字用法；不确认解说原声、香蕉船原图人物或媒体授权。阿克伦孩子（LM-022）和2011生活回应（LM-027）此前补读ESPN正文后升为A，只覆盖已读到的短引语。当前没有C级候选，不代表媒体内容、授权和最早出处已全部核验。A级条目只对各条明确列出的事实负责，例如有某段自述不等于自述内容均已独立证实。

[来源记录](.agents/skills/lebron-meme/references/source-notes.md)索引64个来源页面：41页正文可读，其余仅摘要、失败或外壳；可读页面也包括评分、合集说明和视频页标题，不全是原始采访。虎扑用于社区用法，贴吧提供跨圈聚合及单帖例证，B站提供作品线索和标题用法；NBA、SI公开信、同期AP报道等用于核实事实，新浪及企鹅体育等补中文传播背景。S058是夸赞性的社区修辞标题，S059是约2025年抓取的旧缓存，用户2026-10-17实时复审返回403；两条目前各只有一个可读用法例证，独立补源S062—S064均失败，不能声称已独立互证。没有读取B站评论区或确认最早原帖，平台覆盖仍偏虎扑，不能视作全平台流行度抽样。

[媒体索引](.agents/skills/lebron-meme/references/image-index.md)整理20条线索、18个不同入口：12条的页面信息/社区标签可读，8条仍待核验。**所有视频均未播放、图片未逐帧或逐图核验**。没有第三方媒体二进制，也未确认任何媒体可随仓库再分发。

## 目录与按需加载

- [SKILL.md](.agents/skills/lebron-meme/SKILL.md)：触发边界、三种模式、事实约束和多轮去重。
- [meme-catalog.md](.agents/skills/lebron-meme/references/meme-catalog.md)：快速选择表和逐条证据边界。
- [source-notes.md](.agents/skills/lebron-meme/references/source-notes.md)：来源、访问失败及核验范围。
- [image-index.md](.agents/skills/lebron-meme/references/image-index.md)：媒体作品链接、作者、许可状态。
- [humor-guide.md](.agents/skills/lebron-meme/references/humor-guide.md)：场景到幽默机制的映射与原创示范。
- [v0.1测试用例](tests/test-cases.md)、[v0.1测试记录](tests/test-results.md)：原18个场景及证据，保留原版本结论。
- [v0.2聊天用例](tests/chat-cases.md)、[v0.2聊天实测](tests/chat-results.md)：六轮真实会话、七项定向探针、人工质量判据和本次局限。
- [v0.2.1聊天用例](tests/chat-v0.2.1-cases.md)、[v0.2.1实测](tests/chat-v0.2.1-results.md)：当前版本的六轮真实续接和一组11项探针，覆盖四条补核素材；旧版本证据保持原样。
- [run_chat_checks.py](tests/run_chat_checks.py)：用CLI显式会话ID逐轮resume，保存耗时与读取行为。
- [validate.py](tests/validate.py)：仅用Python标准库检查结构、ID、证据链接及媒体声明。

入口先读相关条目；不要求每次加载全部资料。宿主需要支持读取本地参考文件，联网仅用于更新或补核验，离线也可使用已整理的材料。

## 验证与贡献

在根目录运行：

```powershell
python tests/validate.py
```

这是静态完整性检查，不调用模型，也不证明来源内容真实或输出自然。它也核对本页手写的素材、来源和媒体计数。开发时另运行skill-creator的quick_validate，并实际调用Codex。

校验器优先读取与Skill版本对应的 `tests/chat-v<版本>-evidence.json`，没有则检查旧证据；文件变化时给出WARNING。发布前改用 `python tests/validate.py --strict-evidence`，证据过期即判失败。v0.2.1已重新采样且严格检查通过，这不保证多次生成稳定好笑。接手维护的Agent请先读[AGENTS.md](AGENTS.md)。

要自行重跑v0.2聊天采样，可执行下面命令。它会调用模型、消耗额度，并创建一条本地CLI测试会话；固定gpt-6.1-sol / high，不自动降级。每轮只读，测试不联网检索，原始日志保存在.tmp并被Git忽略。重复运行需换一个输出目录，以保留前次证据：

```powershell
python tests/run_chat_checks.py --case-file tests/chat-v0.2.1-cases.md --output-dir .tmp/my-chat-check
```

脚本只是执行器，不自行给“好笑”打及格。人工需按对象、主机制、转折、自然度和接话表现判读。完整模型设置、结果和限制见各版本测试记录，不合并声称旧18项在新版本全部重新运行。

贡献方式见[CONTRIBUTING.md](CONTRIBUTING.md)。优先补原始采访、早期社区单帖、完整上下文和媒体许可，再扩充数量。不要转载整帖、整套梗图或捏造“全网最早”。

## 版权与定位

[MIT许可证](LICENSE)只适用于项目原创指令、编辑分析、例句和工具。第三方引语、照片、GIF、视频、商标及链接作品保留原权利，不因本项目MIT而获得再分发许可。链接不是授权；未经确认许可的媒体不下载进仓库。

本项目为非官方文化整理与创作工具，与LeBron James、NBA、球队及社区平台没有从属或背书关系。对公众职业表现可以调侃和反讽；未经证实的指控不作为事实。发现错误可按贡献说明给出反证和修正建议。

两条剩余候选各只有一个B级文字例证；后续仍需补充独立来源、最早出处和B站评论证据，实际核对媒体内容，并扩大真实多轮采样。v0.2.1已完成六轮续接与11项探针的一次采样；旧版本测试不据此改写，媒体仍无新增授权。

