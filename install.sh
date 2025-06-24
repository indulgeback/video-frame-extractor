#!/bin/bash
set -e

# 彩色输出函数
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }
red() { echo -e "\033[31m$1\033[0m"; }

# 检查依赖
green "🚀 视频帧提取工具一键安装脚本"
echo "----------------------------------------"

if ! command -v git >/dev/null 2>&1; then
    red "❌ 未检测到 git，请先安装 git！"
    exit 1
fi
if ! command -v pip3 >/dev/null 2>&1; then
    red "❌ 未检测到 pip3，请先安装 Python3 和 pip3！"
    exit 1
fi

green "1️⃣ 依赖检测通过，开始下载仓库..."
REPO_URL="https://github.com/indulgeback/video-frame-extractor.git"
INSTALL_DIR="$HOME/.video-frame-extractor"

if [ -d "$INSTALL_DIR" ]; then
    yellow "⚠️  检测到旧的安装目录，正在清理..."
    rm -rf "$INSTALL_DIR"
fi

git clone --depth=1 "$REPO_URL" "$INSTALL_DIR"
green "2️⃣ 仓库下载完成"

green "3️⃣ 开始安装依赖并注册命令..."
cd "$INSTALL_DIR"
pip3 install .

green "4️⃣ 安装完成！"

echo
yellow "[注意] 如果终端提示找不到 frame-extractor 命令，请将如下路径加入你的 PATH："
BIN_PATH="$HOME/Library/Python/3.9/bin"
echo "  export PATH=\"$BIN_PATH:\$PATH\""
echo "  source ~/.zshrc  # 或 source ~/.bashrc"

green "🎉 恭喜你，安装完成！你可以直接使用 frame-extractor 命令。"
echo "使用方法: frame-extractor --help"
echo "更多开源工具请Follow: https://github.com/indulgeback"