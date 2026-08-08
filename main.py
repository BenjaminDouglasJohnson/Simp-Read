import os
import re
import json
import threading
import webbrowser
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from openai import OpenAI
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

# ==========================================
# 1. 多语言文本字典 (I18N Dictionary)
# ==========================================

I18N = {
    "zh": {
        "title": "EPUB AI 通俗化重构工具 v7.8",
        "lang_label": "界面语言 / Language:",
        "sec1_title": " 1. 智能省 Token 与自适应重构规则 ",
        "chk_cite": "引用资料/文献索引/纯网址自动用点号 '.' 代替（不调 AI）",
        "filter_prefix": "过滤随手打字/空行 (少于",
        "filter_suffix": "个字的短行不送 AI 处理，直接跳过)",
        "chk_delay": "开启请求间隔 (防 429 限流)",
        "delay_unit": "秒",
        "prompt_label": "自适应 Prompt 指令:",
        "default_prompt": (
            "你是一个精简的语言转译与文本重构大师。请把输入的文本重写为【极简通俗人话】。\n\n"
            "【特殊处理规则（严格执行）】：\n"
            "1. 引用文献与来源处理：形如『陈瑞麟（东吴大学哲学教授）』或『——米歇尔·福柯，《哲学剧场》(1970, 第885页)』等学术引用/注释，一律简化为『引自（作者的名字）』。输出中严禁包含出版时间、文献名称、出版社和具体页码！\n"
            "2. 致谢与前言尾页处理：遇到致谢人员、图书前言或尾页等大段客套说明，直接用 1 句话总结概括即可。\n"
            "3. 连续人物对话与密集短句：对于多行连续的人物对话或短句，请联系上下文，将其整合提炼为 1~2 句通俗的白话总结，去除冗余语气词。\n\n"
            "【核心字数与句数控制规则】：\n"
            "1. 短文本（< 30字）：只输出 1 句极简白话，严禁添加任何额外修饰或扩写。\n"
            "2. 中等文本（30 - 150字）：输出 1~2 句核心白话，精准还原关键意思。\n"
            "3. 超长密集文本（> 150字）：将其分层次重构，输出 3 句左右通俗白话。"
        ),
        "sec2_title": " 2. 自定义 API 接口 (支持多节点自动轮询) ",
        "btn_add_api": "+ 添加更多 API 节点",
        "sec3_title": " 3. 备用 API Key ",
        "label_qianwen": "阿里千问:",
        "label_gemini": "Gemini Key:",
        "sec4_title": " 4. 文件设置 ",
        "label_input": "输入 EPUB:",
        "label_output": "输出 EPUB:",
        "btn_browse": "浏览...",
        "chk_bilingual": "开启【原本双语对照模式】（建议勾选）",
        "btn_start": "🚀 开始重构 EPUB",
        "btn_stop": "🛑 停止运行",
        "sec_log_title": " 运行日志 ",
        "btn_guide": "❓ 排错指南",
        "github_tip": "🔗 点击前往开发者 GitHub 主页",
        "quotes": [
            "“如果你不能简单地解释它，你就没有真正理解它。” —— 理查德·费曼",
            "“妙言至径，大道至简。” —— 陶埴",
            "“明晰是文体的首要美德。” —— 休·布莱尔",
            "“书中每增加一个方程式，销量就会减半。” ——  斯蒂芬·霍金"
        ],
        "tip_text": (
            "💡 极速排错指南：\n\n"
            "1. 404 Not Found：\n"
            "   - Gemini 旧版 gemini-1.5-flash 已下线，请改为 gemini-1.5-pro 或 gemini-2.0-flash。\n"
            "   - 检查 Base URL 是否为 https://generativelanguage.googleapis.com/v1beta/openai/\n\n"
            "2. 403 / IP 区域限制与 429 限流：\n"
            "   - 请确保开启全局代理，并切换节点至美国 (US)、日本 (JP) 或新加坡 (SG)。\n"
            "   - 若频繁遭遇 429 Rate Limit，请在设置中勾选『开启请求间隔』并调高延迟时间（建议 2~4 秒）。\n\n"
            "3. 断点续传日志：\n"
            "   - 生成的缓存文件位于原 EPUB 所在目录下 (*.checkpoint.json)。"
        ),
        "col_name": "名称:",
        "col_url": "Base URL:",
        "col_key": "API Key:",
        "col_model": "Model:"
    },
    "en": {
        "title": "EPUB AI Simplifier Tool v7.8",
        "lang_label": "界面语言 / Language:",
        "sec1_title": " 1. Smart Token Saving & Adaptive Rules ",
        "chk_cite": "Replace citations/URLs with '.' directly (Skip AI call)",
        "filter_prefix": "Skip short lines less than",
        "filter_suffix": "characters without calling AI",
        "chk_delay": "Enable Delay between API Calls (Prevent 429)",
        "delay_unit": "s",
        "prompt_label": "Adaptive System Prompt:",
        "default_prompt": (
            "You are a master of text simplification and rewriting. Please rewrite the given text into plain, simple language.\n\n"
            "[SPECIAL RULES]:\n"
            "1. Academic Citations: Simplify references like 'Michel Foucault, Theatrum Philosophicum (1970, p.885)' to 'Cited from (Author Name)'. DO NOT include year, book title, publisher, or page numbers.\n"
            "2. Acknowledgments & Prefaces: Summarize lengthy prefaces or acknowledgments into a single brief sentence.\n"
            "3. Continuous Dialogues: For multi-line dialogue or short sentences, synthesize them into 1-2 core plain sentences.\n\n"
            "[LENGTH CONTROL RULES]:\n"
            "1. Short Text (<30 chars): Output exactly 1 plain sentence.\n"
            "2. Medium Text (30-150 chars): Output 1-2 plain sentences capturing the core meaning.\n"
            "3. Long Text (>150 chars): Restructure into structured plain text, ~3 sentences."
        ),
        "sec2_title": " 2. Custom API Endpoints (Multi-node Fallback) ",
        "btn_add_api": "+ Add API Endpoint",
        "sec3_title": " 3. Backup API Keys ",
        "label_qianwen": "Qwen Key:",
        "label_gemini": "Gemini Key:",
        "sec4_title": " 4. File Settings ",
        "label_input": "Input EPUB:",
        "label_output": "Output EPUB:",
        "btn_browse": "Browse...",
        "chk_bilingual": "Enable Original/Simplified Bilingual Mode (Recommended)",
        "btn_start": "🚀 Start EPUB Processing",
        "btn_stop": "🛑 Stop Execution",
        "sec_log_title": " Execution Logs ",
        "btn_guide": "❓ Troubleshooting",
        "github_tip": "🔗 Click to visit Developer's GitHub Homepage",
        "quotes": [
            "\"If you can’t explain it simply, you don’t understand it well enough.\" — Richard Feynman",
            "\"The finest sayings are the shortest; the grandest doctrines are the simplest.\" — Tao Zhi",
            "\"Perspicuity is the first virtue of style.\" — Hugh Blair",
            "\"For every equation added to a book, it cuts the sales in half.\" — Stephen Hawking"
        ],
        "tip_text": (
            "💡 Troubleshooting Guide:\n\n"
            "1. 404 Not Found:\n"
            "   - gemini-1.5-flash is retired. Use gemini-1.5-flash or gemini-2.0-flash instead.\n"
            "   - Ensure Base URL is https://generativelanguage.googleapis.com/v1beta/openai/\n\n"
            "2. 403 / Region Block & 429 Rate Limit:\n"
            "   - Ensure global proxy is enabled with US/JP/SG node.\n"
            "   - If encountering 429 Errors, check 'Enable Delay between API Calls' and increase duration (2-4s recommended).\n\n"
            "3. Checkpoint Cache:\n"
            "   - Saved under the same directory as original EPUB (*.checkpoint.json)."
        ),
        "col_name": "Name:",
        "col_url": "Base URL:",
        "col_key": "API Key:",
        "col_model": "Model:"
    }
}


