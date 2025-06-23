# 视频帧提取工具

> ## 一键安装
>
> 只需运行：
>
> ```bash
> curl -sSL https://raw.githubusercontent.com/indulgeback/video-frame-extractor/main/install.sh | bash
> ```
>
> 安装脚本 install.sh 内容如下（已包含在仓库根目录）：
>
> ```bash
> #!/bin/bash
> set -e
> TMP_DIR=$(mktemp -d)
> echo "正在下载 video-frame-extractor..."
> git clone https://github.com/indulgeback/video-frame-extractor.git $TMP_DIR
> cd $TMP_DIR
> pip install .
> echo "安装完成！你可以直接使用 frame-extractor 命令。"
>
> 安装完成后，请添加环境变量
> echo 'export PATH=$PATH:/Users/a1234/Library/Python/3.9/bin' >> ~/.zshrc
> source ~/.zshrc
> 
> ```
>
> 安装完成后，可直接使用 `frame-extractor` 命令，无需 python src/frame_extractor.py ...

基于 OpenCV 的命令行视频帧提取工具，支持单帧、批量、采样提取及视频信息查看。

## 安装

### 1. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 命令行用法示例

### 1. 提取单帧（按帧号或时间点）

```bash
# 按帧号提取第100帧
python3 src/frame_extractor.py single -i video.mp4 -f 100 -o frame100.jpg

# 按时间点（秒）提取帧
python3 src/frame_extractor.py single -i video.mp4 -t 3.5 -o frame_at_3_5s.jpg
```

### 2. 批量提取多帧

```bash
# 提取第10帧到第50帧，每隔5帧提取一张，输出到frames目录
python3 src/frame_extractor.py batch -i video.mp4 -o frames -s 10 -e 50 -d 5
```

### 3. 按时间间隔采样提取

```bash
# 每隔2秒采样一帧，输出到samples目录
python3 src/frame_extractor.py sample -i video.mp4 -o samples -t 2
```

### 4. 显示视频信息

```bash
python3 src/frame_extractor.py info -i video.mp4
```

### 5. 批量提取目录下所有视频的首帧

```bash
python3 src/frame_extractor.py dirfirst -i videos_dir -o output_dir
```

## 命令参数说明

### single（提取单帧）

- `-i, --input`：输入视频路径（必需）
- `-o, --output`：输出图像路径（可选，默认自动生成）
- `-f, --frame`：要提取的帧号（二选一，和-t互斥）
- `-t, --time`：要提取的时间点（秒，二选一，和-f互斥）
- `--quality`：JPEG质量（0-100，默认95）

### batch（批量提取）

- `-i, --input`：输入视频路径（必需）
- `-o, --output`：输出目录（必需）
- `-s, --start`：起始帧号（必需）
- `-e, --end`：结束帧号（必需）
- `-d, --delta`：帧间隔（默认1）
- `-w, --workers`：工作线程数（默认4）

### sample（采样提取）

- `-i, --input`：输入视频路径（必需）
- `-o, --output`：输出目录（必需）
- `-t, --interval`：采样间隔（秒，默认1.0）
- `-w, --workers`：工作线程数（默认4）

### info（视频信息）

- `-i, --input`：输入视频路径（必需）

### dirfirst（批量目录首帧提取）

- `-i, --input_dir`：输入视频目录（必需）
- `-o, --output_dir`：输出图片目录（必需）

## 依赖

- opencv-python
- tqdm
- numpy

如需帮助或报错排查，请参考命令行输出信息。
