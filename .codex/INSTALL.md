# J Trader · Codex 安装与使用

J Trader 由 aJay（Aji-Q）维护；为保持兼容，安装目标仍是 `Aji-Q/aJay-Skill`，技术标识仍为 `ajay`。

```bash
git clone https://github.com/Aji-Q/aJay-Skill.git
cd aJay-Skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

需要 Python 3.10+。GitHub 若要求认证，请使用你自己的仓库访问凭据。

让 Codex 打开此仓库并读取根目录 `AGENTS.md`，然后说：

> 用 J Trader 研究 AAPL；先核对数据质量，再生成报告。

快速扫描：

```bash
python run.py AAPL --depth medium --no-browser
```

深度分析须按 `AGENTS.md` 完成采集、美股补数、重新建模、带输入指纹的 agent 复核及报告生成；一次 CLI 运行不等于完成复核。

终端会输出报告实际路径。默认保留本机；`--remote` 会创建可访问的外部链接，使用前先检查报告信息。

更新：先确认 `git remote get-url origin` 是 `https://github.com/Aji-Q/aJay-Skill.git` 或其 SSH 等价地址，再执行 `git pull --ff-only`。完整资料见根目录 `README.md`；问题反馈至 [J Trader issues](https://github.com/Aji-Q/aJay-Skill/issues)。