# ==========================================
# 2. 悬浮提示框 (Tooltip) 实现类
# ==========================================

class HoverTooltip:
    def __init__(self, widget, text_func, offset_x=-110):
        self.widget = widget
        self.text_func = text_func
        self.offset_x = offset_x
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text_func():
            return

        x = self.widget.winfo_rootx() + self.offset_x
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw, text=self.text_func(), justify="left",
            background="#ffffe0", relief="solid", borderwidth=1,
            font=("Microsoft YaHei UI", 9), padx=10, pady=8
        )
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


# ==========================================
# 3. API 调度器与辅助类
# ==========================================

class MultiLLMManager:
    def __init__(self, api_configs, log_func=None):
        self.api_configs = [c for c in api_configs if c.get("api_key") and c.get("base_url")]
        self.log_func = log_func

    def log(self, message):
        print(message)
        if self.log_func:
            self.log_func(message)

    def request(self, system_prompt, user_text):
        if not self.api_configs:
            self.log("[Error] No valid API configuration found!")
            return None

        for config in self.api_configs:
            provider_name = config.get("name") or "API Node"
            base_url = config.get("base_url").rstrip('/')
            api_key = config.get("api_key")
            model = config.get("model", "gemini-2.0-flash")

            try:
                client = OpenAI(base_url=base_url, api_key=api_key, timeout=30)
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_text}
                    ],
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()

            except Exception as e:
                error_str = str(e)
                self.log(f"[Error] Node '{provider_name}' ({model}) failed:")
                if "403" in error_str or "Location not supported" in error_str:
                    self.log("   └─ ❌ [403/Region] Proxy location unsupported. Switch to US/JP/SG node.")
                elif "401" in error_str:
                    self.log("   └─ ❌ [401 Unauthorized] Invalid API Key.")
                elif "404" in error_str:
                    self.log(
                        f"   └─ ❌ [404 Not Found] Model '{model}' not found or regional IP blocked. Try 'gemini-2.0-flash' and check US proxy.")
                elif "429" in error_str:
                    self.log("   └─ ❌ [429 Rate Limit] Rate limit exceeded.")
                else:
                    self.log(f"   └─ ❌ Details: {error_str}")

                self.log("   └─ 🔄 Switching to next available API node...")

        self.log("[Error] All API nodes failed. Fallback to original text.")
        return None


