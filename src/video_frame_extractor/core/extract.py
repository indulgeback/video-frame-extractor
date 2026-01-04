"""
核心帧提取模块
"""
import os
import av
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from .video import get_video_info


def extract_frame(video_path: str, output_path: str, frame_number: int = 0,
                  progress_callback=None) -> None:
    """
    从视频中提取指定帧并保存为图像

    参数:
        video_path: 输入视频文件路径
        output_path: 输出图像文件路径
        frame_number: 要提取的帧号
        progress_callback: 进度回调函数
    """
    info = get_video_info(video_path)

    if info['total_frames'] > 0 and frame_number >= info['total_frames']:
        raise ValueError(f"帧号 {frame_number} 超出范围 (总帧数: {info['total_frames']})")

    # 创建输出目录
    output_dir = os.path.dirname(output_path)
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        container = av.open(video_path)
        stream = container.streams.video[0]

        # 计算目标时间戳并 seek
        if info['fps'] > 0:
            target_time = frame_number / info['fps']
            # 转换为流的时间基准
            target_pts = int(target_time / stream.time_base)
            container.seek(target_pts, stream=stream)

        # 解码帧
        current_frame = 0
        for frame in container.decode(video=0):
            if current_frame == 0:  # seek 后的第一帧
                img = frame.to_image()
                img.save(output_path, quality=95)
                break
            current_frame += 1

        container.close()
    except Exception as e:
        raise ValueError(f"提取帧失败: {e}")

    if progress_callback:
        progress_callback(frame_number, info['total_frames'])


def batch_extract(video_path: str, frame_nums: list, output_dir: str,
                  max_workers: int = 4) -> None:
    """
    批量提取多个帧（支持多线程）

    参数:
        video_path: 输入视频文件路径
        frame_nums: 要提取的帧号列表
        output_dir: 输出目录
        max_workers: 最大工作线程数
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    output_paths = [
        os.path.join(output_dir, f"frame_{frame_num}.jpg")
        for frame_num in frame_nums
    ]

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        with tqdm(total=len(frame_nums), desc="提取帧") as pbar:
            def update_progress(current, total):
                pbar.update(1)

            for frame_num, output_path in zip(frame_nums, output_paths):
                future = executor.submit(
                    extract_frame,
                    video_path,
                    output_path,
                    frame_num,
                    update_progress if max_workers == 1 else None
                )
                futures.append(future)

            for future in futures:
                future.result()
                if max_workers > 1:
                    pbar.update(1)


def extract_by_time(video_path: str, output_path: str, time_sec: float) -> None:
    """
    根据时间点提取帧

    参数:
        video_path: 输入视频文件路径
        output_path: 输出图像文件路径
        time_sec: 时间点（秒）
    """
    output_dir = os.path.dirname(output_path)
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        container = av.open(video_path)
        stream = container.streams.video[0]

        # 转换为流的时间基准并 seek
        target_pts = int(time_sec / stream.time_base)
        container.seek(target_pts, stream=stream)

        # 解码第一帧
        for frame in container.decode(video=0):
            img = frame.to_image()
            img.save(output_path, quality=95)
            break

        container.close()

        info = get_video_info(video_path)
        frame_number = int(time_sec * info['fps'])
        print(f"✅ 在时间点 {time_sec:.2f}s 提取第 {frame_number} 帧")
    except Exception as e:
        raise ValueError(f"提取帧失败: {e}")
