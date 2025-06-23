# src/frame_extractor.py
import cv2
import argparse
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import glob

def extract_frame(video_path: str, output_path: str, frame_number: int = 0, 
                  progress_callback=None) -> None:
    """
    从视频中提取指定帧并保存为图像
    
    参数:
        video_path: 输入视频文件路径
        output_path: 输出图像文件路径
        frame_number: 要提取的帧号
        progress_callback: 进度回调函数，用于显示进度
    """
    # 兼容中文路径
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"无法打开视频文件: {video_path}")
    
    # 获取视频元信息
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    # 验证帧号
    if frame_number >= total_frames:
        cap.release()
        raise ValueError(f"帧号 {frame_number} 超出范围 (总帧数: {total_frames})")
    
    # 设置读取位置
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    # 读取帧
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError(f"无法读取帧 {frame_number}")
    
    # 创建输出目录
    output_dir = os.path.dirname(output_path)
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 保存帧
    cv2.imwrite(output_path, frame)
    
    # 回调进度
    if progress_callback:
        progress_callback(frame_number, total_frames)

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
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 生成输出路径列表
    output_paths = [
        os.path.join(output_dir, f"frame_{frame_num}.jpg")
        for frame_num in frame_nums
    ]
    
    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        
        # 创建进度条
        with tqdm(total=len(frame_nums), desc="提取帧") as pbar:
            # 更新进度的回调函数
            def update_progress(current, total):
                pbar.update(1)
            
            # 提交所有任务
            for frame_num, output_path in zip(frame_nums, output_paths):
                future = executor.submit(
                    extract_frame, 
                    video_path, 
                    output_path, 
                    frame_num,
                    update_progress if max_workers == 1 else None
                )
                futures.append(future)
            
            # 等待所有任务完成
            for future in futures:
                future.result()  # 获取结果，抛出可能的异常

def extract_by_time(video_path: str, output_path: str, time_sec: float) -> None:
    """
    根据时间点提取帧
    
    参数:
        video_path: 输入视频文件路径
        output_path: 输出图像文件路径
        time_sec: 时间点（秒）
    """
    # 打开视频获取FPS
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"无法打开视频文件: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    
    if fps <= 0:
        raise ValueError("无法获取视频帧率")
    
    # 计算对应的帧号
    frame_number = int(time_sec * fps)
    
    # 提取帧
    extract_frame(video_path, output_path, frame_number)
    print(f"✅ 在时间点 {time_sec:.2f}s 提取第 {frame_number} 帧")

