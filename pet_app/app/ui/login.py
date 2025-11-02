# c:\SoftwareTask-main\app\login.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QMessageBox, QStackedWidget, QHBoxLayout, QDesktopWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import requests

class LoginWindow(QWidget):
    """登录界面"""
    
    def __init__(self,main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("智慧宠物管家 - 登录")
        self.setMinimumSize(600, 550)
        self.resize(600, 550)
        
        # 创建UI
        self.create_ui()
    
    def create_ui(self):
        """创建UI界面"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 标题
        title_label = QLabel("智慧宠物管家")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("登录您的账户以管理宠物信息")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 20px;")
        main_layout.addWidget(desc_label)
        
        # 邮箱输入
        email_label = QLabel("邮箱:")
        email_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("请输入您的邮箱")
        self.email_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        main_layout.addWidget(self.email_input)
        
        # 密码输入
        password_label = QLabel("密码:")
        password_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入您的密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        main_layout.addWidget(self.password_input)
        
        # 忘记密码链接
        forgot_layout = QHBoxLayout()
        forgot_layout.addStretch()
        
        forgot_password_btn = QPushButton("忘记密码?")
        forgot_password_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                text-decoration: underline;
                padding: 0;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        forgot_password_btn.clicked.connect(self.show_forgot_password)
        forgot_layout.addWidget(forgot_password_btn)
        
        main_layout.addLayout(forgot_layout)
        
        # 登录按钮
        self.login_button = QPushButton("登录")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        self.login_button.clicked.connect(self.login)
        main_layout.addWidget(self.login_button)
        
        # 注册按钮
        register_btn = QPushButton("还没有账户? 立即注册")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
            }
        """)
        register_btn.clicked.connect(self.show_register)
        main_layout.addWidget(register_btn)
        
        # 设置主布局
        self.setLayout(main_layout)
        
        # 居中显示
        self.center()
    
    def center(self):
        """窗口居中显示"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def login(self):
        """处理登录逻辑"""
        email = self.email_input.text()
        password = self.password_input.text()
        
        # 验证输入
        if not email or not password:
            QMessageBox.warning(self, "输入错误", "邮箱和密码不能为空")
            return
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/auth/login",
                data={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                # 登录成功，跳转到主界面
                QMessageBox.information(self, "登录成功", "欢迎使用智慧宠物管家!")
                self.main_window.token = response.json()["access_token"]
                self.main_window.show_dashboard()
            else:
                error_msg = response.json().get("detail", "登录失败")
                QMessageBox.warning(self, "登录失败", error_msg)
        except Exception as e:
            QMessageBox.critical(self, "网络错误", f"无法连接到服务器: {str(e)}")

    
    def show_register(self):
        """显示注册界面"""
        # 这里应该显示注册界面
        self.main_window.show_register()
    
    def show_forgot_password(self):
        """显示忘记密码界面"""
        self.main_window.show_reset_password()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())