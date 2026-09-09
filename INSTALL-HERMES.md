# aJay · Hermes 安装

**维护者 aJay（Aji-Q） · 默认仓库 [Aji-Q/aJay-Skill](https://github.com/Aji-Q/aJay-Skill)。**

这是从本地审阅过的源码创建 skill 软链接的安装流程，不经过 Hermes Hub 的 Skills Guard 扫描。运行前阅读脚本及依赖；不要把“跳过扫描”理解为安全认证。

## 1. 获取与检查源码

```bash
git clone https://github.com/Aji-Q/aJay-Skill.git
cd aJay-Skill
# 先阅读 install-hermes.sh、requirements.txt 与 NOTICE
bash install-hermes.sh "$PWD"
```

需要 Python 3.10+、Git 和已安装的 Hermes。GitHub 若要求认证，请使用自己的仓库访问凭据。

脚本默认源为 `Aji-Q/aJay-Skill`，显式 `AJAY_REPO_URL` 可使用自己的镜像。已存在 Git 目录先核对 `origin`，不自动把其他项目改成 aJay。安装会把 4 个 skill 链接到 `${HERMES_HOME:-$HOME/.hermes}/skills/`，请留意同名旧 skill 的处理提示。

## 2. 使用自然语言触发

对 Hermes 说：

> 用 aJay 分析 AAPL，先检查数据质量，再生成研究报告。

**`/ajay:analyze-stock` 是 Claude Code 的插件命令，不是 Hermes 的 slash 命令。** Hermes 加载 `SKILL.md`，不自动注册本仓库 `commands/`。

看到 `Unknown command` 时，使用上面的自然语言请求。快速扫描可运行 `python run.py AAPL --depth medium --no-browser`；深度研究按 `AGENTS.md` 完成 agent 复核。

## 3. 更新

```bash
git -C ~/aJay-Skill remote get-url origin
# 应为 Aji-Q/aJay-Skill 的 GitHub 地址
git -C ~/aJay-Skill pull --ff-only
```

若安装在自定义目录，使用该实际目录。软链接会跟随源文件更新；依赖变化后重新安装 `requirements.txt`。不要运行指向上游仓库的旧 Hub 更新命令。

## 历史兼容说明

继承的安装文档记录过 Skills Guard 的 `DANGEROUS` 诊断，并引用 [NousResearch/hermes-agent #1006](https://github.com/NousResearch/hermes-agent/issues/1006)。这是历史记录，不是对当前 Hermes 版本扫描结果的实时判断。具体告警应逐条检查，不能仅因旧文档称“误报”就忽略。

## 项目边界

- 默认报告保留本机，`--remote` 会公开报告访问入口。
- 美股是当前研究主线，A 股 / 港股路径保留兼容。
- 当前维护反馈入口：[aJay issues](https://github.com/Aji-Q/aJay-Skill/issues)。
- 上游贡献与版权保留于 `NOTICE`、`LICENSE` 和历史档案。
