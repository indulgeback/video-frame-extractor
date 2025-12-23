# src/frame_extractor.py
import av
import argparse
import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import glob
from PIL import Image
import io

__version__ = "0.2.3"


def show_version():
    """显示版本和依赖信息"""
    import tqdm as tqdm_module
    print(f"video-frame-extractor: {__version__}")
    print(f"PyAV: {av.__version__}")
    print(f"Pillow: {Image.__version__}")
    print(f"tqdm: {tqdm_module.__version__}")
    print(f"Python: {sys.version.split()[0]}")


def get_video_info(video_path: str) -> dict:
    """
    获取视频信息
    
    参数:
        video_path: 视频文件路径
    返回:
        包含 fps, total_frames, width, height, duration 的字典
    """
    try:
        container = av.open(video_path)
        stream = container.streams.video[0]
        
        fps = float(stream.average_rate) if stream.average_rate else 0
        total_frames = stream.frames if stream.frames else 0
        duration = float(stream.duration * stream.time_base) if stream.duration else 0
        
        # 如果无法获取总帧数，通过时长和帧率计算
        if total_frames == 0 and fps > 0 and duration > 0:
            total_frames = int(duration * fps)
        
        info = {
            'fps': fps,
            'total_frames': total_frames,
            'width': stream.width,
            'height': stream.height,
            'duration': duration
        }
        container.close()
        return info
    except Exception as e:
        raise ValueError(f"无法读取视频信息: {video_path}\n{e}")


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



