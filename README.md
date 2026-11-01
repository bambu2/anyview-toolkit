# Anyview Toolkit

**半**自动答题工具，用来复制题目和自动输入答案。

## 安装
```bash
uv sync
```

## 使用
1. 登录 Anyview，进入答题页面。
2. 使用浏览器的检查功能选中问题。
3. 运行 `uv run anyview-toolkit copy`，答案会被复制到剪贴板。
4. 粘贴题目给 AI，提示词示例：“我给题目，你给答案，不用注释”。
5. 复制答案。
6. 运行 `uv run anyview-toolkit type`，在倒计时时间内把焦点切到目标文本框。
7. 切换英文输入法，等待答案全部被输入到 Anyview 的答案框中，运行答案。

## FAQ

### Q: 为什么不用 Playwright / Selenium ?
A: 保持项目轻量，以及我不会。

### Q: 为什么不写自动登录 Anyview ?
A: 建议用 Bitwarden 之类的密码管理器来填写登录信息。

### Q: 为什么不写接入 AI API 的代码 ?
A: 不要为了 Anyview 花钱。

### Q: 为什么用 PyAutoGUI 来输入 Anyview 的答案框 ?
- Anyview 的答案框是一堆 div 和 span，用 Playwright / Selenium 可能会复杂。
- 用 PyAutoGUI 来输入有 Anyview 的编辑器格式化。
- 保证一定时长的题目计时，避免被 Anyview 认为是作弊。

### Q: 为什么输入时有随机延迟和随机错误 ?
- 水时长。
- 模拟真实用户的行为。
- 想看脚本打字时不会那么无聊。

### Q: 答案要求 ?
A: 不要有中文即可。脚本会删除行首空格和符号两侧空格。

### Q: 题目不会 / 答案看不懂 / 运行不通过 / AI 答案不像人写的?
A: 请自己学习，自己修改答案。
