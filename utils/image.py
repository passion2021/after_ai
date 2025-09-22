#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/9/9 10:37
# @Author  : 李明轩
# @File    : image.py
from PIL import Image


def get_image_info(input_path: str):
    """
    获取图片信息（宽、高、像素数）
    """
    img = Image.open(input_path)
    width, height = img.size
    pixels = width * height
    print(f"原始尺寸: {width}x{height}, 总像素: {pixels}")
    return img, width, height, pixels


def process_image(input_path: str, output_path: str):
    """
    检查并调整图片尺寸以符合方舟新模型要求。
    条件：
      宽 > 14 且 高 > 14
      宽*高 ∈ [196, 36000000]
    """
    img, width, height, pixels = get_image_info(input_path)

    # 检查是否满足条件
    if width > 14 and height > 14 and 196 <= pixels <= 36000000:
        print("✅ 图片已符合要求")
        img.save(output_path)
        return

    # 如果宽或高小于等于14，则放大到15
    new_width = max(width, 15)
    new_height = max(height, 15)

    # 计算像素数是否在范围内
    new_pixels = new_width * new_height
    if new_pixels < 196:
        scale = (196 / new_pixels) ** 0.5
        new_width = int(new_width * scale) + 1
        new_height = int(new_height * scale) + 1
    elif new_pixels > 36000000:
        scale = (36000000 / new_pixels) ** 0.5
        new_width = int(new_width * scale)
        new_height = int(new_height * scale)

    # 调整图片
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    resized_img.save(output_path)

    print(f"修改后尺寸: {new_width}x{new_height}, 总像素: {new_width * new_height}")
    print("✅ 已保存修改后的图片")


if __name__ == '__main__':
    input_path = r"E:\after_ai\p1.png"
    get_image_info(input_path)