def compress_images_to_webp(input_dir: str, output_dir: str, recursive: bool = False, quality: int = 85,
                           max_size_kb: int = None, min_size_kb: int = None) -> None:
    """
    递归遍历目录中的图片，进行压缩并转换为WebP格式
    
    参数:
        input_dir: 输入图片目录
        output_dir: 输出WebP图片目录
        recursive: 是否递归遍历子目录
        quality: WebP压缩质量（0-100，默认85）
        max_size_kb: 最大文件大小（KB），如果超过会自动降低质量
        min_size_kb: 最小文件大小（KB），如果小于会自动提高质量
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    image_exts = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.tif", "*.gif", "*.webp"]
    image_files = []
    
    if recursive:
        for root, dirs, files in os.walk(input_dir):
            for ext in image_exts:
                pattern = os.path.join(root, ext)
                image_files.extend(glob.glob(pattern))
    else:
        for ext in image_exts:
            image_files.extend(glob.glob(os.path.join(input_dir, ext)))
    
    if not image_files:
        print(f"未找到图片文件: {input_dir}")
        return
    
    print(f"找到 {len(image_files)} 个图片文件")
    if max_size_kb:
        print(f"文件大小限制: 最大 {max_size_kb}KB" + (f", 最小 {min_size_kb}KB" if min_size_kb else ""))
    
    def process_single_image(image_path: str) -> tuple:
        """处理单个图片文件"""
        try:
            rel_path = os.path.relpath(image_path, input_dir)
            base = os.path.splitext(rel_path)[0]
            out_path = os.path.join(output_dir, f"{base}.webp")
            Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)
            
            with Image.open(image_path) as img:
                if img.mode == 'P':
                    img = img.convert('RGBA' if 'transparency' in img.info else 'RGB')
                elif img.mode == 'LA':
                    img = img.convert('RGBA')
                elif img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                
                if max_size_kb or min_size_kb:
                    current_quality = quality
                    attempts = 0
                    max_attempts = 20
                    
                    while attempts < max_attempts:
                        buffer = io.BytesIO()
                        img.save(buffer, 'WEBP', quality=current_quality, lossless=False)
                        file_size_kb = buffer.tell() / 1024
                        
                        too_large = max_size_kb and file_size_kb > max_size_kb
                        too_small = min_size_kb and file_size_kb < min_size_kb and current_quality < 95
                        
                        if not too_large and not too_small:
                            with open(out_path, 'wb') as f:
                                f.write(buffer.getvalue())
                            break
                        
                        if too_large:
                            if current_quality <= 10:
                                with open(out_path, 'wb') as f:
                                    f.write(buffer.getvalue())
                                break
                            current_quality = max(10, current_quality - 5)
                        elif too_small:
                            if current_quality >= 95:
                                with open(out_path, 'wb') as f:
                                    f.write(buffer.getvalue())
                                break
                            current_quality = min(95, current_quality + 5)
                        
                        attempts += 1
                    
                    file_size_info = f" ({file_size_kb:.1f}KB, quality={current_quality})"
                else:
                    img.save(out_path, 'WEBP', quality=quality, lossless=False)
                    file_size_kb = os.path.getsize(out_path) / 1024
                    file_size_info = f" ({file_size_kb:.1f}KB)"
            
            return True, rel_path, os.path.relpath(out_path, output_dir) + file_size_info
        except Exception as e:
            return False, rel_path, str(e)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        
        with tqdm(total=len(image_files), desc="压缩转换图片") as pbar:
            for image_path in image_files:
                future = executor.submit(process_single_image, image_path)
                futures.append(future)
            
            success_count = 0
            for future in futures:
                success, rel_path, result = future.result()
                if success:
                    print(f"✅ 已转换: {rel_path} -> {result}")
                    success_count += 1
                else:
                    print(f"❌ 跳过 {rel_path}: {result}")
                pbar.update(1)
    
    print(f"\n🎉 转换完成！成功转换 {success_count}/{len(image_files)} 个文件")



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


def main():
    parser = argparse.ArgumentParser(description="基于 PyAV 的命令行视频帧提取工具，支持单帧、批量、采样提取及视频信息查看。")
    parser.add_argument("-v", "--version", action="store_true", help="显示版本和依赖信息")
    subparsers = parser.add_subparsers(dest='command',
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
    dirfirst_parser.add_argument("-r", "--recursive", action="store_true", help="递归遍历子目录")
    dirfirst_parser.add_argument("-c", "--compress", action="store_true", help="压缩转换为WebP格式")
    dirfirst_parser.add_argument("--webp-quality", type=int, default=85, help="WebP压缩质量（0-100，默认85）")
    dirfirst_parser.add_argument("--max-size", type=int, default=100, help="最大文件大小（KB，默认100）")
    dirfirst_parser.add_argument("--min-size", type=int, default=50, help="最小文件大小（KB，默认50）")
    
    # 图片压缩转换命令
    compress_parser = subparsers.add_parser('compress', help="递归压缩目录中的图片为WebP格式")
    compress_parser.add_argument("-i", "--input_dir", required=True, help="输入图片目录")
    compress_parser.add_argument("-o", "--output_dir", required=True, help="输出WebP图片目录")
    compress_parser.add_argument("-r", "--recursive", action="store_true", help="递归遍历子目录")
    compress_parser.add_argument("-q", "--quality", type=int, default=85, help="WebP压缩质量（0-100，默认85）")
    compress_parser.add_argument("--max-size", type=int, default=100, help="最大文件大小（KB，默认100），超过会自动降低质量")
    compress_parser.add_argument("--min-size", type=int, default=50, help="最小文件大小（KB，默认50），小于会自动提高质量")

    args = parser.parse_args()
    
    try:
        if args.version:
            show_version()
            return
        
        if not args.command:
            parser.print_help()
            return
        
        if args.command == 'info':
            info = get_video_info(args.input)
            print(f"视频信息: {args.input}")
            print(f"  分辨率: {info['width']}x{info['height']}")
            print(f"  帧率: {info['fps']:.2f} FPS")
            print(f"  总帧数: {info['total_frames']}")
            print(f"  时长: {info['duration']:.2f} 秒")
            
        elif args.command == 'single':
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
            frame_nums = list(range(args.start, args.end + 1, args.delta))
            batch_extract(args.input, frame_nums, args.output, args.workers)
            
        elif args.command == 'sample':
            info = get_video_info(args.input)
            
            time_points = [i * args.interval for i in range(int(info['duration'] / args.interval) + 1)]
            frame_nums = [int(t * info['fps']) for t in time_points]
            frame_nums = [f for f in frame_nums if f < info['total_frames']]
            
            print(f"将从视频中按 {args.interval} 秒间隔采样 {len(frame_nums)} 帧")
            batch_extract(args.input, frame_nums, args.output, args.workers)
            
        elif args.command == 'dirfirst':
            max_size = getattr(args, 'max_size', None)
            min_size = getattr(args, 'min_size', None)
            extract_first_frames_with_compression(args.input_dir, args.output_dir, args.recursive,
                                                args.compress, args.webp_quality, max_size, min_size)
            
        elif args.command == 'compress':
            max_size = getattr(args, 'max_size', None)
            min_size = getattr(args, 'min_size', None)
            compress_images_to_webp(args.input_dir, args.output_dir, args.recursive, args.quality,
                                  max_size, min_size)
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
