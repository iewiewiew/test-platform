#!/usr/bin/env python3
"""
简单的图标生成脚本
使用 PIL/Pillow 创建扩展所需的图标文件
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("需要安装 Pillow 库: pip install Pillow")
    exit(1)

def create_icon(size, output_path):
    """创建指定尺寸的图标"""
    # 创建渐变背景
    img = Image.new('RGB', (size, size), color='#667eea')
    draw = ImageDraw.Draw(img)
    
    # 绘制渐变效果（简化版）
    for i in range(size):
        ratio = i / size
        r = int(102 + (118 - 102) * ratio)  # 667eea -> 764ba2
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        draw.line([(0, i), (size, i)], fill=(r, g, b))
    
    # 绘制 "T" 字母（表示 Test）
    font_size = int(size * 0.6)
    try:
        # macOS 系统字体
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        try:
            # Linux 系统字体
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            # 默认字体
            font = ImageFont.load_default()
    
    text = "T"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size - text_width) // 2, (size - text_height) // 2 - int(size * 0.05))
    
    # 绘制白色文字，带阴影效果
    shadow_offset = max(1, size // 32)
    draw.text((position[0] + shadow_offset, position[1] + shadow_offset), text, fill='#00000040', font=font)
    draw.text(position, text, fill='white', font=font)
    
    # 保存图标
    img.save(output_path, 'PNG')
    print(f"✓ 已创建 {output_path} ({size}x{size})")

def main():
    """主函数"""
    icons_dir = os.path.dirname(os.path.abspath(__file__))
    sizes = [16, 48, 128]
    
    print("正在生成图标文件...")
    for size in sizes:
        output_path = os.path.join(icons_dir, f'icon{size}.png')
        create_icon(size, output_path)
    
    print("\n✓ 所有图标已生成完成！")

if __name__ == '__main__':
    main()

