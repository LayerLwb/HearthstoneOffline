# 第三方素材与依赖归属声明（NOTICE）

**适用项目：《炉石离线旅店》（hearthstone-offline）**
**版本：1.0 | 更新日期：2026-10-10**

> 本文件是 `LICENSE` 第 3 节「排除范围」的展开清单，与 `LICENSE`、`DISCLAIMER.md`
> 构成一个整体。分发本项目时**必须原样保留本文件**，不得删除或改写归属信息。
> 逐文件的来源地址、字节长度与 SHA-256 校验值见 `public/data/art-manifest.json`。

---

## 1. 概览

本项目仅在**代码与自研界面层面**为原创。运行所需的卡牌资料、插画与部分参考资料
均来自第三方，权利归各自权利人所有。本项目：

- 对这些内容**不主张任何权利**，也**不授予**任何人任何权利；
- 仅按**原样引用**的方式用于本地、离线、非商业的学习与研究；
- 保留原始来源标注，不以任何方式暗示获得授权或背书。

---

## 2. 权利归属清单

### 2.1 暴雪娱乐（Blizzard Entertainment, Inc.）

| 内容 | 说明 |
| --- | --- |
| 名称与商标 | 「Hearthstone」「炉石传说」及标识、职业名、角色名、卡牌名 |
| 卡牌文本与数值 | 卡牌描述文本、攻击力、生命值、法力消耗与全部规则数值 |
| 原版卡牌插画 | 本项目使用的全部原版卡牌插画 |
| 原版美术与音频 | 本项目**未使用**原版音乐、语音或抽取的游戏音频 |

本项目与暴雪娱乐无任何隶属、赞助或背书关系。详见 `DISCLAIMER.md` 第 1 节。

### 2.2 HearthSim / hearthstonejson（卡牌数据整理）

| 内容 | 来源 |
| --- | --- |
| 固定中文快照 | `https://api.hearthstonejson.com/v1/251951/zhCN/cards.json` |
| 版本资料 | `https://github.com/HearthSim/hsdata` |
| 插画接口说明 | `https://hearthstonejson.com/docs/images.html` |
| 插画地址形式 | `https://art.hearthstonejson.com/v1/512x/{cardId}.webp` |

数据整理工作归 HearthSim 项目；**原始内容权利仍归暴雪娱乐**。

### 2.3 同人扩展包素材

| 内容 | 说明 |
| --- | --- |
| 处理方式 | 74 个实体对应的离线 WebP，记录来源、大小与 SHA-256 |
| 具体来源 | 农场立绘自截图内部裁剪；幼龙使用 Dragon（`phx_2_117`） |
| 权利归属 | 原立绘权利归各自原权利人所有，本项目不主张权利 |

### 2.4 参考资料（仅作方法参考，未直接复制素材）

| 内容 | 来源 |
| --- | --- |
| 纳克萨玛斯首领牌组 | Icy Veins — Curse of Naxxramas 各首领指南，`https://www.icy-veins.com/hearthstone/anub-rekhan-guide-for-the-curse-of-naxxramas` |
| 达拉然大劫案关卡结构 | Hearthstone Wiki（`https://hearthstone.wiki.gg/wiki/The_Dalaran_Heist`）及其英雄、首领、宝藏、畸变、鲍勃酒馆页面 |

仅采用其中的首领牌组与关卡结构信息，**未复制其页面图文素材**。
开发期缓存与逐页来源记录保存在 `artifacts/` 目录中。

---

## 3. 主要软件依赖

准确版本由 `package.json` 与 `package-lock.json` 固定。
发布目录中保留 Electron 随附的许可文件与 Chromium 第三方声明。

| 组件 | 用途 | 上游许可 |
| --- | --- | --- |
| Electron / Chromium | Windows 桌面运行时 | MIT / 多种第三方许可 |
| React / React DOM | 菜单、收藏与组牌 | MIT |
| TypeScript | 类型检查 | Apache-2.0 |
| Vite | 构建与开发服务器 | MIT |
| PixiJS | 棋盘与效果渲染 | MIT |
| Phosphor Icons | 界面图标 | MIT |
| Vitest | 规则、成长、回放与存档测试 | MIT |
| Playwright | 界面与实际 Electron 验收 | Apache-2.0 |
| electron-builder | Windows 安装包与 ZIP | MIT |

> 完整依赖清单（含传递依赖）以 `package-lock.json` 为准；
> 若新增依赖，请在此表与 `docs/素材与依赖说明.md` 中同步登记。

---

## 4. 本项目自有的原创内容

以下内容由本项目作者原创，受同目录 `LICENSE` 保护：

- TypeScript / JavaScript / CSS / HTML 源码：规则引擎、卡牌效果登记、电脑决策、
  动画调度、存档与回放、创意工坊校验等全部逻辑；
- 构建、验证、覆盖率与打包脚本；
- 项目文档；
- 由 CSS / SVG / Canvas / PixiJS 绘制的木质棋盘、边框、卡框、法力水晶、卡背、
  导航与动画，以及由 Web Audio **实时合成**的交互与战斗提示音
  （本项目不包含原版语音、音乐或抽取的游戏音频）；
- 界面使用实时数据重新绘制卡框、中文文本与数值，**不将旧版整张卡图作为牌面**。

---

## 5. 侵权反馈

若你是上述任一内容的权利人，认为本项目的使用方式侵犯了你的权利，
请按 `DISCLAIMER.md` 第 9 节的流程通知我们，我们承诺在 **72 小时内**处理。

---

# Third-Party Notices (English)

Hearthstone Offline Inn includes only original code, scripts, documentation and
self-made UI/audio assets. All card names, card text, card values, card data and
original card art used at runtime are the property of **Blizzard Entertainment, Inc.**
Card data snapshots are sourced from **HearthSim / hearthstonejson**
(`https://api.hearthstonejson.com`, `https://github.com/HearthSim/hsdata`).
their respective owners. Advisory reference material was consulted from
**Icy Veins** and **Hearthstone Wiki (hearthstone.wiki.gg)**; no page content was copied.

This project claims no rights over any third-party content and grants none.
It is an unofficial, non-commercial fan project with no affiliation to, sponsorship
by, or endorsement from Blizzard Entertainment. Bundled dependencies (Electron,
Chromium, React, TypeScript, Vite, PixiJS, Phosphor Icons, Vitest, Playwright,
electron-builder) remain under their respective upstream licenses as pinned in
`package-lock.json`.

If you are a rights holder and believe this project infringes your rights, please
see the notice-and-takedown procedure in `DISCLAIMER.md`. We commit to acting within
72 hours of a valid notice.