class TextPackager:
    @staticmethod
    def pack_paragraphs(p_tags, min_length=25):
        packed_blocks = []
        buffer_tags, buffer_texts = [], []

        for p in p_tags:
            text_str = p.get_text().strip()
            if not text_str:
                continue

            is_dialogue_or_short = (
                    len(text_str) < min_length or
                    text_str.startswith("“") or text_str.startswith('"') or
                    "：" in text_str[:5] or ":" in text_str[:5]
            )

            if is_dialogue_or_short:
                buffer_tags.append(p)
                buffer_texts.append(text_str)
            else:
                if buffer_texts:
                    packed_blocks.append(
                        {"type": "dialogue_block", "tags": buffer_tags, "text": "\n".join(buffer_texts)})
                    buffer_tags, buffer_texts = [], []

                packed_blocks.append({"type": "normal_para", "tags": [p], "text": text_str})

        if buffer_texts:
            packed_blocks.append({"type": "dialogue_block", "tags": buffer_tags, "text": "\n".join(buffer_texts)})

        return packed_blocks


# ==========================================
# 4. GUI 主界面
# ==========================================

class SimpReadApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "zh"
        self.is_running = False
        self.api_rows = []

        # 实例化 Main Canvas 滚动视图
        self.main_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.v_scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.main_canvas.yview)

        self.scroll_content = ttk.Frame(self.main_canvas)
        self.scroll_content.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )

        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.main_canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.main_canvas.bind('<Configure>', self._on_canvas_configure)
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

        self.setup_ui()
        self.update_language(None)

    def _on_canvas_configure(self, event):
        self.main_canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        top, _ = self.main_canvas.yview()
        if event.delta > 0 and top <= 0:
            return
        self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def open_github(self):
        webbrowser.open_new_tab("https://github.com/BenjaminDouglasJohnson")

    def setup_ui(self):
        self.root.geometry("920x900")
        self.root.minsize(700, 500)

        # ----------------------------------------------------
        # 1. 固定顶部置顶栏
        # ----------------------------------------------------
        top_frame = ttk.Frame(self.root)
        top_frame.pack(side="top", fill="x", padx=15, pady=(10, 5))

        self.lbl_lang = ttk.Label(top_frame, text="")
        self.lbl_lang.pack(side="left")

        self.combo_lang = ttk.Combobox(top_frame, values=["中文 (Chinese)", "English"], state="readonly", width=16)
        self.combo_lang.current(0)
        self.combo_lang.pack(side="left", padx=5)
        self.combo_lang.bind("<<ComboboxSelected>>", self.update_language)

        # 右侧按钮组
        self.btn_github = ttk.Button(top_frame, text="🐙 GitHub", command=self.open_github)
        self.btn_github.pack(side="right", padx=(5, 0))

        self.btn_guide = ttk.Button(top_frame, text="")
        self.btn_guide.pack(side="right", padx=5)

        HoverTooltip(self.btn_github, lambda: I18N[self.current_lang]["github_tip"], offset_x=-110)
        HoverTooltip(self.btn_guide, lambda: I18N[self.current_lang]["tip_text"], offset_x=-150)

        # ----------------------------------------------------
        # 2. 挂载下方滚动区域
        # ----------------------------------------------------
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.v_scrollbar.pack(side="right", fill="y")

        # 1. Rules Frame
        self.frame1 = ttk.LabelFrame(self.scroll_content, text="")
        self.frame1.pack(fill="x", padx=15, pady=5)

        self.var_cite_dot = tk.BooleanVar(value=True)
        self.chk_cite = ttk.Checkbutton(self.frame1, text="", variable=self.var_cite_dot)
        self.chk_cite.pack(anchor="w", padx=10, pady=(5, 2))

        filter_frame = ttk.Frame(self.frame1)
        filter_frame.pack(fill="x", padx=10, pady=2)
        self.lbl_filter1 = ttk.Label(filter_frame, text="")
        self.lbl_filter1.pack(side="left")
        self.spin_min_len = ttk.Spinbox(filter_frame, from_=0, to=50, width=5)
        self.spin_min_len.set(8)
        self.spin_min_len.pack(side="left", padx=2)
        self.lbl_filter2 = ttk.Label(filter_frame, text="")
        self.lbl_filter2.pack(side="left")

        # 防 429 断流延时选项
        delay_frame = ttk.Frame(self.frame1)
        delay_frame.pack(fill="x", padx=10, pady=2)
        self.var_enable_delay = tk.BooleanVar(value=True)
        self.chk_delay = ttk.Checkbutton(delay_frame, text="", variable=self.var_enable_delay)
        self.chk_delay.pack(side="left")
        self.spin_delay_sec = ttk.Spinbox(delay_frame, from_=0.1, to=60.0, increment=0.5, width=6)
        self.spin_delay_sec.set(2.0)
        self.spin_delay_sec.pack(side="left", padx=5)
        self.lbl_delay_unit = ttk.Label(delay_frame, text="")
        self.lbl_delay_unit.pack(side="left")

        # Prompt 标题与名言控件组合 Header
        prompt_header = ttk.Frame(self.frame1)
        prompt_header.pack(fill="x", padx=10, pady=(8, 4))

        self.lbl_prompt = ttk.Label(prompt_header, text="")
        self.lbl_prompt.pack(side="left")

        self.combo_quotes = ttk.Combobox(
            prompt_header,
            state="readonly",
            font=("Microsoft YaHei UI", 8, "italic")
        )
        self.combo_quotes.pack(side="right", fill="x", expand=True, padx=(120, 0))

        self.txt_prompt = tk.Text(self.frame1, height=9, font=("Consolas", 9))
        self.txt_prompt.pack(fill="x", padx=10, pady=(0, 8))

        # 2. Multi-API Frame
        self.frame_api = ttk.LabelFrame(self.scroll_content, text="")
        self.frame_api.pack(fill="x", padx=15, pady=5)

        self.api_container = ttk.Frame(self.frame_api)
        self.api_container.pack(fill="x", padx=5, pady=2)

        self.add_api_row("DashScope", "https://dashscope.aliyuncs.com/compatible-mode/v1", "", "qwen3.6-plus")
        self.add_api_row("Gemini Official", "https://generativelanguage.googleapis.com/v1beta/openai/", "",
                         "gemini-2.0-flash")

        self.btn_add_api = ttk.Button(self.frame_api, text="", command=self.add_api_row)
        self.btn_add_api.pack(anchor="w", padx=10, pady=(2, 5))

        # 3. Backup API Frame
        self.frame3 = ttk.LabelFrame(self.scroll_content, text="")
        self.frame3.pack(fill="x", padx=15, pady=5)
        f3_inner = ttk.Frame(self.frame3)
        f3_inner.pack(fill="x", padx=10, pady=5)

        self.lbl_qw = ttk.Label(f3_inner, text="")
        self.lbl_qw.pack(side="left")
        self.entry_qianwen = ttk.Entry(f3_inner, width=22)
        self.entry_qianwen.pack(side="left", padx=(2, 15))

        self.lbl_gm = ttk.Label(f3_inner, text="")
        self.lbl_gm.pack(side="left")
        self.entry_gemini = ttk.Entry(f3_inner, width=22, show="*")
        self.entry_gemini.pack(side="left", padx=2)

        # 4. File Settings Frame
        self.frame4 = ttk.LabelFrame(self.scroll_content, text="")
        self.frame4.pack(fill="x", padx=15, pady=5)
        f4_grid = ttk.Frame(self.frame4)
        f4_grid.pack(fill="x", padx=10, pady=5)

        self.lbl_inp = ttk.Label(f4_grid, text="")
        self.lbl_inp.grid(row=0, column=0, sticky="e", pady=2)
        self.entry_input = ttk.Entry(f4_grid, width=58)
        self.entry_input.grid(row=0, column=1, padx=5, pady=2)
        self.btn_b1 = ttk.Button(f4_grid, text="", command=self.browse_input)
        self.btn_b1.grid(row=0, column=2, padx=2, pady=2)

        self.lbl_out = ttk.Label(f4_grid, text="")
        self.lbl_out.grid(row=1, column=0, sticky="e", pady=2)
        self.entry_output = ttk.Entry(f4_grid, width=58)
        self.entry_output.grid(row=1, column=1, padx=5, pady=2)
        self.btn_b2 = ttk.Button(f4_grid, text="", command=self.browse_output)
        self.btn_b2.grid(row=1, column=2, padx=2, pady=2)

        self.var_bilingual = tk.BooleanVar(value=True)
        self.chk_bi = ttk.Checkbutton(self.frame4, text="", variable=self.var_bilingual)
        self.chk_bi.pack(anchor="w", padx=10, pady=(2, 5))

        # Controls Frame
        btn_frame = ttk.Frame(self.scroll_content)
        btn_frame.pack(fill="x", padx=15, pady=5)

        self.btn_start = ttk.Button(btn_frame, text="", command=self.start_processing)
        self.btn_start.pack(side="left", expand=True, fill="x", padx=(0, 5))

        self.btn_stop = ttk.Button(btn_frame, text="", command=self.stop_processing, state="disabled")
        self.btn_stop.pack(side="right", expand=True, fill="x", padx=(5, 0))

        # Log Frame
        self.log_frame = ttk.LabelFrame(self.scroll_content, text="")
        self.log_frame.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        self.txt_log = ScrolledText(self.log_frame, height=10, font=("Consolas", 9))
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)

    def update_language(self, event):
        lang_idx = self.combo_lang.current()
        self.current_lang = "zh" if lang_idx == 0 else "en"
        txt = I18N[self.current_lang]

        self.root.title(txt["title"])
        self.lbl_lang.config(text=txt["lang_label"])
        self.btn_guide.config(text=txt["btn_guide"])

        current_quote_idx = self.combo_quotes.current()
        if current_quote_idx < 0:
            current_quote_idx = 0
        self.combo_quotes.config(values=txt["quotes"])
        self.combo_quotes.current(current_quote_idx)

        self.frame1.config(text=txt["sec1_title"])
        self.chk_cite.config(text=txt["chk_cite"])
        self.lbl_filter1.config(text=txt["filter_prefix"])
        self.lbl_filter2.config(text=txt["filter_suffix"])
        self.chk_delay.config(text=txt["chk_delay"])
        self.lbl_delay_unit.config(text=txt["delay_unit"])
        self.lbl_prompt.config(text=txt["prompt_label"])

        self.txt_prompt.delete("1.0", tk.END)
        self.txt_prompt.insert("1.0", txt["default_prompt"])

        self.frame_api.config(text=txt["sec2_title"])
        self.btn_add_api.config(text=txt["btn_add_api"])

        for row in self.api_rows:
            row["lbl_name"].config(text=txt["col_name"])
            row["lbl_url"].config(text=txt["col_url"])
            row["lbl_key"].config(text=txt["col_key"])
            row["lbl_model"].config(text=txt["col_model"])

        self.frame3.config(text=txt["sec3_title"])
        self.lbl_qw.config(text=txt["label_qianwen"])
        self.lbl_gm.config(text=txt["label_gemini"])

        self.frame4.config(text=txt["sec4_title"])
        self.lbl_inp.config(text=txt["label_input"])
        self.lbl_out.config(text=txt["label_output"])
        self.btn_b1.config(text=txt["btn_browse"])
        self.btn_b2.config(text=txt["btn_browse"])
        self.chk_bi.config(text=txt["chk_bilingual"])

        self.btn_start.config(text=txt["btn_start"])
        self.btn_stop.config(text=txt["btn_stop"])
        self.log_frame.config(text=txt["sec_log_title"])

    def add_api_row(self, name="", url="", key="", model=""):
        txt = I18N[self.current_lang]
        row = ttk.Frame(self.api_container)
        row.pack(fill="x", pady=2)

        lbl_name = ttk.Label(row, text=txt["col_name"])
        lbl_name.pack(side="left")
        e_name = ttk.Entry(row, width=10)
        e_name.insert(0, name)
        e_name.pack(side="left", padx=2)

        lbl_url = ttk.Label(row, text=txt["col_url"])
        lbl_url.pack(side="left")
        e_url = ttk.Entry(row, width=28)
        e_url.insert(0, url)
        e_url.pack(side="left", padx=2)

        lbl_key = ttk.Label(row, text=txt["col_key"])
        lbl_key.pack(side="left")
        e_key = ttk.Entry(row, width=16, show="*")
        e_key.insert(0, key)
        e_key.pack(side="left", padx=2)

        lbl_model = ttk.Label(row, text=txt["col_model"])
        lbl_model.pack(side="left")
        e_model = ttk.Entry(row, width=18)
        e_model.insert(0, model)
        e_model.pack(side="left", padx=2)

        btn_del = ttk.Button(row, text="❌", width=3, command=lambda: self.remove_api_row(row))
        btn_del.pack(side="left", padx=2)

        self.api_rows.append({
            "frame": row, "lbl_name": lbl_name, "name": e_name,
            "lbl_url": lbl_url, "url": e_url, "lbl_key": lbl_key,
            "key": e_key, "lbl_model": lbl_model, "model": e_model
        })

    def remove_api_row(self, row_frame):
        row_frame.destroy()
        self.api_rows = [r for r in self.api_rows if r["frame"] != row_frame]

    def _safe_log_insert(self, msg_str):
        current_y = self.txt_log.yview()
        is_at_bottom = current_y[1] >= 0.98

        self.txt_log.insert(tk.END, msg_str)

        if is_at_bottom:
            self.txt_log.see(tk.END)

    def log(self, msg):
        msg_str = str(msg) + "\n"
        self.root.after(0, lambda: self._safe_log_insert(msg_str))

    def browse_input(self):
        path = filedialog.askopenfilename(filetypes=[("EPUB Files", "*.epub")])
        if path:
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, path)
            if not self.entry_output.get():
                self.entry_output.insert(0, path.replace(".epub", "_easy.epub"))

    def browse_output(self):
        path = filedialog.asksaveasfilename(filetypes=[("EPUB Files", "*.epub")])
        if path:
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, path)

    def get_all_api_configs(self):
        configs = []
        for r in self.api_rows:
            u, k, m = r["url"].get().strip(), r["key"].get().strip(), r["model"].get().strip()
            if u and k:
                configs.append({"name": r["name"].get().strip(), "base_url": u, "api_key": k, "model": m})

        q_key = self.entry_qianwen.get().strip()
        if q_key:
            configs.append({"name": "Qwen Backup", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                            "api_key": q_key, "model": "qwen3.6-plus"})
        g_key = self.entry_gemini.get().strip()
        if g_key:
            configs.append(
                {"name": "Gemini Backup", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                 "api_key": g_key, "model": "gemini-2.0-flash"})
        return configs

    def start_processing(self):
        input_path = self.entry_input.get().strip()
        output_path = self.entry_output.get().strip()

        if not input_path or not os.path.exists(input_path):
            messagebox.showerror("Error", "Please select a valid EPUB file!")
            return

        api_configs = self.get_all_api_configs()
        if not api_configs:
            messagebox.showerror("Error", "Please configure at least one valid API Endpoint!")
            return

        self.is_running = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.txt_log.delete("1.0", tk.END)

        threading.Thread(target=self.run_worker, args=(input_path, output_path, api_configs), daemon=True).start()

    def stop_processing(self):
        self.is_running = False
        self.log("\n[Notice] Task canceled by user.")
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

    def run_worker(self, input_path, output_path, api_configs):
        self.log(f"Reading EPUB file: {input_path} ...")
        llm_mgr = MultiLLMManager(api_configs, log_func=self.log)
        checkpoint_path = input_path + ".checkpoint.json"

        cache = {}
        if os.path.exists(checkpoint_path):
            try:
                with open(checkpoint_path, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                self.log(f"Loaded checkpoint with {len(cache)} entries.")
            except Exception:
                cache = {}

        try:
            book = epub.read_epub(input_path)
        except Exception as e:
            self.log(f"[Error] Failed to read EPUB: {e}")
            self.stop_processing()
            return

        items = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
        min_len = int(self.spin_min_len.get() or 8)
        system_prompt = self.txt_prompt.get("1.0", tk.END).strip()
        is_bilingual = self.var_bilingual.get()

        # 读取延迟配置
        enable_delay = self.var_enable_delay.get()
        try:
            delay_sec = float(self.spin_delay_sec.get())
        except ValueError:
            delay_sec = 2.0

        # 第一步：预扫描全书的有效行/文本块总数，计算准确的全书总行数
        self.log("Scanning document total lines...")
        parsed_doc_blocks = []
        total_lines = 0

        for item in items:
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            p_tags = soup.find_all('p')
            if not p_tags:
                parsed_doc_blocks.append((item, soup, []))
                continue

            packed_blocks = TextPackager.pack_paragraphs(p_tags, min_length=min_len)
            total_lines += len(packed_blocks)
            parsed_doc_blocks.append((item, soup, packed_blocks))

        self.log(f"Total lines/blocks found in EPUB: {total_lines}")

        # 第二步：按全书总行数逐行处理并实时输出日志进度 [当前行数/全书总行数]
        current_line = 0

        for item, soup, packed_blocks in parsed_doc_blocks:
            if not self.is_running:
                break

            if not packed_blocks:
                continue

            for block in packed_blocks:
                if not self.is_running:
                    break

                current_line += 1
                text = block['text']

                if self.var_cite_dot.get() and (text.startswith("http") or "doi.org" in text):
                    rewritten = "."
                elif text in cache:
                    rewritten = cache[text]
                    display_text = text[:20].replace('\n', ' ')
                    self.log(f"[{current_line}/{total_lines}] ({block['type']}) [Cached] {display_text}...")
                else:
                    display_text = text[:25].replace('\n', ' ')
                    # 仅在此处调用一次 log
                    self.log(f"[{current_line}/{total_lines}] ({block['type']}) Processing: {display_text}...")

                    rewritten = llm_mgr.request(system_prompt, text)
                    if not rewritten:
                        rewritten = text

                    # 动态请求间隔控制
                    if enable_delay and delay_sec > 0:
                        time.sleep(delay_sec)

                    cache[text] = rewritten
                    with open(checkpoint_path, 'w', encoding='utf-8') as f:
                        json.dump(cache, f, ensure_ascii=False, indent=2)

                tags = block['tags']
                if tags:
                    main_tag = tags[0]
                    if is_bilingual and rewritten != ".":
                        # 清空原标签文本，改用 BeautifulSoup 插入 <br> 显式换行
                        main_tag.clear()
                        main_tag.append(text)
                        main_tag.append(soup.new_tag("br"))
                        main_tag.append(soup.new_tag("br"))
                        main_tag.append(f"【sim】：{rewritten}")
                    else:
                        main_tag.string = rewritten

                    for extra_tag in tags[1:]:
                        extra_tag.decompose()

            item.set_content(soup.encode('utf-8'))

        if self.is_running:
            try:
                epub.write_epub(output_path, book)
                self.log(f"\n🎉 [Success] EPUB exported to: {output_path}")
                messagebox.showinfo("Success", f"EPUB re-structured successfully!\nSaved to: {output_path}")
            except Exception as e:
                self.log(f"\n[Error] Export failed: {e}")

        self.root.after(0, lambda: self.btn_start.config(state="normal"))
        self.root.after(0, lambda: self.btn_stop.config(state="disabled"))


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpReadApp(root)
    root.mainloop()