def extract_first_frames_from_dir(input_dir: str, output_dir: str) -> None:
    """
    批量提取目录下所有视频的首帧，输出到指定目录，图片文件名与原视频名一致。
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    # 支持常见视频格式
    exts = ["*.mp4", "*.avi", "*.mov", "*.mkv", "*.flv", "*.wmv"]
    video_files = []
    for ext in exts:
        video_files.extend(glob.glob(os.path.join(input_dir, ext)))
    if not video_files:
        print(f"未找到视频文件: {input_dir}")
        return
    for video_path in video_files:
        base = os.path.splitext(os.path.basename(video_path))[0]
        out_path = os.path.join(output_dir, f"{base}.jpg")
        try:
            extract_frame(video_path, out_path, 0)
            print(f"已提取: {video_path} -> {out_path}")
        except Exception as e:
            print(f"跳过 {video_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="基于 OpenCV 的命令行视频帧提取工具，支持单帧、批量、采样提取及视频信息查看。")
    subparsers = parser.add_subparsers(dest='command', required=True, 
                                        help="可用命令")
    
    # 单帧提取命令
    single_parser = subparsers.add_parser('single', help="提取单帧")
    single_parser.add_argument("-i", "--input", required=True, help="输入视频路径")
    single_parser.add_argument("-o", "--output", help="输出图像路径")
    group = single_parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--frame", type=int, help="要提取的帧号")
    group.add_argument("-t", "--time", type=float, help="要提取的时间点（秒）")
    single_parser.add_argument("--quality", type=int, default=95, 
                              help="JPEG质量（0-100，默认95）")
    
    # 批量提取命令
    batch_parser = subparsers.add_parser('batch', help="批量提取多帧")
    batch_parser.add_argument("-i", "--input", required=True, help="输入视频路径")
    batch_parser.add_argument("-o", "--output", required=True, help="输出目录")
    batch_parser.add_argument("-s", "--start", type=int, required=True, 
                             help="起始帧号")
    batch_parser.add_argument("-e", "--end", type=int, required=True, 
                             help="结束帧号")
    batch_parser.add_argument("-d", "--delta", type=int, default=1, 
                             help="帧间隔（默认1）")
    batch_parser.add_argument("-w", "--workers", type=int, default=4, 
                             help="工作线程数（默认4）")
    
    # 采样提取命令
    sample_parser = subparsers.add_parser('sample', help="按时间间隔采样提取")
    sample_parser.add_argument("-i", "--input", required=True, help="输入视频路径")
    sample_parser.add_argument("-o", "--output", required=True, help="输出目录")
    sample_parser.add_argument("-t", "--interval", type=float, default=1.0, 
                              help="采样间隔（秒，默认1.0）")
    sample_parser.add_argument("-w", "--workers", type=int, default=4, 
                              help="工作线程数（默认4）")
    
    # 信息命令
    info_parser = subparsers.add_parser('info', help="显示视频信息")
    info_parser.add_argument("-i", "--input", required=True, help="输入视频路径")
    
    # 批量目录首帧命令
    dirfirst_parser = subparsers.add_parser('dirfirst', help="批量提取目录下所有视频的首帧")
    dirfirst_parser.add_argument("-i", "--input_dir", required=True, help="输入视频目录")
    dirfirst_parser.add_argument("-o", "--output_dir", required=True, help="输出图片目录")
    
    args = parser.parse_args()
    
    try:
        if args.command == 'info':
            # 显示视频信息
            cap = cv2.VideoCapture(args.input)
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {args.input}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            cap.release()
            
            print(f"视频信息: {args.input}")
            print(f"  分辨率: {width}x{height}")
            print(f"  帧率: {fps:.2f} FPS")
            print(f"  总帧数: {total_frames}")
            print(f"  时长: {duration:.2f} 秒")
            
        elif args.command == 'single':
            # 单帧提取
            if args.output is None:
                base_name = os.path.splitext(os.path.basename(args.input))[0]
                if args.frame is not None:
                    args.output = f"{base_name}_frame_{args.frame}.jpg"
                else:
                    args.output = f"{base_name}_time_{args.time:.2f}s.jpg"
            
            if args.frame is not None:
                extract_frame(args.input, args.output, args.frame)
            else:
                extract_by_time(args.input, args.output, args.time)
            
        elif args.command == 'batch':
            # 批量提取
            frame_nums = list(range(args.start, args.end + 1, args.delta))
            batch_extract(args.input, frame_nums, args.output, args.workers)
            
        elif args.command == 'sample':
            # 按时间间隔采样
            cap = cv2.VideoCapture(args.input)
            if not cap.isOpened():
                raise ValueError(f"无法打开视频文件: {args.input}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            cap.release()
            
            # 计算要提取的时间点和对应的帧号
            time_points = [i * args.interval for i in range(int(duration / args.interval) + 1)]
            frame_nums = [int(t * fps) for t in time_points]
            
            # 确保不超过最大帧号
            frame_nums = [f for f in frame_nums if f < total_frames]
            
            print(f"将从视频中按 {args.interval} 秒间隔采样 {len(frame_nums)} 帧")
            batch_extract(args.input, frame_nums, args.output, args.workers)
            
        elif args.command == 'dirfirst':
            extract_first_frames_from_dir(args.input_dir, args.output_dir)
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()