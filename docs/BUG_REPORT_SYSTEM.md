# 卡牌缺陷报告与 Issue 自动化系统说明

本项目在卡牌详情模块中深度集成了缺陷反馈系统，方便玩家、开发者与社区成员在测试单机版卡牌机制时，能够一键定位异常卡牌并将精确的卡牌上下文与问题描述反馈至 GitHub 仓库。

---

## 1. 功能特性

1. **零学习成本**：玩家在“我的收藏”浏览任意卡牌（含随从、法术、英雄、衍生牌）时，详情界面均提供「🐞 报告Bug」按钮。
2. **自动化元数据提取**：
   - 卡牌官方名称
   - 卡牌数据库唯一 ID（如 `CS2_029`, `BOT_914`）
   - 职业归属、法力值消耗、稀有品质、扩展包系列
   - 当前卡牌效果描述文本与自定义规则说明
3. **强制性必填校验**：
   - 必须输入具体的 Bug 描述，杜绝空白误触或无意义提交。
   - 输入框具有动态错误反馈与红色边框高亮警告。
4. **即时协同与一键跳转**：
   - 自动生成标准化 GitHub Issue 模版。
   - 自动复制到剪贴板，并一键调起浏览器直达 GitHub New Issue 提交页。

---

## 2. 界面效果与代码实现

### 2.1 触发按钮与状态
在 `web/assets/index.js` 中的 `card-detail-info` 区域注入：
```javascript
T.jsx("div", {
  className: "card-detail-actions",
  style: { marginTop: "14px", display: "flex", gap: "10px" },
  children: T.jsx("button", {
    type: "button",
    className: "subtle-button bug-report-btn",
    style: {
      display: "flex",
      alignItems: "center",
      gap: "6px",
      padding: "8px 14px",
      borderRadius: "4px",
      border: "1px solid #d45d5d88",
      color: "#fca5a5",
      background: "rgba(185, 28, 28, 0.15)",
      cursor: "pointer",
      fontSize: "12px",
    },
    onClick: () => {
      setBugReportCard(q);
      setBugDesc("");
      setBugError("");
    },
    children: "🐞 报告Bug",
  }),
});
```

### 2.2 提交验证与 Issue 格式化
```javascript
const desc = bugDesc.trim();
if (!desc) {
  setBugError("必须进行 Bug 描述才能提交！");
  return;
}
const card = bugReportCard;
const issueTitle = `[Bug] 卡牌异常: ${card.name} (${card.id})`;
const issueBody = `### 缺陷卡牌信息\n- **卡牌名称**: ${card.name}\n- **卡牌编号**: ${card.id}\n- **职业**: ${card.cardClass ?? "中立"}\n- **费用**: ${card.cost ?? 0}\n- **品质**: ${Sz[card.rarity ?? ""] ?? "普通"}\n- **系列**: ${yz[card.set ?? ""] ?? card.set ?? "未知"}\n- **卡牌描述**: ${card.text ?? "无"}\n\n### Bug 描述\n${desc}\n\n---\n*提交环境: 炉石传说单机版客户端 / 卡牌详情内置反馈*`;

const repo = window.HSO_CONFIG?.GITHUB_REPO || "LayerLwb/HearthstoneOffline";
const githubUrl = `https://github.com/${repo}/issues/new?title=${encodeURIComponent(issueTitle)}&body=${encodeURIComponent(issueBody)}`;

try {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(issueBody);
  }
} catch (_) {}

window.open(githubUrl, "_blank");
o && o("Bug 报告已生成，正在前往 GitHub Issue 提交页面！");
setBugReportCard(null);
```
