"""
命令行接口模块
"""
import sys
import argparse
import os

from .core.video import get_video_info, show_version
from .core.extract import extract_frame, extract_by_time, batch_extract
from .core.directory import extract_first_frames_with_compression
from .core.compression import compress_images_to_webp
from .core.video_compression import compress_video, compress_videos_in_dir


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

    # 视频压缩命令
    vcompress_parser = subparsers.add_parser('vcompress', help="压缩视频文件")
    vcompress_parser.add_argument("-i", "--input", required=True, help="输入视频路径或目录")
    vcompress_parser.add_argument("-o", "--output", required=True, help="输出视频路径或目录")
    vcompress_parser.add_argument("-r", "--recursive", action="store_true", help="递归遍历子目录（当输入为目录时）")
    vcompress_parser.add_argument("-q", "--quality", type=int, default=50, help="压缩质量（0-100，默认50，值越小压缩率越高）")
    vcompress_parser.add_argument("-w", "--workers", type=int, default=2, help="工作线程数（默认2）")

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

        elif args.command == 'vcompress':
            if os.path.isfile(args.input):
                # 单个视频文件压缩
                success, info = compress_video(args.input, args.output, args.quality)
                if success:
                    print(f"✅ 压缩完成: {info['input_size']:.1f}MB -> {info['output_size']:.1f}MB (-{info['compression_ratio']:.1f}%)")
            else:
                # 目录批量压缩
                compress_videos_in_dir(args.input, args.output, args.recursive, args.quality, args.workers)

    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
