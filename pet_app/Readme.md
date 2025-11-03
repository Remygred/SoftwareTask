智慧宠物管家
智慧宠物管家是一款桌面应用程序，帮助宠物主人管理宠物信息、查看健康建议并接收提醒。该应用采用前后端分离架构，前端使用 PyQt5 构建用户界面，后端使用 FastAPI 提供 REST API 服务。
项目结构
SoftwareTask-main/
├── app/                      # 主应用程序代码
│   ├── ui/                   # 用户界面组件
│   │   ├── __init__.py       # UI模块初始化
│   │   ├── dashboard.py      # 仪表盘界面
│   │   ├── login.py          # 登录界面
│   │   ├── pet_detail.py     # 宠物详情界面
│   │   ├── register.py       # 注册界面
│   │   └── reset_password.py # 密码重置界面
│   ├── __init__.py           # 应用初始化
│   ├── api_server.py         # FastAPI后端服务
│   └── main.py               # 应用入口，启动UI和API服务
├── hooks/                    # PyInstaller钩子文件
│   ├── hook-fastapi.py       # FastAPI打包钩子
│   └── hook-uvicorn.py       # Uvicorn打包钩子
├── upx/                      # UPX压缩工具相关
│   ├── README                # UPX说明文档
│   └── upx-doc.html          # UPX文档
├── build_app.py              # 打包脚本（使用PyInstaller）
└── requirements.txt          # 项目依赖

开发环境设置
1. 安装依赖
# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

开发与测试
启动开发环境
# 启动应用（开发模式）
python -m app.main

打包应用程序
1. 基本打包流程
# 清理旧构建
rmdir /s /q build dist

# 运行打包脚本
python build_app.py

2. 打包选项说明
图标设置：确保 assets/logo.ico 是有效的 ICO 文件（不是 PNG 重命名）
UPX 压缩：如果项目目录下有 upx/upx.exe，将自动启用压缩
无图标打包：修改 build_app.py，在第 60 行添加 icon_valid = False
禁用 UPX：修改 build_app.py，移除 --upx-dir 参数

3. 打包后运行
打包完成后，可执行文件位于：

dist/智慧宠物管家/智慧宠物管家.exe