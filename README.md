# 炉石传说单机版 (Hearthstone Offline Inn)

[![Release](https://img.shields.io/badge/Release-v1.5.7-gold.svg)](https://github.com/LayerLwb/HearthstoneOffline/releases)
[![Platform](https://img.shields.io/badge/Platform-Web%20%7C%20Android-brightgreen.svg)]()
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20TypeScript-blue.svg)]()
[![License](https://img.shields.io/badge/License-MIT%20%2F%20Fan%20Project-orange.svg)]()

《炉石传说单机版》（Hearthstone Offline Inn）是一款基于 Web 与 Android 混合架构实现的完全离线单机版《炉石传说》游戏。游戏完整收录了数千张经典与扩展包卡牌数据，支持标准与狂野对战、AI 对弈、卡组自由构筑、开包模拟、酒馆战棋等核心玩法。

---

## 🌟 核心特色

- **纯正离线体验**：无需联网，不依赖任何外部游戏服务器，随时随地开启旅店对决。
- **全量卡牌数据**：基于 HearthSim / hearthstonejson 数据集，收录数万张卡牌元数据、关键词与衍生卡。
- **智能 AI 对战**：基于独立 Web Worker 运行的启发式 Minimax 极大极小博弈搜索树，告别掉帧与卡顿。
- **跨平台支持**：
  - **Web 端**：直接使用任意现代浏览器运行，支持 Chrome、Edge、Firefox、Safari。
  - **Android 端**：原生全屏硬件加速 WebView 包装，完美适配全面屏与刘海屏。
- **全新「卡牌缺陷反馈 (Bug Report)」系统**：
  - 在卡牌详情中新增「🐞 报告Bug」入口。
  - 强制必填问题描述校验。
  - 自动提取当前卡牌的所有关键属性（名称、编号、费用、身材、效果），一键生成标准化 GitHub Issue 并自动跳转提交。

---

## 📁 目录结构

```text
HearthstoneOffline/
├── android/                         # Android 原生包装层
│   ├── app/                         # App 模块
│   │   ├── src/main/AndroidManifest.xml
│   │   ├── src/main/java/com/hearthstone/offline/MainActivity.java # 核心容器
│   │   └── src/main/res/            # 应用程序图标与资源
│   ├── build.gradle                 # 构建脚本
│   └── settings.gradle
├── web/                             # Web 游戏核心
│   ├── index.html                   # 网页主入口 (已配置 CSP 与全屏元标签)
│   ├── assets/
│   │   ├── index.js                 # 游戏主程序 (含 React UI、对战状态机与卡牌详情)
│   │   ├── ai.worker.js             # 独立 Web Worker AI 决策计算器
│   │   ├── mobile-layout.js         # 移动端视口与手牌防误触适配
│   │   ├── index.css                # 炉石酒馆风格主样式表
│   │   └── mobile-layout.css        # 移动端弹性布局样式
│   ├── data/                        # 卡牌数据库与规则集
│   │   ├── cards.zhCN.json          # 全量中文卡牌数据
│   │   ├── catalog.collectible.json # 可收集卡牌清单
│   │   ├── catalog.tokens.json      # 衍生卡牌清单
│   │   ├── ruleset.json             # 核心机制与关键词规则
│   │   └── art-manifest.json        # 原画哈希清单
│   └── scripts/
│       └── download_art.py          # 原画多线程下载与提取脚本
├── tools/                           # 逆向与数据分析工具
│   ├── inspect_hand.py              # 手牌布局分析
│   └── scratch_whizbang_analysis.txt# 威兹班套牌逆向笔记
├── docs/                            # 项目设计与架构文档
│   ├── ARCHITECTURE.md              # 架构深度剖析
│   ├── CODE_INVENTORY.md            # 代码与资产全景盘点
│   └── BUG_REPORT_SYSTEM.md         # Bug 报告系统详细说明
├── build_release_apk.py             # 自动化构建与签名 Release APK 脚本
├── LICENSE                          # 开源协议
├── NOTICE.md                        # 第三方组件与资源声明
├── DISCLAIMER.md                    # 免责声明与非商业用途说明
└── README.md                        # 本说明文件
```

---

## 🚀 快速开始

### 方式 1：Web 端直接运行（无需安装）
你可以使用任何静态网页服务器托管 `web` 目录：

```bash
# 使用 Python 启动本地服务器
cd web
python -m http.server 8080
```
启动后在浏览器中打开 `http://localhost:8080` 即可开始游戏。

### 方式 2：Android 端安装
前往 [GitHub Releases](https://github.com/LayerLwb/HearthstoneOffline/releases) 下载最新签名的 `HearthstoneOffline-v1.5.7.apk` 直接安装到手机或 Android 模拟器即可。

---

## 🐞 卡牌 Bug 报告流程

1. 进入游戏主界面，点击 **「我的收藏 (Collection)」**。
2. 找到有疑问或机制异常的卡牌，点击打开 **「卡牌详情」** 弹窗。
3. 点击下方的 **「🐞 报告Bug」** 红色按钮。
4. 在弹出的反馈框中输入 **详细的 Bug 描述**（必填，未填会提示阻止提交）。
5. 点击 **「提交」**，系统将自动汇总卡牌名称、卡牌 ID、身材、效果描述并调起 GitHub Issue 创建页面完成提交。

---

## ⚖️ 知识产权与免责声明

1. 本项目为非商业性质的开源技术研究与同人学习项目。
2. 《炉石传说》（Hearthstone）、魔兽世界观背景、卡牌名称、卡牌原画插图及音效的著作权与商标权完全归属于 **暴雪娱乐（Blizzard Entertainment, Inc.）**。
3. 卡牌结构化数据库快照来自开源社区 **HearthSim / hearthstonejson**。
4. 详细声明请参阅 [DISCLAIMER.md](docs/DISCLAIMER.md) 与 [NOTICE.md](docs/NOTICE.md)。
