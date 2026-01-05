"""
视频基础操作模块
"""
import sys
import av


__version__ = "0.3.5"


def show_version():
    """显示版本和依赖信息"""
    import tqdm as tqdm_module
    from PIL import Image

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
