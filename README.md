# 纸片动画导演

> 把故事做成一部真正“演起来”的纸片动画：空间可信、人物连贯、动作有因果、声音有归属。

`paper-animation-director` 是一套面向连续叙事纸片动画的导演与制作规程。它适用于剪纸动画、皮影动画、宣纸水彩故事、非遗宣传片和历史题材短片，尤其适合那些不能靠“几张漂亮图片 + 平移”糊过去的项目。

它是一个**纯文件、跨工具、可项目化复用**的 skill：核心由 Markdown 规程、参考文档、审计脚本和最小项目模板组成，不绑定某一家模型或某一个 IDE。只要工具能够读取 Markdown 规则、运行项目命令并调用图像/音频/视频工具，就可以接入。

## 兼容哪些工具？

| 工具 | 推荐接入方式 | 调用方式 |
| --- | --- | --- |
| OpenAI Codex | 安装到 Codex skills 目录，或放进当前工作区的 skill 目录 | `Use $paper-animation-director ...` |
| Cursor | 放入项目 `.cursor/` 规则目录或工作区文档，并保留完整 `references/`、`scripts/` | 在 Composer/Agent 中引用 `paper-animation-director` |
| Cloud Code / Claude Code 类工具 | 放入项目 `.claude/skills/`，或将 `SKILL.md` 加入项目 instructions | `Read paper-animation-director/SKILL.md ...` |
| 其他 Markdown Rules / Agent 工具 | 把 `SKILL.md` 作为主规则，把 `references/` 作为按需参考 | 先读主规则，再按制作阶段读 reference |

这里的“兼容”指文件和工作流兼容，不代表这些工具都提供相同的图像生成、TTS 或视频渲染 API。模型生成、Fish Audio、HyperFrames、FFmpeg 等能力由宿主工具或项目环境提供。

## 为什么不绑定单一平台？

纸片动画导演的核心判断应该跨平台保持一致：

- 空间是否成立，不取决于使用哪个 IDE；
- 角色是否完整，不取决于使用哪一个图像模型；
- 台词是否归属正确，不取决于使用哪个 TTS 服务；
- 交付是否可信，要看渲染帧和音视频探测，不看某个预览面板的截图。

因此平台适配只负责“如何加载这套规则”，而本 skill 负责“应该如何做判断”。

## 目录

