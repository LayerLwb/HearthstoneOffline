# 免责声明与权利归属告知

**适用项目：《炉石离线旅店》（HearthstoneOffline / hearthstone-offline）**
**版本：1.0 | 生效日期：2026-10-10**

> 本文件与同目录 `LICENSE`、`NOTICE.md` 构成一个整体，应一并阅读与分发。
> 在程序内对应「首次启动协议页」；修改本文件正文时，应同时递增
> `src/game/license.ts` 中的 `LICENSE_VERSION`，玩家会被重新要求确认。

---

## 一句话版本

《炉石离线旅店》是一个**非官方、非商业、完全离线**的《炉石传说》同人学习项目，
与暴雪娱乐没有任何关系；所有卡牌名称、卡牌数据、插画与商标权利均归暴雪娱乐及各自权利人所有，
本项目不向其主张任何权利，也不用于任何营利目的。

---

## 1. 非官方声明（No Affiliation）

1.1 《炉石离线旅店》是由爱好者独立开发的**同人作品**，不是官方产品，
    不是官方版本的移植、复刻或替代品。

1.2 本项目与暴雪娱乐（Blizzard Entertainment, Inc.）及其关联公司之间
    **不存在任何隶属、代理、合作、赞助、认可或背书关系**。

1.3 本项目**未获得、也未主张**暴雪娱乐或任何第三方的授权、许可、批准或支持。

1.4 本项目名称、界面与文档中出现的「炉石」「炉石传说」「Hearthstone」等表述，
    仅为说明内容来源与适用范围而作的**指示性使用**，不构成商标性使用，
    也不表示任何形式的关联。

1.5 使用者不得以任何方式暗示本项目由暴雪娱乐发布、授权或认可，
    不得使用官方标识，不得使用「正版」「官方版」「国服版」「重制版」等易致混淆的表述。

---

## 2. 权利归属（Ownership）

2.1 **属于第三方的内容**（本项目不享有权利、不授予任何权利）：

| 内容 | 权利人 |
| --- | --- |
| 「Hearthstone / 炉石传说」名称、标识、商标、职业与角色名称 | 暴雪娱乐（Blizzard Entertainment） |
| 卡牌名称、卡牌文本、卡牌数值 | 暴雪娱乐 |
| 结构化卡牌数据快照（`cards.zhCN.json`、`catalog.*.json` 等） | 原始内容归暴雪娱乐；数据整理归 HearthSim / hearthstonejson |
| 原版卡牌插画及任何原版美术、音频素材 | 暴雪娱乐 |
| 同人扩展包中引用的第三方卡牌截图与立绘（如 Eternal 素材） | 各自原权利人 |
| 冒险复刻所参考的第三方攻略与 Wiki 内容 | Icy Veins、hearthstone.wiki.gg 及原文作者 |
| 第三方开源依赖（Electron、React、PixiJS 等） | 各上游项目，适用其自身许可 |

2.2 **属于本项目作者的内容**（受 `LICENSE` 保护）：
    规则引擎、电脑决策、动画调度、存档与回放、创意工坊校验等全部自研代码，
    构建与测试脚本，项目文档，以及由 CSS / SVG / Canvas / PixiJS 绘制、
    由 Web Audio 实时合成的界面与音效素材。

2.3 逐项的素材来源地址、文件长度与 SHA-256 校验值记录在
    `public/data/art-manifest.json` 与 `docs/素材与依赖说明.md` 中，供核查。

---

## 3. 本项目不主张权利（No Claim）

3.1 本项目**不对任何第三方内容主张著作权、商标权或其他权利**，
    也不以本项目之名向任何第三方主张这些权利。

3.2 本项目在源码仓库与发行包中保留原始权利人的名称与来源说明，
    目的是**如实标注来源**，而非主张许可。

3.3 本项目不对因使用者自行替换、增补第三方素材而产生的后果负责。

---

## 4. 非商业用途与开发目的

4.1 本项目的开发目的是**学习与研究**：练习游戏规则引擎、
    状态同步、确定性回放、界面渲染与本地存档的实现方式。

