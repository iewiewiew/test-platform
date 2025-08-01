# Chrome 扩展目录

本目录存放 Chrome 浏览器扩展项目。

## 当前扩展

### test-data-generator

测试数据生成器 Chrome 扩展，用于快速生成各种测试数据（身份证、手机号、邮箱等）。

**安装路径**: `backend/chrome/test-data-generator`

详细说明请查看 [test-data-generator/README.md](./test-data-generator/README.md)

## 目录结构

```
chrome/
├── test-data-generator/    # 测试数据生成器扩展
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.js
│   ├── popup.css
│   ├── create_icons.py
│   ├── icons/
│   └── README.md
└── README.md               # 本文件
```

## 添加新扩展

如需添加新的 Chrome 扩展，请在此目录下创建新的子目录，并遵循以下命名规范：

- 使用小写字母和连字符（kebab-case）
- 名称应清晰描述扩展的功能
- 例如：`api-tester`, `mock-server`, `data-validator`
