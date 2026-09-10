#!/bin/bash
# J Trader 一键安装脚本（技术目录名保留 aJay-Skill）
# 用法: bash ~/Claude/aJay/setup.sh        # 在源码目录内运行;不在目录内时 AJAY_REPO_URL 默认 https://github.com/Aji-Q/aJay-Skill.git

set -e

REPO_URL="${AJAY_REPO_URL:-https://github.com/Aji-Q/aJay-Skill.git}"

# Compare repository identities before updating an existing checkout. Accept
# GitHub HTTPS/SSH spellings, but never silently repoint another project's origin.
normalize_repo_url() {
    printf '%s' "$1" | sed -E 's#/*$##; s#\.git$##; s#^https?://github\.com/##; s#^ssh://git@github\.com/##; s#^git@github\.com:##'
}
verify_repo_origin() {
    local directory="$1" actual
    actual=$(git -C "$directory" remote get-url origin 2>/dev/null) || {
        echo "❌ $directory 没有 origin；请先确认它是 J Trader 源码，再配置来源。"
        return 1
    }
    if [ "$(normalize_repo_url "$actual")" != "$(normalize_repo_url "$REPO_URL")" ]; then
        echo "❌ 仓库来源不匹配：$actual"
        echo "   预期：${REPO_URL}；未更新该目录。请选择新的 J Trader 目录，或显式设置 AJAY_REPO_URL。"
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 J Trader · 安装中..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查 Python
if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo "❌ 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)
echo "✓ Python: $($PYTHON --version)"

# 检查 git
if ! command -v git &>/dev/null; then
    echo "❌ 未找到 git"
    exit 1
fi

# 克隆（如果不在仓库内）
if [ ! -f "run.py" ]; then
    if [ -d "aJay-Skill" ]; then
        echo "✓ aJay-Skill 目录已存在，更新中..."
        verify_repo_origin "aJay-Skill"
        cd aJay-Skill && git pull --ff-only origin
    else
        # 默认克隆 J Trader 官方仓库；技术仓库名保留 aJay-Skill，可用 AJAY_REPO_URL 覆盖
        AJAY_REPO_URL="${AJAY_REPO_URL:-https://github.com/Aji-Q/aJay-Skill.git}"  # private 仓库,需本机已配置 GitHub 凭据
        echo "⏬ 克隆仓库 $AJAY_REPO_URL ..."
        git clone "$AJAY_REPO_URL" aJay-Skill
        cd aJay-Skill
    fi
else
    if [ -e ".git" ]; then
        verify_repo_origin "."
    fi
    echo "✓ 已在仓库目录中"
fi

# 安装依赖 — 先试默认 pypi，挂了就自动切国内镜像（大陆网络环境友好）
echo "📦 安装 Python 依赖..."

PIP_MIRRORS=(
    ""  # 默认 pypi.org（空字符串代表不指定 -i，走默认）
    "https://pypi.tuna.tsinghua.edu.cn/simple"
    "https://mirrors.aliyun.com/pypi/simple/"
    "https://pypi.mirrors.ustc.edu.cn/simple/"
)

install_deps() {
    local mirror="$1"
    if [ -z "$mirror" ]; then
        $PYTHON -m pip install -r requirements.txt -q 2>/dev/null
    else
        local host
        host=$(echo "$mirror" | awk -F/ '{print $3}')
        $PYTHON -m pip install -r requirements.txt -q \
            --index-url "$mirror" \
            --trusted-host "$host" 2>/dev/null
    fi
}

SUCCESS=0
for mirror in "${PIP_MIRRORS[@]}"; do
    if [ -z "$mirror" ]; then
        echo "   [1] 尝试默认 pypi.org ..."
    else
        echo "   [+] 尝试镜像 $mirror ..."
    fi
    if install_deps "$mirror"; then
        SUCCESS=1
        [ -z "$mirror" ] && echo "   ✓ 安装成功（默认 pypi）" || echo "   ✓ 安装成功（via $mirror）"
        break
    fi
done

if [ "$SUCCESS" -eq 0 ]; then
    echo "   ❌ 所有源都失败。手动试："
    echo "      pip install -r requirements.txt \\"
    echo "          -i https://pypi.tuna.tsinghua.edu.cn/simple"
    exit 1
fi

# v2.6 · 确保 hooks 脚本有可执行权限（论坛报告 macOS Claude plugin 不能执行）
if [ -d "hooks" ]; then
    chmod +x hooks/session-start hooks/run-hook.cmd 2>/dev/null
    echo "✓ hooks 脚本可执行权限已设置"
fi

# 验证
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 安装完成！"
echo ""
echo "用法:"
echo "  python run.py AAPL              # J Trader 美股研究"
echo "  python run.py 贵州茅台          # A 股兼容工作流"
echo "  python run.py 00700.HK          # 分析港股"
echo "  python run.py AAPL --remote      # 主动公开报告访问链接"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
