# 向后兼容的公开API
from .core.video import get_video_info, show_version, __version__
from .core.extract import extract_frame, extract_by_time, batch_extract
from .core.directory import extract_first_frames_from_dir, extract_first_frames_with_compression
from .core.compression import compress_images_to_webp
from .core.video_compression import compress_video, compress_videos_in_dir
from .cli import main

# 为了兼容入口点 video_frame_extractor.frame_extractor:main
__all__ = [
    '__version__',
    'get_video_info',
    'show_version',
    'extract_frame',
    'extract_by_time',
    'batch_extract',
    'extract_first_frames_from_dir',
    'extract_first_frames_with_compression',
    'compress_images_to_webp',
    'compress_video',
    'compress_videos_in_dir',
    'main',
]
