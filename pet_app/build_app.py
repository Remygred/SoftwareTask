import os
import sys
import glob
from PyInstaller.__main__ import run

def validate_icon_file(icon_path):
    """
    验证图标文件是否为有效的ICO格式
    ICO文件的魔数是 00 00 01 00
    """
    if not os.path.exists(icon_path):
        print(f"❌ 图标文件不存在: {icon_path}")
        return False
    
    try:
        with open(icon_path, 'rb') as f:
            header = f.read(4)
            if header == b'\x00\x00\x01\x00':
                print(f"✓ 检测到有效的ICO文件: {icon_path}")
                return True
            else:
                print(f"❌ 检测到无效的ICO文件: {icon_path}")
                print("   提示: 可能是将PNG文件重命名为.ico，这会导致打包失败")
                print("   请使用真正的ICO格式文件（可使用在线转换工具）")
                return False
    except Exception as e:
        print(f"❌ 验证图标文件时出错: {str(e)}")
        return False

def get_data_files():
    """收集所有需要打包的资源文件"""
    data_files = []
    
    # 收集所有UI文件
    for ui_file in glob.glob('app/ui/*.py'):
        data_files.append((ui_file, 'app/ui'))
    
    # 收集所有静态资源
    for asset_file in glob.glob('assets/*'):
        if os.path.isfile(asset_file):
            data_files.append((asset_file, 'assets'))
    
    return data_files

def get_hidden_imports():
    """获取所有隐藏的导入"""
    return [
        'app',
        'app.api_server',
        'app.ui',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.protocols',
        'pymysql',  # 确保MySQL驱动被包含
        'passlib.handlers.bcrypt',
        'fastapi.security',
        'pydantic.json',
        'email.mime.text',
        'smtplib',
        'jinja2',
        'starlette',
        'websockets',
        'h11'
    ]

def main():
    # 检查图标文件
    icon_path = 'assets/logo.ico'
    icon_valid = validate_icon_file(icon_path)
    
    # 检查UPX是否存在
    upx_path = None
    possible_upx_paths = [
        'upx/upx.exe',
        'C:/upx/upx.exe',
        'C:/Program Files/upx/upx.exe'
    ]
    
    for path in possible_upx_paths:
        if os.path.exists(path):
            upx_path = os.path.dirname(path)
            print(f"✓ 找到UPX: {path}")
            break
    
    # 构建参数
    args = [
        'app/main.py',
        '--name=智慧宠物管家',
        '--windowed',  # 无控制台窗口
        '--clean',
        '--noconfirm',
        '--add-data=app/ui;app/ui',  # 包含UI文件
        '--add-data=assets;assets',  # 包含资源文件
    ]
    
    # 添加隐藏导入
    for imp in get_hidden_imports():
        args.append(f'--hidden-import={imp}')
    
    # 仅当图标有效时才添加图标参数
    if icon_valid:
        args.append(f'--icon={icon_path}')
        print(f"✓ 使用图标: {icon_path}")
    else:
        print("⚠️ 跳过图标设置（图标文件无效或不存在）")
        print("   提示: 打包完成后，您可以使用Resource Hacker等工具手动添加图标")
    
    # 添加UPX支持（如果找到）
    if upx_path:
        args.append(f'--upx-dir={upx_path}')
        print("✓ 启用UPX压缩")
    else:
        print("⚠️ 未找到UPX，打包文件将较大")
        print("   提示: 下载UPX (https://upx.github.io/) 并解压到项目目录的upx文件夹")
    
    print("\n" + "="*50)
    print("开始打包应用...")
    print(f"打包参数: {args}")
    print("="*50)
    
    # 运行PyInstaller
    try:
        print("尝试第一阶段打包（禁用UPX以避免资源错误）...")
        # 先尝试禁用UPX打包，解决UpdateResourceW问题
        no_upx_args = [arg for arg in args if not arg.startswith('--upx')]
        run(no_upx_args)
        
        # 如果第一阶段成功，尝试用UPX压缩（可选）
        if upx_path and os.path.exists('dist/智慧宠物管家/智慧宠物管家.exe'):
            print("\n第一阶段打包成功，尝试使用UPX压缩...")
            try:
                import subprocess
                upx_cmd = [
                    os.path.join(upx_path, 'upx.exe'),
                    '--force',  # 新增强制压缩参数（解决GUARD_CF问题）
                    '--best',
                    'dist/智慧宠物管家/智慧宠物管家.exe'
                ]
                subprocess.run(upx_cmd, check=True)
                print("✓ UPX压缩成功")
            except Exception as e:
                print(f"⚠️ UPX压缩失败: {str(e)}")
                print("   打包已完成，但文件未压缩")
        
        print("\n" + "="*50)
        print("打包成功完成！")
        print("可执行文件位于 dist/智慧宠物管家 目录")
        print(f"完整路径: {os.path.abspath('dist/智慧宠物管家')}")
        print("="*50)
        
        if not icon_valid:
            print("\n" + "="*50)
            print("重要提示: 由于图标问题，应用将使用默认图标")
            print("要添加图标，请:")
            print("1. 确保assets/logo.ico是真正的ICO格式（不是PNG重命名）")
            print("2. 使用在线ICO转换工具（如 https://www.icoconverter.com/）")
            print("3. 重新运行打包脚本")
            print("="*50)
        
    except Exception as e:
        print(f"\n❌ 打包过程中出错: {str(e)}")
        
        # 提供详细的故障排除建议
        print("\n" + "="*50)
        print("故障排除建议:")
        print("1. 验证图标文件是否为真正的ICO格式（不是PNG重命名）")
        print("   - 真正的ICO文件魔数应为 00 00 01 00")
        print("   - 可使用在线转换工具创建有效的ICO文件")
        print("2. 以管理员身份运行命令提示符")
        print("3. 更新PyInstaller: pip install --upgrade pyinstaller")
        print("4. 尝试完全禁用图标: 注释掉--icon参数")
        print("5. 如果问题仍然存在，尝试使用替代打包命令:")
        print("   pyinstaller app/main.py --name=智慧宠物管家 --windowed --clean")
        print("="*50)
        
        sys.exit(1)

if __name__ == "__main__":
    main()