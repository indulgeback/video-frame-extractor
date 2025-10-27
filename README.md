# 🎬 视频帧提取工具 Video Frame Extractor

[![GitHub stars](https://img.shields.io/github/stars/indulgeback/video-frame-extractor?style=social)](https://github.com/indulgeback/video-frame-extractor)
[![License](https://img.shields.io/github/license/indulgeback/video-frame-extractor)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)

---

> 基于 OpenCV 的命令行视频帧提取工具，支持单帧、批量、采样提取及视频信息查看。

---

## 🚀 一键安装

```bash
curl -sSL https://raw.githubusercontent.com/indulgeback/video-frame-extractor/main/install.sh | bash
```

脚本会自动下载仓库到 `~/.video-frame-extractor` 并用 pip3 安装。

> **注意**：如果安装后提示 `frame-extractor` 命令找不到（command not found），请将 pip3 的 user bin 路径加入 PATH，例如：
>
> ```bash
> echo 'export PATH="$HOME/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc
> source ~/.zshrc
> ```

## 📦 功能特性

- [x] 支持单帧提取（按帧号或时间点）
- [x] 批量提取多帧
- [x] 按时间间隔采样提取
- [x] 批量目录首帧提取
- [x] 视频信息查看
- [x] 多线程加速
- [x] 兼容常见视频格式
- [x] 跨平台支持（Windows/macOS/Linux）
- [x] 图片压缩转换为 WebP 格式
- [x] 递归目录处理

---

## 🛠️ 命令行用法示例

### 1. 提取单帧（按帧号或时间点）

```bash
# 按帧号提取第100帧
frame-extractor single -i video.mp4 -f 100 -o frame100.jpg

# 按时间点（秒）提取帧
frame-extractor single -i video.mp4 -t 3.5 -o frame_at_3_5s.jpg
```

### 2. 批量提取多帧

```bash
frame-extractor batch -i video.mp4 -o frames -s 10 -e 50 -d 5
```

### 3. 按时间间隔采样提取

```bash
frame-extractor sample -i video.mp4 -o samples -t 2
```

### 4. 显示视频信息

```bash
frame-extractor info -i video.mp4
```

### 5. 批量提取目录下所有视频的首帧

```bash
# 提取当前目录下的视频首帧
frame-extractor dirfirst -i videos_dir -o output_dir

# 递归提取所有子目录下的视频首帧（保持目录结构）
frame-extractor dirfirst -i videos_dir -o output_dir -r

# 提取首帧并压缩转换为WebP格式
frame-extractor dirfirst -i videos_dir -o output_dir -c

# 递归提取首帧并压缩转换（指定WebP质量）
frame-extractor dirfirst -i videos_dir -o output_dir -r -c --webp-quality 90

# 递归提取首帧并压缩，控制文件大小在50-100KB
frame-extractor dirfirst -i video -o output -r -c --min-size 50 --max-size 100
```

### 6. 图片压缩转换为 WebP 格式

```bash
# 压缩当前目录下的图片
frame-extractor compress -i images_dir -o webp_dir

# 递归压缩所有子目录下的图片（保持目录结构）
frame-extractor compress -i images_dir -o webp_dir -r

# 指定WebP压缩质量
frame-extractor compress -i images_dir -o webp_dir -q 95

# 限制文件大小（自动调整质量，确保每个文件不超过100KB）
frame-extractor compress -i images_dir -o webp_dir --max-size 100

# 限制文件大小范围（50KB-200KB之间）
frame-extractor compress -i images_dir -o webp_dir --min-size 50 --max-size 200
```

---

## 📑 命令参数一览

### single（提取单帧）

| 参数         | 说明                 | 必需   | 备注         |
| ------------ | -------------------- | ------ | ------------ |
| -i, --input  | 输入视频路径         | ✅     |              |
| -o, --output | 输出图像路径         |        | 默认自动生成 |
| -f, --frame  | 要提取的帧号         | 二选一 | 和-t 互斥    |
| -t, --time   | 要提取的时间点（秒） | 二选一 | 和-f 互斥    |
| --quality    | JPEG 质量（0-100）   |        | 默认 95      |

### batch（批量提取）

| 参数          | 说明         | 必需 | 备注   |
| ------------- | ------------ | ---- | ------ |
| -i, --input   | 输入视频路径 | ✅   |        |
| -o, --output  | 输出目录     | ✅   |        |
| -s, --start   | 起始帧号     | ✅   |        |
| -e, --end     | 结束帧号     | ✅   |        |
| -d, --delta   | 帧间隔       |      | 默认 1 |
| -w, --workers | 工作线程数   |      | 默认 4 |

### sample（采样提取）

| 参数           | 说明           | 必需 | 备注     |
| -------------- | -------------- | ---- | -------- |
| -i, --input    | 输入视频路径   | ✅   |          |
| -o, --output   | 输出目录       | ✅   |          |
| -t, --interval | 采样间隔（秒） |      | 默认 1.0 |
| -w, --workers  | 工作线程数     |      | 默认 4   |

### info（视频信息）

| 参数        | 说明         | 必需 | 备注 |
| ----------- | ------------ | ---- | ---- |
| -i, --input | 输入视频路径 | ✅   |      |

### dirfirst（批量目录首帧提取）

| 参数             | 说明                   | 必需 | 备注                   |
| ---------------- | ---------------------- | ---- | ---------------------- |
| -i, --input_dir  | 输入视频目录           | ✅   |                        |
| -o, --output_dir | 输出图片目录           | ✅   |                        |
| -r, --recursive  | 递归遍历子目录         |      | 保持对等目录结构       |
| -c, --compress   | 压缩转换为 WebP        |      | 自动清理原始图片       |
| --webp-quality   | WebP 压缩质量（0-100） |      | 默认 85                |
| --max-size       | 最大文件大小（KB）     |      | 默认 100，自动调整质量 |
| --min-size       | 最小文件大小（KB）     |      | 默认 50，自动调整质量  |

### compress（图片压缩转换）

| 参数             | 说明                   | 必需 | 备注                         |
| ---------------- | ---------------------- | ---- | ---------------------------- |
| -i, --input_dir  | 输入图片目录           | ✅   |                              |
| -o, --output_dir | 输出 WebP 图片目录     | ✅   |                              |
| -r, --recursive  | 递归遍历子目录         |      | 保持对等目录结构             |
| -q, --quality    | WebP 压缩质量（0-100） |      | 默认 85                      |
| --max-size       | 最大文件大小（KB）     |      | 默认 100，超过会自动降低质量 |
| --min-size       | 最小文件大小（KB）     |      | 默认 50，小于会自动提高质量  |

---

## 📦 依赖

- opencv-python
- tqdm
- numpy
- Pillow（图片处理和 WebP 格式支持）

---

## ❓ FAQ

- **Q: 安装后命令找不到？**  
  A: 请将 pip3 的 user bin 路径加入 PATH，见上方安装说明。
- **Q: 支持哪些视频格式？**  
  A: 支持 mp4、avi、mov、mkv、flv、wmv 等常见格式。
- **Q: 如何卸载？**  
  A: 运行 `pip3 uninstall video-frame-extractor`，可手动删除 `~/.video-frame-extractor` 目录。
- **Q: 如何贡献代码？**  
  A: 欢迎 PR 或 issue！

---

如需帮助或报错排查，请参考命令行输出信息，或在 GitHub 提 issue。
