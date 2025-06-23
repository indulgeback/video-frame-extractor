from setuptools import setup, find_packages

setup(
    name="video-frame-extractor",
    version="1.0.0",
    description="命令行视频帧提取工具",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "opencv-python",
        "tqdm",
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "frame-extractor=frame_extractor:main"
        ]
    },
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=False,
) 