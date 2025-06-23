import os
import cv2
import tempfile
import numpy as np
from src.frame_extractor import extract_frame

def test_extract_frame():
    # 创建临时视频文件
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, "test.mp4")
        output_path = os.path.join(tmpdir, "frame.jpg")
        
        # 生成测试视频（10帧）
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, 20.0, (640, 480))
        for _ in range(10):
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            out.write(frame)
        out.release()
        
        # 提取帧
        extract_frame(video_path, output_path, 5)
        
        # 验证输出文件
        assert os.path.exists(output_path)
        img = cv2.imread(output_path)
        assert img.shape == (480, 640, 3)