4.2 本项目**完全离线**，不连接暴雪或任何第三方的服务器，
    不含联网对战、账号系统、内购、付费抽卡或任何形式的付费机制。

4.3 本项目**严禁任何形式的商业使用**，包括出售、付费分发、付费解锁、
    广告或打赏变现、预装在收费设备或收费场所、作为赠品引流等，
    详见 `LICENSE` 第 5.2 节。

4.4 本项目中的卡牌数据与图片用于**个人离线学习与本地展示**，
    不作为任何商业产品或服务的组成部分。

---

## 5. 担保排除与责任限制

5.1 本项目按**「现状」与「现有」**提供，不附带任何明示或默示的担保，
    包括但不限于可商用性、特定用途适用性、权利无瑕疵与不侵权的担保。

5.2 作者**不保证**本项目在任何设备、操作系统或版本上都能正常运行，
    不保证不存在程序缺陷，也不保证存档不会丢失、损坏或无法恢复。

5.3 在适用法律允许的最大范围内，作者**不对**因使用或无法使用本项目而产生的
    任何直接、间接、附带、特殊、惩罚性或后果性损害承担责任，
    包括但不限于设备损坏、数据丢失、存档损坏、利润损失、
    第三方索赔以及由此产生的法律费用。

5.4 存档保存在本机。卸载、覆盖安装或删除程序目录前，请自行导出备份。
    作者不对存档丢失负责。

5.5 本条不限制或排除依法不得限制或排除的责任。

---

## 6. 使用者的义务

使用、复制、修改或分发本项目，即视为你已阅读并同意：

6.1 **自行确认合法性**：请自行确认在所在国家或地区使用本项目
    符合当地法律法规，并自行承担相应后果。

6.2 **保持非商业**：不得收费、不得变现、不得移除本声明与来源标注。

6.3 **如实标注**：分发修改版时必须标注为「非官方同人作品」，
    并说明修改性质与修改者身份。

6.4 **扩展包自负责任**：你制作或分发的创意工坊扩展包，
    其内容合法性由你自行负责；不得夹带脚本、可执行文件、动态库
    或任何试图突破本程序沙箱的内容。

6.5 **配合下架**：收到权利人通知后应立即停止分发并删除相关内容。

---

## 7. 离线运行与隐私

7.1 本项目运行时**不发起任何网络请求**，不上传存档、日志或设备信息。

7.2 本项目**不收集**任何个人信息，不包含统计、埋点、遥测或广告 SDK。

7.3 错误日志、存档与设置文件仅保存在本机，
    由你自行决定是否导出与分享；一旦导出并分享，其后果由你自行承担。

7.4 本项目不提供、也不应被用于任何形式的在线服务或用户账号体系。

---

## 8. 内容适宜性

8.1 本项目为策略卡牌游戏，不含赌博机制、不含真实货币消费、
    不含色情或暴力内容，适合一般玩家。

8.2 未成年人使用本项目应在其监护人知情与同意下进行。

---

## 9. 权利通知与下架流程（重要）

本项目无意侵犯任何人的合法权利。**若你是权利人（或其授权代理人），
认为本项目侵犯了你的权利，请按下述方式通知我们，我们会优先处理：**

请在通知中提供：

1. 你的身份信息与权利证明（著作权登记、商标注册或授权文件等）；
2. 涉嫌侵权内容在本项目中的具体位置（文件路径、界面名称、截图或链接）；
3. 你的联系方式；
4. 一份声明，说明你善意地认为该使用未获授权；
5. 一份声明，说明通知内容真实准确，并愿意承担相应法律责任。

**我们的承诺：**

- 收到符合上述要求的通知后，我们将在 **72 小时内**下架或删除相关内容，
  并停止分发包含该内容的版本；
- 我们**不会**就非商业、非营利的同人学习项目主张任何对抗性权利；
- 我们不会要求任何补偿，也不会对善意通知者采取任何不利措施。

**联系方式：**

- 邮箱：`【待填写：你的联系邮箱】`
- 仓库 Issue / 私信：`【待填写：仓库地址】`

