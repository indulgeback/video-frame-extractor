from setuptools import setup, find_packages

setup(
    name="video-frame-extractor",
    version="0.1.0-beta",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],  # 如有依赖请补充
    entry_points={
        "console_scripts": [
            "frame-extractor=video_frame_extractor.frame_extractor:main"
        ]
    },
    author="LeviLiu",
    description="一个用于提取视频帧的命令行工具",
    url="https://github.com/indulgeback/video-frame-extractor",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
) 