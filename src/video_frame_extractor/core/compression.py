"""
图片压缩和格式转换模块
"""
import os
import glob
import io
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from PIL import Image


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
