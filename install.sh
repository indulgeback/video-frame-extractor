#!/bin/bash
set -e
TMP_DIR=$(mktemp -d)
echo "正在下载 video-frame-extractor..."
git clone https://github.com/indulgeback/video-frame-extractor.git $TMP_DIR
cd $TMP_DIR
pip3 install .
echo "请添加环境变量"
echo "export PATH=$PATH:/Users/<your_user_name>/Library/Python/3.9/bin" >> ~/.zshrc
echo "并刷新环境变量"
echo "source ~/.zshrc"
echo "恭喜你，安装完成！你可以直接使用 frame-extractor 命令。"