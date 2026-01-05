"""
视频压缩模块
使用 PyAV 对视频进行重新编码压缩
"""
import os
import glob
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import av


def compress_video(input_path: str, output_path: str, quality: int = 23) -> None:
    """
    压缩单个视频文件

    参数:
        input_path: 输入视频文件路径
        output_path: 输出视频文件路径
        quality: 压缩质量（0-100，值越小质量越高文件越大）
                 转换为 CRF: 0-100 -> 51-0 (反向映射)
                 默认 23 (CRF约28, 中等质量)
    """
    # 创建输出目录
    output_dir = os.path.dirname(output_path)
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 将 0-100 的质量值转换为 CRF 值 (0-51)
    # quality 越小，CRF 越大（压缩越厉害）
    # quality=100 -> CRF=0 (无损/最高质量)
    # quality=50 -> CRF=23 (默认/中等)
    # quality=0 -> CRF=51 (最低质量/最大压缩)
    crf = int(51 * (100 - quality) / 100)

    try:
        # 打开输入视频
        input_container = av.open(input_path)
        input_video_stream = input_container.streams.video[0]
        input_audio_streams = input_container.streams.audio

        # 创建输出视频
        output_container = av.open(output_path, 'w')

        # 添加视频流，使用输入视频的帧率
        input_fps = input_video_stream.guessed_rate
        output_video_stream = output_container.add_stream('libx264', rate=input_fps)

        # 设置编码参数
        output_video_stream.width = input_video_stream.width
        output_video_stream.height = input_video_stream.height
        output_video_stream.pix_fmt = 'yuv420p'

        # 设置 CRF 值控制质量
        output_video_stream.codec_context.options = {
            'crf': str(crf),
            'preset': 'medium',  # 编码速度预设
        }

        # 如果有音频流，复制音频
        output_audio_streams = []
        for audio_stream in input_audio_streams:
            # PyAV 16+ 不支持 template 参数，需要手动指定 codec
            audio_codec = audio_stream.codec_context.name
            output_audio_stream = output_container.add_stream(audio_codec)
            # 复制音频编码参数
            output_audio_stream.sample_rate = audio_stream.sample_rate
            output_audio_stream.layout = audio_stream.layout
            output_audio_streams.append((audio_stream, output_audio_stream))

        # 获取输入视频的平均码率，用于预估
        input_bitrate = getattr(input_video_stream, 'bit_rate', None)
        if input_bitrate:
            input_bitrate_kb = input_bitrate / 1000

        # 编码视频帧
        for packet in input_container.demux(input_video_stream):
            for frame in packet.decode():
                for output_packet in output_video_stream.encode(frame):
                    output_container.mux(output_packet)

        # 刷新编码器
        for output_packet in output_video_stream.encode():
            output_container.mux(output_packet)

        # 处理音频流
        for input_audio, output_audio in output_audio_streams:
            for packet in input_container.demux(input_audio):
                output_container.mux(packet)

        # 获取输出视频信息
        output_video_stream = output_container.streams.video[0]
        output_bitrate = getattr(output_video_stream, 'bit_rate', None)
        if output_bitrate:
            output_bitrate_kb = output_bitrate / 1000

        input_container.close()
        output_container.close()

        # 获取文件大小
        input_size = os.path.getsize(input_path) / 1024 / 1024  # MB
        output_size = os.path.getsize(output_path) / 1024 / 1024  # MB
        compression_ratio = (1 - output_size / input_size) * 100 if input_size > 0 else 0

        return True, {
            'input_size': input_size,
            'output_size': output_size,
            'compression_ratio': compression_ratio,
        }

    except Exception as e:
        # 清理失败的输出文件
        if os.path.exists(output_path):
            os.remove(output_path)
        raise ValueError(f"视频压缩失败: {e}")


def compress_videos_in_dir(input_dir: str, output_dir: str, recursive: bool = False,
                           quality: int = 23, max_workers: int = 2) -> None:
    """
    批量压缩目录中的视频文件

    参数:
        input_dir: 输入视频目录
        output_dir: 输出视频目录
        recursive: 是否递归遍历子目录
        quality: 压缩质量（0-100，默认23）
        max_workers: 最大工作线程数（视频编码消耗资源，默认2）
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 支持的视频格式
    video_exts = ["*.mp4", "*.avi", "*.mov", "*.mkv", "*.flv", "*.wmv", "*.m4v", "*.webm"]
    video_files = []

    if recursive:
        for root, dirs, files in os.walk(input_dir):
            for ext in video_exts:
                pattern = os.path.join(root, ext)
                video_files.extend(glob.glob(pattern))
    else:
        for ext in video_exts:
            video_files.extend(glob.glob(os.path.join(input_dir, ext)))

    if not video_files:
        print(f"未找到视频文件: {input_dir}")
        return

    print(f"找到 {len(video_files)} 个视频文件")
    print(f"压缩质量: {quality} (CRF ≈ {int(51 * (100 - quality) / 100)})")

    def process_single_video(video_path: str) -> tuple:
        """处理单个视频文件"""
        try:
            rel_path = os.path.relpath(video_path, input_dir)
            base = os.path.splitext(rel_path)[0]
            out_path = os.path.join(output_dir, f"{base}.mp4")
            Path(os.path.dirname(out_path)).mkdir(parents=True, exist_ok=True)

            success, info = compress_video(video_path, out_path, quality)

            if success:
                size_info = (f" {info['input_size']:.1f}MB -> "
                           f"{info['output_size']:.1f}MB "
                           f"(-{info['compression_ratio']:.1f}%)")
                return True, rel_path, os.path.relpath(out_path, output_dir) + size_info
            else:
                return False, rel_path, "压缩失败"
        except Exception as e:
            return False, rel_path, str(e)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        with tqdm(total=len(video_files), desc="压缩视频") as pbar:
            for video_path in video_files:
                future = executor.submit(process_single_video, video_path)
                futures.append(future)

            success_count = 0
            for future in futures:
                success, rel_path, result = future.result()
                if success:
                    print(f"✅ 已压缩: {rel_path} -> {result}")
                    success_count += 1
                else:
                    print(f"❌ 跳过 {rel_path}: {result}")
                pbar.update(1)

    print(f"\n🎉 压缩完成！成功压缩 {success_count}/{len(video_files)} 个文件")
