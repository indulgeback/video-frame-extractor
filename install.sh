#!/bin/bash
set -e

REPO_URL="https://github.com/indulgeback/video-frame-extractor.git"
INSTALL_DIR="$HOME/.video-frame-extractor"

echo "正在下载 video-frame-extractor 到 $INSTALL_DIR ..."
rm -rf "$INSTALL_DIR"
git clone --depth=1 "$REPO_URL" "$INSTALL_DIR"

echo "正在安装依赖并注册命令..."
cd "$INSTALL_DIR"
pip3 install .

echo "恭喜你，安装完成！你可以直接使用 frame-extractor 命令;使用方法: frame-extractor --help;更多开源工具请Follow: https://github.com/indulgeback"