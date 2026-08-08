<div align="center">
  <h1>📚 SimpRead: AI EPUB 通俗化重构工具</h1>
  <p>
    <a href="README_EN.md">English Version</a> | 
    <b>简体中文</b>
  </p>
</div>

## 📚 Simp Read：把“天书”重构成人话的 AI EPUB 炼金术 v7.8

你是否非常厌烦后现代主义那种堆砌词藻、空洞虚无的文本，折腾半天读不进一章？🤮
你是否因为书架上拖延了半年的厚重名著，每次看到都陷入无尽的阅读焦虑？😫
你又是否想啃一啃硬核大部头的名著，却刚翻开第一页就被高冷晦涩的门槛彻底劝退？🤯

现在，**Simp Read 第7.8版** 来了！😎
一款专门治愈“阅读痛苦症”的 AI 电子书重构工具，可以把你手里的 EPUB 格式书籍，用各种大语言模型直接降维打击，炼成“极简通俗人话”！谁说那些繁冗高冷的原版就不算是一种需要翻译的“天书语言”呢？

### 主界面
![SimpRead 主界面](images/main-ui.png)

## ✨ 为什么它能让你“看书如看戏”？

*   **原白双语对照**：转写后的通俗白话与原文上下逐段对照呈现，既能一眼看懂核心要点，又能随时回头核对原文，阅读体验直接拉满！
*   **抠门级省 Token 算法**：智能识别文献索引、参考文献、乱码网址，直接替换成点号；甚至连致谢名单都能一句话概括。过滤随手打字与空行，绝不把一毛钱浪费在没用的垃圾文本上！
*   **连续对话智能打包**：对于连续的人物对话或短句，算法会自动打包压缩，联系上下文提炼成 1~2 句白话，告别碎片化请求，效率直接翻倍！
*   **多 API 自动轮询接力**：支持阿里千问、Google Gemini 等各种大模型多节点并发。主 Key 额度用光了或者遭遇 IP 区域封锁？别慌，它会自动识别 401/403/404/429 报错，并无缝无感地切换到备用节点接着干，彻底告别额度与报错焦虑！
*   **防 429 限流“保命延时”**：内置动态请求间隔控制，精准把控 API 频率，再也不用担心因为发包太猛被模型提供商拉黑。
*   **上帝视角·全书行数精确进度条**：打破传统的“文件数”模糊计数！系统会自动预扫描全书的有效文本块，日志直接以 `[当前行数/全书总行数]`（比如 `[1/350]`）实时滚动，让你对重构进度了如指掌！
*   **断点续传，随时喊停**：中途关机或者想换个模型？进度实时自动保存为 Checkpoint 缓存文件，重新打开继续跑，绝不重复消耗你宝贵的 Token。
*   **高精排版防崩 UI**：采用独特的 Tkinter 动态滚动画布（Canvas），不管你用多小分辨率的屏幕，控件都不可能被挤出画面；附带鼠标悬浮 Tooltip 提示与排错指南，优雅永不过时。
*   **双语 UI 界面 + 名言调侃**：中英文界面一键切换，内嵌爱因斯坦、理查德·费曼等大佬的“讲人话”名言，一边炼金一边治愈内卷。

### 重构前后对比《个人知识：朝向后批判哲学》
![原文 vs 白话](images/output1.png)

> 当然，如果你懒得折腾高深学术书，把中等难度的畅销书、小说扔进去提纯也完全没问题！不过开发者本人并不承担文学小说被魔改得面貌全非的后果哦～库嘻嘻😚🎵

👉 只需自备 API Key（别忘了可以用阿里和谷歌的免费额度白嫖），即可开启“讲人话”的无痛阅读时代！

## 🍧 **快速开始**：无需配置 Python 环境！直接前往 [👉 Releases 页面](https://github.com/BenjaminDouglasJohnson/Simp-Read/releases/latest) 下载最新版 `SimpRead-v7.8.exe` 开箱即用。

## 🚀 快速上手

### 1. 安装环境与依赖
请确保你的电脑已安装 **Python 3.8+**。

```bash
# 克隆仓库
git clone https://github.com/BenjaminDouglasJohnson/Simp-Read.git
cd Simp-Read

# 安装依赖
pip install -r requirements.txt

# 启动程序
python main.py
. 界面配置与使用步骤 (Usage)
配置 API 节点：在软件第 2 区填写你的大模型 API 信息（Base URL、API Key、Model 名称）。
提示：支持任何兼容 OpenAI 格式的接口（如 DashScope/阿里千问、Google Gemini OpenAI 端点、DeepSeek 等）。
导入 EPUB：点击“浏览...”选择你想要重构的电子书。
开启双语模式（推荐）：勾选“开启原本双语对照模式”，重构后的文字将紧跟原文呈现。
开始重构：点击“🚀 开始重构 EPUB”，观察下方日志即可！
🔌 常见 API 配置参考

提供商	Base URL	推荐 Model
阿里千问 (DashScope)	https://dashscope.aliyuncs.com/compatible-mode/v1	qwen3.6-plus 或 qwen-turbo
Google Gemini	https://generativelanguage.googleapis.com/v1beta/openai/	gemini-2.0-flash
DeepSeek	https://api.deepseek.com/v1	deepseek-chat
❓ 常见问题排错 (FAQ)
 Not Found：请检查 Gemini 模型名是否填写正确（推荐 gemini-2.0-flash），或检查 Base URL 末尾是否有 /openai/。
 / 区域限制：Gemini 等模型需开启全局代理，并切换节点至美国 (US)、日本 (JP) 或新加坡 (SG)。
 Rate Limit（频繁限流）：请勾选界面上的“开启请求间隔”，并将延迟设为 2.0~4.0 秒。
导出的 EPUB 在某些阅读器打不开：推荐配合 Calibre 进行一次“EPUB 到 EPUB”的自动转换即可修复排版结构。
📄 开源协议
本项目采用 MIT License 开源，欢迎提交 PR、Issue 或分享你的 Prompt 玩法！
```
### 重构前后对比2(《哥德尔、埃舍尔、巴赫：集异璧之大成》)
![原文 vs 白话](images/output2.png)

### 重构前后对比3(《政治的概念》)
![原文 vs 白话](images/output3.png)
