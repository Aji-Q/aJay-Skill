# J Trader · OpenCode 安装与使用

J Trader 由 aJay（Aji-Q）维护；为保持兼容，默认安装目标仍是 `Aji-Q/aJay-Skill`，技术标识仍为 `ajay`。

```bash
git clone https://github.com/Aji-Q/aJay-Skill.git
cd aJay-Skill
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py AAPL --depth medium --no-browser
```

需要 Python 3.10+。打开此仓库，读 `AGENTS.md`，用自然语言请求“用 J Trader 深度研究 AAPL”。深度研究按文档完成数据采集、美股补数与 agent 复核；报告路径以实际终端输出为准。

默认本地报告；`--remote` 属于主动公开访问选项。A 股 / 港股保留兼容，不代表相同覆盖能力。

更新前核对 `origin` 属于 `Aji-Q/aJay-Skill`，再执行 `git pull --ff-only`。详见根目录 `README.md` 与 `NOTICE`；[问题反馈](https://github.com/Aji-Q/aJay-Skill/issues)。
