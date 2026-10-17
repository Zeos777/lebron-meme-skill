# LeBron Meme Skill · v0.2.1

给 AI 助手装上一个“詹姆斯梗”技能：让它用中文篮球圈的玩梗方式帮你调侃日常小事，讲清楚某个梗是怎么来的，还能对比詹姆斯以前说过的话和后来的结果。它会分清哪些是本人真说过的，哪些是网友恶搞，哪些还查不到出处。

**什么是“技能”（Skill）？** 就是一个装着说明书和资料的文件夹。装进 Claude Code、Codex 这类 AI 助手后，它在聊到相关话题时会自动翻看这份说明书照着做。这个技能全是文字文件，不用装别的软件，也不用联网就能用。

注意：AI 每次回答都不完全一样，不保证每句都好笑；资料只是帮它少说错话。

## 快速上手

**第 1 步：准备 Node.js。** 安装命令要用到它。没装过的话，去 [nodejs.org](https://nodejs.org/) 下载安装（选 LTS 版，一路“下一步”即可）。

**第 2 步：打开终端，粘贴下面这行，回车。**（Windows 用“终端”或 PowerShell，Mac 用“终端”App）

```bash
npx skills add Zeos777/lebron-meme-skill -g
```

它会列出你电脑上装了的 AI 助手（Claude Code、Codex、Cursor 等），用空格勾选要装的，回车确认。`-g` 表示装给你自己，以后在任何文件夹里都能用。

**第 3 步：重新打开 AI 助手，直接说：**

```text
用一句詹式幽默调侃：我又把DDL记错了。
```

如果它没反应，可以点名叫它：Claude Code 里输入 `/lebron-meme`，Codex 里输入 `$lebron-meme`，后面接你的问题。

以后想更新，运行 `npx skills update`；不想要了，运行 `npx skills remove lebron-meme -g`。

## 它能做什么

下面两段是本项目自己编的示范，**不是詹姆斯原话**：

> 我换了三款笔记软件，最后又用了记事本。  
> 三次转会，零次出场。先打开第一页，合同细节晚点再谈。

> 组队作业最后只剩我在写。  
> 手套上已经集齐写作、排版、查重和答辩四颗宝石，最后一颗叫“队友已读”。

三种主要用法：

| 用法 | 你可以这样问 |
| --- | --- |
| 玩梗调侃 | 用一句詹式幽默调侃项目延期；轻一点／火力足一点 |
| 讲梗的来历 | “你知道的，某某是我兄弟”整段是原话吗？ |
| 前后说法对比 | 不止一个不止两个的豪言，后来结果怎么样？ |

也可以让它找相关图片或视频的出处。

**它不会乱插嘴：**你问普通的代码问题、认真求助，或者没在聊这个话题时，它不会突然开始玩梗。聊天中也能接着上一句的梗继续，你说“换个角度”它才换。

## 其他安装方式

### 只装到某一个项目

在那个项目的文件夹里运行（去掉 `-g`）：

```bash
npx skills add Zeos777/lebron-meme-skill
```

想跳过勾选、直接指定装给谁，在末尾加上 `-a 助手名 -y`，例如：

```bash
npx skills add Zeos777/lebron-meme-skill -g -a claude-code -a codex -y
```

### 不想装 Node.js：手动复制

这个技能就是仓库里的 `.agents/skills/lebron-meme` 文件夹。把**整个文件夹**复制到下面的位置就行（`~` 指你的用户文件夹，Windows 上一般是 `C:\Users\你的用户名`）：

| AI 助手 | 复制到 |
| --- | --- |
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.agents/skills/` |

要整个文件夹一起复制，别只拿 SKILL.md（它要用到里面的资料）。如果目标位置已经有同名文件夹，先看看是不是旧版本，别直接覆盖。

Mac / Linux 用户可以用这一行命令代劳（装给 Claude Code；装给 Codex 就把最后的 `~/.claude/skills/` 换成 `~/.agents/skills/`）：

```bash
git clone --depth 1 https://github.com/Zeos777/lebron-meme-skill.git /tmp/lebron-meme-skill && mkdir -p ~/.claude/skills && cp -R /tmp/lebron-meme-skill/.agents/skills/lebron-meme ~/.claude/skills/
```

Windows 用户先下载本仓库并解压，在解压出的文件夹里打开 PowerShell，运行下面这段（装给 Codex；装给 Claude Code 就把第二行的 `.agents` 换成 `.claude`）：

```powershell
$skillSource = Join-Path (Get-Location) '.agents\skills\lebron-meme'
$skillParent = Join-Path $env:USERPROFILE '.agents\skills'
$skillTarget = Join-Path $skillParent 'lebron-meme'
if (Test-Path -LiteralPath $skillTarget) { throw '已有同名技能，请先比较内容。' }
New-Item -ItemType Directory -Path $skillParent -Force | Out-Null
Copy-Item -LiteralPath $skillSource -Destination $skillTarget -Recurse
```

### 直接在本仓库里用 Codex

下载本仓库后，在仓库文件夹里打开 Codex 就能直接用，不用安装。Claude Code 不会自动识别这个位置，请用上面的命令安装。

装好后没出现？重新打开 AI 助手试试。其他支持 [Agent Skills 标准](https://agentskills.io/specification) 的助手也能用同一个文件夹，具体放哪里看各自的说明。Codex 的官方说明见[这里](https://learn.chatgpt.com/docs/build-skills)。

## 资料靠谱吗

资料核查于 2026-10-16，10-17 又补查了四条。共34条候选梗，**默认可用34条**（注意：34 条不等于 34 种不同的笑法）。每条梗都按证据强弱分了级：

| 级别 | 数量 | 意思 |
| --- | --- | --- |
| A | 19 | 有官方记录或靠谱的采访报道，能确认是真事、真说过（只确认写明的那部分） |
| B | 15 | 能找到网友真实在这么用，但属于网友恶搞或模仿，不能当本人说的话 |
| C | 0 | 还没查实的候选，AI 默认不会拿来用 |

目前 C 级是 0 条，但这不代表一切都查清了：视频内容、图片授权和“最早是谁先说的”大多还没确认。

一些要知道的不足：

- **两条梗的证据偏薄。**“最高的山，最长的河”（LM-012）和香蕉船兄弟（LM-021）各只找到一个网友用法的例子，只能说明网上有人这么用，不能确认解说原声或照片里是谁。其中香蕉船兄弟的例子是约 2025 年的网页旧存档，2026-10-17 再打开原网页已无法访问；另外找的三个独立来源（S062—S064）都没能读到内容。
- **来源以虎扑为主**，还有贴吧、B站、NBA 官网、新闻报道等，不能代表全网的流行程度；B站评论区没看过。
- [来源记录](.agents/skills/lebron-meme/references/source-notes.md)一共索引64个来源页面，其中 41 页能读到正文，其余只看到摘要、打不开或只有空壳页面。
- [媒体索引](.agents/skills/lebron-meme/references/image-index.md)整理20条线索，来自18个不同入口：12条的页面信息/社区标签可读，8条仍待核验。**所有视频都没播放过，图片也没逐张看过**，仓库里不存任何图片或视频。

## 项目里都有什么

技能本体（装的就是这部分）：

- [SKILL.md](.agents/skills/lebron-meme/SKILL.md)：给 AI 看的说明书，写着什么时候用、怎么用、哪些话不能乱说。
- [meme-catalog.md](.agents/skills/lebron-meme/references/meme-catalog.md)：梗的清单，每条写清来历和证据。
- [source-notes.md](.agents/skills/lebron-meme/references/source-notes.md)：所有来源链接，以及哪些能打开、查到了什么程度。
- [image-index.md](.agents/skills/lebron-meme/references/image-index.md)：图片、视频的出处链接、作者和授权情况。
- [humor-guide.md](.agents/skills/lebron-meme/references/humor-guide.md)：什么场景配什么笑法，附原创示范。

AI 每次只翻看用得上的那几条，不会一次读完全部资料。

测试记录（给想了解效果的人看）：

- [v0.1 测试用例](tests/test-cases.md)、[v0.1 测试记录](tests/test-results.md)：最早的 18 个场景测试。
- [v0.2 聊天用例](tests/chat-cases.md)、[v0.2 聊天实测](tests/chat-results.md)：一段六轮的真实对话，加七个专门测试的问题。
- [v0.2.1 聊天用例](tests/chat-v0.2.1-cases.md)、[v0.2.1 实测](tests/chat-v0.2.1-results.md)：当前版本的六轮对话和 11 个专门测试的问题。

每个版本的测试结果都单独保留，不会被新版本覆盖。v0.2.1 只完整测过一轮，不代表每次都能这么好笑。

## 给想参与改进的人

规则见[贡献指南](CONTRIBUTING.md)。最欢迎的是：补充原始采访、早期网友帖子、完整上下文和图片视频的授权信息，而不是单纯多加几条梗。请不要整段转载帖子、整套搬运梗图，或者声称自己找到了“全网最早出处”却没有证据。

改完之后，在仓库文件夹里运行这个检查（需要 Python，不会调用 AI，也不花钱）：

```powershell
python tests/validate.py
```

它检查文件格式、编号对不对得上、链接有没有登记，以及本页写的数量和资料是否一致。看到 `PASS` 就是通过。它只能查格式，查不出内容是否真实、回答是否自然。准备发布新版本时，改用 `python tests/validate.py --strict-evidence`：如果技能内容改过、但还没重新测试，它会报错。

如果改动会影响 AI 的回答方式，需要重新做一轮真实对话测试。下面这个命令会真的调用 AI，**会消耗额度**，测试记录存在 `.tmp` 文件夹（不会上传到 GitHub）。每次要换一个新的文件夹名，免得覆盖上次的结果：

```powershell
python tests/run_chat_checks.py --case-file tests/chat-v0.2.1-cases.md --output-dir .tmp/my-chat-check
```

测试脚本只负责跑对话，好不好笑要人来判断：看它有没有抓准调侃对象、转折够不够、说话自不自然、接梗接得顺不顺。用哪个模型、具体结果和不足都写在各版本的测试记录里。用 AI 来维护这个项目的话，先让它读 [AGENTS.md](AGENTS.md)。

## 版权说明

[MIT 许可证](LICENSE)只管本项目自己写的内容：说明书、整理分析、原创例句和测试工具。詹姆斯的原话、照片、动图、视频、商标和链接里的作品，版权仍归原作者，不会因为本项目用了 MIT 就能随便转载。放了链接不等于有授权，没确认授权的图片视频不会下载进仓库。

这是一个非官方的整理和创作工具，和勒布朗·詹姆斯本人、NBA、各球队及各社区平台都没有关系，也没有得到他们的认可。可以拿公开的球场表现开玩笑、反讽，但没证实的指控不会当成事实来说。发现错误欢迎按贡献指南提出，附上反证和修改建议。

接下来还要做：给那两条证据偏薄的梗补独立来源、最早出处和 B站评论，真正打开媒体内容核对，以及做更多真实对话测试。
