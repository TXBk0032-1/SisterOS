"""
图像处理工具模块
提供图像处理相关的工具函数
"""

import os
from typing import Tuple, Optional

from PIL import Image, ImageTk


class AvatarCropper:
    """头像裁剪器"""
    
    def __init__(self):
        self.crop_size = (200, 200)
    
    def crop_to_circle(self, image_path: str, output_path: str = None) -> Optional[str]:
        """
        将图片裁剪为圆形头像
        """
        try:
            # 打开图片
            image = Image.open(image_path)
            
            # 转换为RGBA模式
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # 裁剪为正方形
            width, height = image.size
            size = min(width, height)
            left = (width - size) // 2
            top = (height - size) // 2
            image = image.crop((left, top, left + size, top + size))
            
            # 调整大小
            image = image.resize(self.crop_size, Image.Resampling.LANCZOS)
            
            # 创建圆形蒙版
            mask = Image.new('L', self.crop_size, 0)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, self.crop_size[0], self.crop_size[1]), fill=255)
            
            # 应用蒙版
            output = Image.new('RGBA', self.crop_size, (0, 0, 0, 0))
            output.paste(image, (0, 0))
            output.putalpha(mask)
            
            # 保存图片
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_avatar.png"
            
            output.save(output_path, 'PNG')
            return output_path
            
        except Exception as e:
            print(f"图片裁剪失败: {e}")
            return None
    
    def resize_image(self, image_path: str, size: Tuple[int, int], 
                    output_path: str = None) -> Optional[str]:
        """
        调整图片大小
        """
        try:
            image = Image.open(image_path)
            image = image.resize(size, Image.Resampling.LANCZOS)
            
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_resized{ext}"
            
            image.save(output_path)
            return output_path
            
        except Exception as e:
            print(f"图片大小调整失败: {e}")
            return None


def create_thumbnail(image_path: str, size: Tuple[int, int] = (100, 100)) -> Optional[ImageTk.PhotoImage]:
    """
    创建图片缩略图
    """
    try:
        image = Image.open(image_path)
        image.thumbnail(size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"创建缩略图失败: {e}")
        return None


def load_image_for_tkinter(image_path: str) -> Optional[ImageTk.PhotoImage]:
    """
    加载图片用于Tkinter显示
    """
    try:
        image = Image.open(image_path)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        print(f"加载图片失败: {e}")
        return None


def convert_to_grayscale(image_path: str, output_path: str = None) -> Optional[str]:
    """
    转换为灰度图
    """
    try:
        image = Image.open(image_path)
        gray_image = image.convert('L')
        
        if output_path is None:
            name, ext = os.path.splitext(image_path)
            output_path = f"{name}_gray{ext}"
        
        gray_image.save(output_path)
        return output_path
        
    except Exception as e:
        print(f"转换为灰度图失败: {e}")
        return None