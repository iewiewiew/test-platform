# 图标文件说明

扩展需要以下三个尺寸的图标文件：

- `icon16.png` - 16x16 像素（工具栏图标）
- `icon48.png` - 48x48 像素（扩展管理页面）
- `icon128.png` - 128x128 像素（Chrome Web Store）

## 快速创建图标

你可以使用以下方法创建图标：

### 方法一：使用在线工具
1. 访问 [Favicon Generator](https://www.favicon-generator.org/)
2. 上传你的图标图片
3. 下载不同尺寸的图标
4. 重命名并放置到本目录

### 方法二：使用 ImageMagick（如果已安装）
```bash
# 创建测试图标（需要先有一个源图标 source.png）
convert source.png -resize 16x16 icon16.png
convert source.png -resize 48x48 icon48.png
convert source.png -resize 128x128 icon128.png
```

### 方法三：使用 Python PIL/Pillow
```python
from PIL import Image, ImageDraw, ImageFont

# 创建简单的测试图标
sizes = [16, 48, 128]
for size in sizes:
    img = Image.new('RGB', (size, size), color='#667eea')
    draw = ImageDraw.Draw(img)
    # 绘制简单的 "T" 字母表示 Test
    font_size = int(size * 0.6)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()
    text = "T"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((size - text_width) // 2, (size - text_height) // 2)
    draw.text(position, text, fill='white', font=font)
    img.save(f'icon{size}.png')
```

### 临时解决方案
如果没有图标文件，扩展仍然可以工作，只是不会显示自定义图标。Chrome 会使用默认图标。

## 图标设计建议

- 使用简洁的设计，在小尺寸下也能清晰识别
- 建议使用与扩展主题相关的图标（如测试、数据等）
- 可以使用渐变背景色（#667eea 到 #764ba2）保持与 UI 一致






