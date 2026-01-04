"""
目录批量处理模块
"""
import os
import glob
from pathlib import Path

from .extract import extract_frame
from .compression import compress_images_to_webp


def extract_first_frames_from_dir(input_dir: str, output_dir: str, recursive: bool = False) -> None:
    """
    批量提取目录下所有视频的首帧，输出到指定目录，图片文件名与原视频名一致。
    支持递归遍历子目录。

    参数:
        input_dir: 输入视频目录
        output_dir: 输出图片目录
        recursive: 是否递归遍历子目录
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    exts = ["*.mp4", "*.avi", "*.mov", "*.mkv", "*.flv", "*.wmv"]
    video_files = []

    if recursive:
        for root, dirs, files in os.walk(input_dir):
            for ext in exts:
                pattern = os.path.join(root, ext)
                video_files.extend(glob.glob(pattern))
    else:
        for ext in exts:
            video_files.extend(glob.glob(os.path.join(input_dir, ext)))

    if not video_files:
        print(f"未找到视频文件: {input_dir}")
        return

    print(f"找到 {len(video_files)} 个视频文件")

    for video_path in video_files:
        rel_path = os.path.relpath(video_path, input_dir)
        base = os.path.splitext(rel_path)[0]
        out_path = os.path.join(output_dir, f"{base}.jpg")
        Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)

        try:
            extract_frame(video_path, out_path, 0)
            print(f"✅ 已提取: {rel_path} -> {os.path.relpath(out_path, output_dir)}")
        except Exception as e:
            print(f"❌ 跳过 {rel_path}: {e}")


def extract_first_frames_with_compression(input_dir: str, output_dir: str, recursive: bool = False,
                                        compress: bool = False, webp_quality: int = 85,
                                        max_size_kb: int = None, min_size_kb: int = None) -> None:
    """
    提取视频首帧并可选择性地进行压缩转换

    参数:
        input_dir: 输入视频目录
        output_dir: 输出图片目录
        recursive: 是否递归遍历子目录
        compress: 是否压缩转换为WebP
        webp_quality: WebP压缩质量（0-100，默认85）
        max_size_kb: 最大文件大小（KB）
        min_size_kb: 最小文件大小（KB）
    """
    extract_first_frames_from_dir(input_dir, output_dir, recursive)

    if compress:
        print(f"\n🔄 开始压缩转换提取的图片...")
        compress_images_to_webp(output_dir, output_dir, recursive, webp_quality, max_size_kb, min_size_kb)

        if recursive:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if not file.lower().endswith('.webp'):
                        os.remove(os.path.join(root, file))
        else:
            for file in os.listdir(output_dir):
                if not file.lower().endswith('.webp'):
                    os.remove(os.path.join(output_dir, file))

        print("🧹 已清理原始图片文件，只保留WebP格式")