- [兼容哪些工具](#兼容哪些工具)
- [安装与快速开始](#快速开始)
- [八道制作门](#八道制作门)
- [资产架构](#资产架构什么时候整合什么时候分层)
- [角色一致性](#角色一致性最低标准)
- [历史题材空间准则](#历史题材的空间准则)
- [声音与字幕](#声音和字幕的三条底线)
- [三次审片](#三次审片)
- [作为开源项目使用](#作为开源项目使用)
- [安全与许可证](#安全与隐私)

![纸片动画导演的核心流程](assets/project-template/README-flow.svg)

> 如果上面的流程图在当前查看器中不可见，可直接看下方的 Mermaid 版本。

```mermaid
flowchart LR
  A[剧本与史料] --> B[俯视平面]
  B --> C[完整资产决策]
  C --> D[最难镜头基准]
  D --> E[多帧动作]
  E --> F[配音字幕时间轴]
  F --> G[静音/声音/画音三检]
  G --> H[渲染与交付]
  G -.不通过.-> B
```

## 这套 skill 解决什么问题？

它专门解决纸片动画中最容易被忽略、但最影响观感的事情：

| 问题 | 导演规则 |
| --- | --- |
| 人物像贴纸，走路像顺移 | 完整人物多帧 + 规范化六帧步态 |
| 床、桌、灯、人物互相悬浮 | 先画空间平面；接触脆弱时整场景生成 |
| 角色每个镜头长得不一样 | 身份参考图 + 比例/脚底线/服装锁定 |
| 揭榜、扶起、拦驾、拉被看不懂 | `cause → action → propagation → result → proof` |
| 历史宫殿像影视城或破旧木屋 | 史料采用清单 + 后世元素排除清单 |
| 旁白说了，画面没做 | 每个动词必须有静音可读的证明帧 |
| 皇帝声音像普通人、甚至带方言 | 试听同时检查口音、身份、咬字和情绪 |
| 字幕遮住手、脚、灯和接触点 | 默认底部水平居中，按实际渲染帧检查安全区 |
| Studio 预览和成片不一致 | 最终以渲染 MP4 抽帧和 FFprobe 为证据 |

## 最重要的顺序

```text
空间成立
  → 资产适配
  → 动作可读
  → 声音归属
  → 字幕安全
  → 视觉装饰
  → 渲染交付
```

不要反过来。灯光、纸纹、粒子和漂亮转场不能修复错误的朝向、悬空的桌子或不属于角色的台词。

## 八道制作门

1. **故事门**：写出事件链和 proof，不让旁白独自承担动作。
2. **历史门**：确定时代、功能空间、采用依据与明确排除项。
3. **空间门**：先俯视平面，再正视机位，再生成背景。
4. **资产门**：决定整场景、完整人物、ensemble 或独立道具，不为了复用而复用。
5. **基准门**：先完成最难的 8–15 秒，证明接触、比例、方向和因果。
6. **声音门**：角色试音、标准普通话/口音筛选、实测时长、混音窗口。
7. **审片门**：静音看、只听声音、画音合看；字幕和 proof frame 单独检查。
8. **交付门**：HyperFrames、MP4 抽帧、音视频探测、master/social 双版本。

## 快速开始

### 0. 安装 / 复制 skill

#### 方式 A：Codex 全局安装

将整个 `paper-animation-director/` 文件夹复制到 Codex 的 skills 目录，保持以下结构：

```text
<codex-skills>/paper-animation-director/
├── SKILL.md
├── README.md
├── references/
├── scripts/
└── assets/
```

在 Codex 中直接调用：

```text
Use $paper-animation-director to turn this script into a historically grounded,
spatially credible, multi-layer paper-cut animation. Start with the story contract,
spatial plan, and hardest benchmark scene before generating the full film.
```

#### 方式 B：Cursor 项目内接入

将本目录复制到项目中，例如：

```text
your-video-project/
├── .cursor/
│   └── rules/
│       └── paper-animation-director.md
└── tools/
    └── paper-animation-director/
        ├── SKILL.md
        ├── references/
        └── scripts/
```

在 `.cursor/rules/paper-animation-director.md` 中写明：

```md
当任务涉及纸片动画、皮影动画、连续角色或历史/非遗场景时，
先阅读 tools/paper-animation-director/SKILL.md，
再按制作阶段阅读其 references/ 文件。不得跳过空间平面、完整姿势、静音 proof 和渲染抽帧审查。
```

在 Cursor Agent/Composer 中可以这样开始：

```text
@paper-animation-director
请把这段剧本转换为横版纸片动画方案，先输出空间圣经、资产决策表和最难镜头基准，不要立即批量生成素材。
```

#### 方式 C：Cloud Code / Claude Code 类工具

如果工具支持项目级 skills，将目录放在：

```text
your-project/.claude/skills/paper-animation-director/
```

至少保留 `SKILL.md`、`references/` 和 `scripts/`。在项目 instructions 中加入：

```md
纸片动画任务必须先读取 .claude/skills/paper-animation-director/SKILL.md。
历史、非遗、重复角色或复杂空间任务还必须读取 references/production-retrospective.md。
```

然后用自然语言调用：

```text
Read .claude/skills/paper-animation-director/SKILL.md and use it for this project.
先做故事事件链、历史采用/排除清单、俯视空间平面和 8–15 秒 benchmark，再进入素材生成。
```

#### 方式 D：任何支持 Markdown 规则的工具

不需要特殊插件。把 `SKILL.md` 当作主规则文件，把 reference 按需加载：

```text
1. 读取 SKILL.md
2. 读取 production-retrospective.md
3. 读取当前阶段需要的 reference
4. 执行 scripts/ 中的审计命令
5. 在渲染 MP4 抽帧后再交付
```

### 运行环境要求

| 能力 | 用途 | 必需性 |
| --- | --- | --- |
| Python 3 | 故事清单、素材、节奏与声音审计脚本 | 必需 |
| Node.js / npm | HyperFrames 工程与渲染命令 | 使用 HyperFrames 时必需 |
| FFmpeg / FFprobe | 音视频探测、社会化版本与成片核验 | 交付时必需 |
| 图像生成/编辑工具 | 背景、完整角色、姿势图集、整场景帧 | 生成新素材时必需 |
| TTS 服务 | 旁白和角色对白 | 有配音时必需 |
| 浏览器/Studio | 预览与交互检查 | 开发阶段推荐 |

API key 只放在宿主工具的环境变量或外部 `.env`，不要写入 skill、项目 manifest、README、prompt 或音频候选记录。

### 1. 读路由与复盘规程

主规则在 [`SKILL.md`](SKILL.md)，项目复盘和失败模式在 [`references/production-retrospective.md`](references/production-retrospective.md)。历史、非遗、空间复杂或角色重复的项目，两者都要读。

### 2. 建立故事清单

```bash
python3 scripts/validate_story_manifest.py story-manifest.json --strict
```

每场至少写：

- `narrative_goal`
- `duration_policy`
- `events[].cause`
- `events[].action`
- `events[].propagation`
- `events[].result`
- `events[].proof`
- `activity_windows`

### 3. 生成前先做资产和空间审查

```bash
python3 scripts/audit_asset_integrity.py assets/generated --kind character --strict
python3 scripts/probe_voice_timing.py assets/audio/*.mp3 --output voice-manifest.json
```

图片生成前请准备：身份参考图、俯视平面、正视机位、历史采用/排除表和素材架构表。不要先批量生成，再试图用 CSS 把错误素材摆正确。

### 4. 先做基准镜头

基准镜头应包含项目最难的动作：共同负重、扶起、拦驾、拉被、灯—幕—影光学关系、火/水传播或完整工艺步骤。通过静音语义、接触关系和角色一致性后，再扩展全片。

### 5. 进入 HyperFrames

```bash
python3 scripts/init_paper_project.py --manifest story-manifest.json --output ./my-paper-story
python3 scripts/build_hyperframes_timeline.py --manifest story-manifest.json --project ./my-paper-story
npm run check
```

每个场景使用一个暂停的、已注册的 timeline；所有音频直接挂在根组合；关键动作写入 `*.motion.json`，不能只让装饰粒子“动起来”。

## 资产架构：什么时候整合，什么时候分层？

### 默认整合

- 床 + 李夫人 + 锦被 + 帐架；
- 灯体 + 油盘 + 灯芯 + 火焰；
- 扶起、拦驾、抬物、拥抱、共同负重；
- 需要同时证明空间接触和人物状态的关键帧。

### 允许独立

- 需要走动、转向、反应的完整人物；
- 需要独立传播的帐纱、烟、火光、纸纹；
- 灯、幕、影人之间的光学关系；
- 不承载人物语义、只承担物理效果的道具。

“独立”指独立的完整 PNG，不指把头、身体、手、腿拆成零件。人体零件拼接不是纸片动画的默认方案。

## 角色一致性最低标准

每个重复角色必须有一张身份参考卡，记录：

- 脸型、年龄、眉眼和发式；
- 帽冠、服装轮廓、腰带、鞋和主色；
- 站立高度、跪坐高度、脚底基线和画布中心；
- 纸边颜色、光向和禁用变化。

走路至少使用六帧：

```text
承重 → 抬脚 → 落脚 → 过渡 → 换脚 → 收势
```

所有帧的画布、脚底线和人物中心必须一致。父轨道负责世界坐标移动，子帧负责重心变化；只做 `x` 平移不算走路。

## 历史题材的空间准则

以汉代宫廷为例，庄重感应来自：

- 高台、夯土基座、柱网、开间和台阶；
- 维护良好的髹漆木构和墙面；
- 低榻、席地、低案、帷帐和真实落点；
- 大尺度、密缝、哑光的方砖/条砖，而不是现代抛光瓷砖；
- 厅堂、殿庭和临时棚架，而不是后世成熟固定戏台。

每个历史选择都要同时写：

```text
采用：证据支持的结构/材质/活动
排除：不属于时代或会破坏空间的元素
```

## 声音和字幕的三条底线

1. 每句台词必须有唯一 `speaker`；旁白不能代替角色念第一人称句。
2. 试听必须检查口音。`深沉/权威/电影感`不等于标准普通话。
3. 中文字幕默认底部水平居中，不能盖住手、脚、灯、帘口、影子边缘和接触点。

声音审核要单独做一次“只听声音”：确认没有抢词、重叠、错角色、方言和不合情绪的语速。画面对不上时，先扩展动作或场景时间，不要强行压缩人物情感。

## 三次审片

### 静音看

能否看出谁在什么位置，为什么开始动，碰到了什么，结果改变了什么？

### 只听声音

每句是谁说的？音色、口音、语气是否符合人物？有没有旁白和对白重叠？

### 画音合看

字幕是否在说话时出现？动作是否先于/同步于台词？转场是否说明时间、地点或情绪改变？

## 目录导航

```text
paper-animation-director/
├── SKILL.md                         # 给模型执行的主规程
├── README.md                        # 人类快速阅读的导演手册
├── references/
│   ├── production-retrospective.md  # 全面复盘、失败模式与镜头卡模板
│   ├── story-and-beat-design.md     # 故事与事件链
│   ├── character-and-pose-system.md # 身份、姿势、步态、ensemble
│   ├── image-generation-prompts.md  # 背景/角色/道具 prompt 合同
│   ├── layers-physics-and-occlusion.md
│   ├── semantic-action-checks.md
│   ├── voice-timing-and-subtitles.md
│   ├── hyperframes-production.md
│   └── quality-gates-and-delivery.md
├── scripts/                         # 初始化、审计、时间轴与交付工具
└── assets/project-template/         # 最小 HyperFrames 工程模板
```

## 适用与不适用

适用：连续故事、重复角色、纸影/剪纸、历史与非遗、可验证动作、旁白驱动的 HyperFrames 项目。

不适用：主要由海报式信息卡组成的编辑型解释视频；这类项目应考虑 `vox-director` 或 `faceless-explainer`。

## 版本记录

### v2.2 · 头脸完整性与遮挡审核 · 2026-07-29

- 将头部、脸部、手、脚和关键接触点加入每镜保护区域；
- 拦截画框、容器、overflow、蒙版、alpha 裁切、前景、字幕、转场或水印造成的半脸/断头效果；
- 区分自然侧脸、具有物理依据的计划遮挡与无来源的错误截断；
- 要求计划遮挡声明遮挡物、深度、时间窗、原因和无遮挡身份确认帧；
- 审片联系表自动加入遮挡进入、最大覆盖、退出和身份确认时刻。

### v2.1 · 角色参考与镜头空间合同 · 2026-07-29

- 将角色前置资产收敛为每个重复角色一张正面中性身份参考图，并明确禁止直接用于动画；
- 删除全局预生成姿势库，改为镜头空间合同通过后按镜头即时设计和生成；
- 加入归一化坐标、运动走廊、障碍、方向、朝向、动作目标、可达性和连续性合同；
- 将方向相反、通路不足、目标语义错误设为硬失败，禁止因素材已生成而强行复用；
- 更新 manifest 和验证器，使身份、空间与镜头资产门禁可自动检查。

### v2.0 · 制作复盘升级 · 2026-07-26

- 加入空间圣经和历史采用/排除双清单；
- 加入整场景多帧、灯火一体、ensemble 优先的资产决策；
- 加入六帧规范化步态和侧面视角规则；
- 加入标准普通话/口音排除、speaker 归属和字幕居中安全区；
- 加入静音/只听/画音三次审片；
- 加入预览缓存、渲染抽帧和交付证据规则；
- 加入本项目中的失败模式速查表与可复用镜头卡模板。

### v1.0 · 基础规程

建立完整角色、ensemble 动作、事件 proof、HyperFrames 时间轴和 P0–P3 交付门。

## 作为开源项目使用

### 项目级 vendoring

如果一个视频项目需要长期复用这套规则，建议把 skill 复制进项目的 `tools/`、`.cursor/` 或 `.claude/skills/`，并在项目自己的 `AGENTS.md`、`CLAUDE.md` 或 rules 文件中声明加载顺序。这样项目可以锁定一版稳定规程，不会因为全局 skill 更新而突然改变已审批的制作标准。

### 更新策略

- 只读 `SKILL.md` 不足以完成复杂项目；按阶段加载对应的 `references/`；
- 新的失败模式优先写进 `production-retrospective.md`，确认可迁移后再提升到 `SKILL.md` 的硬规则；
- 工具特定命令放在适配层或项目文档，不要把 Codex、Cursor、Claude Code 的私有 API 写进核心规则；
- 修改脚本后，用一个最小 manifest 和一个短 benchmark 做回归，不要只检查 Markdown 能否打开；
- 修改 README、SKILL 或 references 后，检查相对链接、示例路径和命令是否仍然成立。

### 贡献一个新经验

提交新规则时请说明：

```text
症状：观众/审片者看到了什么问题？
根因：是空间、素材、动作、声音、字幕还是工具链问题？
修正：采取了什么可复现的做法？
验证：通过哪一帧、哪条命令或哪种审片确认？
迁移：这条经验适用于哪些其他故事？
```

不要只提交“这一帧更好看”的主观结论，要提交能被另一个项目复用的判断标准。

## 安全与隐私

- 不要在仓库中提交 API key、访问令牌、`.env`、私有音频链接或未授权素材；
- 生成脚本只记录公开 voice/reference ID、参数和文件路径，不记录秘密；
- 历史图片、角色参考和音乐/音效应记录来源与使用边界；
- 需要公开仓库时，清理项目中的临时截图、缓存、预览 URL 和本地绝对路径；
- 最终交付中的动态水印不能替代版权、授权和素材来源记录。

## 许可证

本目录目前未附带正式开源许可证。若要发布到公共仓库，请由项目维护者补充 `LICENSE`，并明确：skill 文档、脚本、模板资产、示例 prompt 和用户生成素材各自的使用边界。在许可证确定前，不要把“公开可见”理解成“可以任意商用”。

## 最后一句

**先证明，再装饰；先适配，再复用；先完整，再拆层。**

纸片动画的神奇感，不是因为观众没看出问题，而是因为观众看懂了物理关系，却仍然觉得它像真的活了起来。
