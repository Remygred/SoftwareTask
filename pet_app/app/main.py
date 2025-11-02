import sys
import threading
import time
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from app.api_server import run_server  # 修正为相对导入
from app.ui.login import LoginWindow
from app.ui.dashboard import DashboardWindow
from app.ui.pet_detail import PetDetailWindow
from app.ui.register import RegisterWindow 
from app.ui.reset_password import ResetPasswordWindow
import traceback
import os

API_SERVER_ERROR = None
class MainWindow(QStackedWidget):
    """主窗口管理器，负责界面切换和状态管理"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智慧宠物管家")
        self.setFixedSize(600, 600)
        self.token = None  # 存储JWT令牌
        
        # 初始化所有UI组件
        self.login_window = LoginWindow(self)
        self.dashboard_window = DashboardWindow(self)
        self.register_window = RegisterWindow(self)  
        self.reset_password_window = ResetPasswordWindow(self)
        self.pet_detail_window = None  # 动态创建，避免重复添加
        self.meal_plan_window = None

        
        # 添加到堆栈
        self.addWidget(self.login_window)
        self.addWidget(self.dashboard_window)
        self.addWidget(self.register_window)  
        self.addWidget(self.reset_password_window)
        
        self.setCurrentWidget(self.login_window)
    
    def show_login(self):
        """显示登录界面"""
        self.setCurrentWidget(self.login_window)
    
    def show_dashboard(self):
        """显示主仪表盘"""
        self.dashboard_window.load_pets()
        self.setCurrentWidget(self.dashboard_window)
    
    def show_pet_detail(self, pet_data=None):
        """显示宠物详情界面（动态创建）"""
        # 移除旧的详情窗口（如果存在）
        if self.pet_detail_window:
            self.removeWidget(self.pet_detail_window)
            self.pet_detail_window.deleteLater()
        
        # 创建新的详情窗口
        self.pet_detail_window = PetDetailWindow(self, pet_data)
        self.addWidget(self.pet_detail_window)
        self.setCurrentIndex(self.count() - 1)
    
    def show_meal_plan(self, pet_data):
        """显示食谱计划界面"""
        # 移除旧的详情窗口（如果存在）
        if self.meal_plan_window:
            self.removeWidget(self.meal_plan_window)
            self.meal_plan_window.deleteLater()
    
        # 创建新的详情窗口
        from app.ui.meal_plan import MealPlanWindow
        self.meal_plan_window = MealPlanWindow(
            self, 
            pet_data['id'], 
            pet_data['name'],
            pet_data['species']
        )
        self.addWidget(self.meal_plan_window)
        self.setCurrentIndex(self.count() - 1)
    def show_add_pet(self):
        """显示添加宠物界面"""
        self.show_pet_detail()  # 无参数表示新建宠物

    # 添加显示注册窗口的方法
    def show_register(self):
        """显示注册界面"""
        self.setCurrentWidget(self.register_window)

    def show_reset_password(self):
        """显示重置密码界面"""
        self.setCurrentWidget(self.reset_password_window)

    

def get_database_url():
    """从环境变量获取数据库连接URL"""
    DB_HOST = os.getenv("DB_HOST", "rm-bp19kz85ye935j549po.mysql.rds.aliyuncs.com")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "petapp_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Lsm050401")
    DB_NAME = os.getenv("DB_NAME", "petapp_db")
    
    return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
def start_api_server():
    """在后台线程启动API服务器并捕获异常"""
    def run_server_safely():
        """安全包装的服务器启动函数"""
        global API_SERVER_ERROR
        try:
            # 在启动前测试数据库连接
            DATABASE_URL = get_database_url()
            print("🔍 测试数据库连接...")
            from sqlalchemy import create_engine
            engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 15})
            with engine.connect() as conn:
                print("✅ 数据库连接成功")
            run_server()
        except Exception as e:
            error_msg = f"API服务器启动失败: {str(e)}\n{traceback.format_exc()}"
            with open('api_server_error.log', 'w') as f:
                f.write(error_msg)
            API_SERVER_ERROR = error_msg
            print(f"❌ API服务器启动失败: {error_msg}")
    
    server_thread = threading.Thread(target=run_server_safely, daemon=True)
    server_thread.start()
    
    max_wait = 15
    waited = 0
    server_ready = False
    
    while waited < max_wait:
        time.sleep(1)
        if API_SERVER_ERROR:
            break
        try:
            response = requests.get("http://127.0.0.1:8000/api/health/advice/dog", timeout=1)
            if response.status_code == 200:
                print("✓ API服务器已启动并响应")
                server_ready = True
                break
        except:
            pass
        waited += 1
        print(f"⏳ 等待API服务器启动... ({waited}/{max_wait})")
    
    if not server_ready:
        if API_SERVER_ERROR:
            print(f"❌ API服务器启动失败: {API_SERVER_ERROR}")
        else:
            print("❌ API服务器启动超时，请检查端口8000是否被占用")
        sys.exit(1)  # 退出程序，此时还没有QApplication，所以不能使用QMessageBox

def main():
    # 启动API服务器
    start_api_server()
    
    # 创建Qt应用
    app = QApplication(sys.argv)
    
    # 设置全局样式
    app.setStyle("Fusion")

    app.setStyleSheet("""
        /* 全局字体和背景 */
        QWidget {
            font-family: "Microsoft YaHei", "Segoe UI", Arial, sans-serif;
            font-size: 11pt;
            background-color: #f5f7fa;
        }
        
        /* 按钮样式 */
        QPushButton {
            min-height: 36px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 10pt;
            padding: 5px 15px;
        }
        
        QPushButton:disabled {
            background-color: #e0e0e0;
            color: #a0a0a0;
        }
        
        /* 输入框样式 */
        QLineEdit {
            min-height: 32px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 5px 10px;
            font-size: 10.5pt;
            background-color: white;
        }
        
        QLineEdit:focus {
            border: 1px solid #3498db;
            background-color: #f8f9fa;
        }
        
        /* 标签样式 */
        QLabel {
            font-size: 10.5pt;
            color: #2c3e50;
        }
        
        /* 标题标签 */
        QLabel[heading="true"] {
            font-size: 18pt;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        /* 说明文本 */
        QLabel[description="true"] {
            font-size: 9.5pt;
            color: #7f8c8d;
            margin-bottom: 20px;
        }
        
        /* 验证码倒计时 */
        QLabel[countdown="true"] {
            color: #e74c3c;
            font-size: 9pt;
        }
        
        /* 链接样式 */
        QPushButton[link="true"] {
            background-color: transparent;
            border: none;
            color: #3498db;
            text-decoration: underline;
            font-weight: normal;
            padding: 0;
            min-height: auto;
            font-size: 10pt;
        }
        
        QPushButton[link="true"]:hover {
            color: #2980b9;
        }
        
        /* 主要操作按钮 */
        QPushButton[primary="true"] {
            background-color: #3498db;
            color: white;
            border: none;
        }
        
        QPushButton[primary="true"]:hover {
            background-color: #2980b9;
        }
        
        QPushButton[primary="true"]:pressed {
            background-color: #1c6ea4;
        }
        
        /* 次要操作按钮 */
        QPushButton[secondary="true"] {
            background-color: #2ecc71;
            color: white;
            border: none;
        }
        
        QPushButton[secondary="true"]:hover {
            background-color: #27ae60;
        }
        
        QPushButton[secondary="true"]:pressed {
            background-color: #1e8449;
        }
        
        /* 警示操作按钮 */
        QPushButton[danger="true"] {
            background-color: #e74c3c;
            color: white;
            border: none;
        }
        
        QPushButton[danger="true"]:hover {
            background-color: #c0392b;
        }
        
        QPushButton[danger="true"]:pressed {
            background-color: #a93226;
        }
        
        /* 容器样式 */
        QGroupBox {
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            margin-top: 1ex;
            background-color: white;
            padding: 15px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            font-weight: bold;
        }
    """)
    app.setFont(QFont("Microsoft YaHei", 10))
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("智慧宠物管家")
    window.resize(600, 600)
    
    # 设置中央部件为堆栈窗口
    main_window = MainWindow()
    window.setCentralWidget(main_window)
    
    # 显示窗口
    window.show()
    
    # 检查是否已存在管理员账号
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/auth/login",
            data={"email": "admin@petapp.com", "password": "admin123"}
        )
        if response.status_code == 200:
            print("测试账号已就绪: admin@petapp.com / admin123")
    except:
        print("等待API服务启动...")
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()