> 注：在收到有效通知前，本项目按现状提供；收到通知后，本项目将按要求调整内容，
> 并在版本说明中记录该调整。

---

## 10. 版本记录

| 版本 | 日期 | 变更 |
| --- | --- | --- |
| 1.0 | 2026-10-10 | 首版。在程序内「开源协议与责任告知」基础上，拆分为 `LICENSE` + 本文件 + `NOTICE.md` 三份文件。 |

---

---

# Disclaimer & Ownership Notice (English Version)

*The Chinese text above is the authoritative version and prevails in case of any conflict.*

**Project: Hearthstone Offline Inn (hearthstone-offline) — Version 1.0, effective 2026-10-10**

## 1. No Affiliation

Hearthstone Offline Inn is an **unofficial, non-commercial, fully offline fan project**
created by hobbyist developers for study and research purposes. It is **not** an official
product, and it is **not** affiliated with, authorized by, sponsored by, approved by, or
endorsed by Blizzard Entertainment, Inc. or any of its affiliates. No authorization,
license or approval has been obtained from, or is claimed against, Blizzard Entertainment
or any other third party. References to "Hearthstone" are purely nominative, used only to
describe the subject matter of this project.

## 2. Ownership

All Hearthstone names, logos, trademarks, class and character names, card names, card text
and card values are the property of **Blizzard Entertainment**. Card data snapshots are
sourced from **HearthSim / hearthstonejson**; the underlying content rights remain with
Blizzard Entertainment. **All original card art and any original game art or audio are the
property of Blizzard Entertainment.** Third-party assets referenced by community expansion
packs (e.g. Eternal card images) remain the property of their respective owners.

This project claims **no rights whatsoever** over any of the above, and grants **no rights**
over them. Per-asset source URLs, file sizes and SHA-256 checksums are recorded in
`public/data/art-manifest.json` and `docs/素材与依赖说明.md`.

## 3. Non-Commercial Use Only

This project is provided strictly for **learning, research and personal use**. It is
entirely offline, connects to no server, contains no online multiplayer, no accounts, no
in-app purchases and no paid card packs. **Any commercial use is strictly prohibited**,
including selling, paid distribution, paywalled access, monetization through advertising or
donations, pre-installation on paid devices or in paid venues, and use as a promotional
giveaway. See Section 5.2 of the `LICENSE` file.

## 4. Disclaimer of Warranty and Limitation of Liability

THIS PROJECT IS PROVIDED "AS IS" AND "AS AVAILABLE", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. THE AUTHORS DO NOT WARRANT
THAT THE PROJECT WILL RUN ON ANY PARTICULAR DEVICE OR SYSTEM, OR THAT SAVED DATA WILL NOT
BE LOST OR CORRUPTED. TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, THE AUTHORS SHALL
NOT BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, PUNITIVE OR CONSEQUENTIAL
DAMAGES, INCLUDING DEVICE DAMAGE, DATA LOSS, LOST PROFITS, THIRD-PARTY CLAIMS OR LEGAL
FEES, ARISING FROM THE USE OF OR INABILITY TO USE THIS PROJECT, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGES.

## 5. Privacy

This project makes **no network requests** during operation, uploads no saves, logs or
device information, and contains **no telemetry, analytics or advertising SDKs**. All
saved data remains on your local machine.

## 6. Notice and Takedown

This project has no intention of infringing anyone's rights. **If you are a rights holder
and believe this project infringes your rights, please contact us** with (1) your identity
and proof of rights, (2) the specific location of the allegedly infringing content within
this project, (3) your contact details, and (4)(5) the statements required under applicable
takedown procedures. **We commit to removing or disabling the relevant content within 72
hours** of receiving a valid notice, and to ceasing distribution of any version containing
it. We assert no adversarial rights against non-commercial, non-profit fan study projects.

Contact: `【email address】` / `【repository URL】`

## 7. Governing Law

This notice and the accompanying `LICENSE` are governed by the laws of the
People's Republic of China.
