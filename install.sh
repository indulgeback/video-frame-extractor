#!/bin/bash
set -e
TMP_DIR=$(mktemp -d)
echo "正在下载 video-frame-extractor..."
git clone https://github.com/indulgeback/video-frame-extractor.git $TMP_DIR
cd $TMP_DIR
pip3 install .
echo "安装完成！你可以直接使用 frame-extractor 命令。"
