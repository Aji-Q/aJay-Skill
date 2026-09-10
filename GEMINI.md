# J Trader · Gemini CLI 指令

J Trader 是由 aJay（Aji-Q）维护的美股研究助手，保留 A 股 / 港股兼容路径；扩展技术名仍为 `ajay`。

## 安装与更新

```bash
gemini extensions install https://github.com/Aji-Q/aJay-Skill
gemini extensions update ajay
```

也可从本仓库安装 Python 3.10+ 依赖，直接执行：

```bash
python -m pip install -r requirements.txt
python run.py AAPL --depth medium --no-browser
```

## 完整流程

读 `AGENTS.md` 和 `skills/deep-analysis/SKILL.md`：采集 → 按需美股补数 → 重新建模 / 输入指纹 → agent 证据复核 → J Trader 编辑式 HTML 报告。

模拟评审不是人物真实观点，评分不是收益概率。缺失来源应明确展示；默认报告保留本地。

当前项目入口：[Aji-Q/aJay-Skill](https://github.com/Aji-Q/aJay-Skill)。来源与 MIT 版权见 `NOTICE` / `LICENSE`。
