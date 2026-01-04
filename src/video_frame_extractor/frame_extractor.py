# 兼容层：保持入口点 video_frame_extractor.frame_extractor:main 有效
from .cli import main

if __name__ == "__main__":
    main()
