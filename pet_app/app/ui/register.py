import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QMessageBox, QDesktopWidget, QScrollArea
)
from PyQt5.QtCore import Qt,QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
import requests
import time

class RegisterWindow(QWidget):
    """注册界面"""
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("智慧宠物管家 - 注册")
        # 创建UI
        self.create_ui()


        
        # 初始化计时器
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.remaining_time = 0
    
    def create_ui(self):
        """创建UI界面"""

        container = QWidget()
        container.setStyleSheet("background-color: white;")  # 保持背景一致
        # 主布局
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)
        
        # 标题
        title_label = QLabel("创建新账户")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("请输入您的信息以创建新账户")
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
        
        # 昵称输入
        display_name_label = QLabel("昵称:")
        display_name_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(display_name_label)
        
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("请输入您的昵称")
        self.display_name_input.setStyleSheet("""
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
        main_layout.addWidget(self.display_name_input)
        
        # 密码输入
        password_label = QLabel("密码:")
        password_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码（至少6位）")
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
        
        # 确认密码
        confirm_password_label = QLabel("确认密码:")
        confirm_password_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(confirm_password_label)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("请再次输入密码")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setStyleSheet("""
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
        main_layout.addWidget(self.confirm_password_input)
        
        # 验证码输入区域
        verification_layout = QVBoxLayout()
        verification_layout.setContentsMargins(0, 0, 0, 0)
        
        self.verification_label = QLabel("验证码:")
        self.verification_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        verification_layout.addWidget(self.verification_label)
        
        code_input_layout = QVBoxLayout()
        code_input_layout.setSpacing(5)
        
        self.verification_code_input = QLineEdit()
        self.verification_code_input.setPlaceholderText("请输入收到的验证码")
        self.verification_code_input.setStyleSheet("""
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
        code_input_layout.addWidget(self.verification_code_input)
        
        # 验证码倒计时
        self.countdown_label = QLabel("")
        self.countdown_label.setStyleSheet("color: #e74c3c; font-size: 12px;")
        self.countdown_label.setAlignment(Qt.AlignRight)
        code_input_layout.addWidget(self.countdown_label)
        
        verification_layout.addLayout(code_input_layout)
        main_layout.addLayout(verification_layout)
        
        # 按钮区域
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        self.send_code_button = QPushButton("发送验证码")
        self.send_code_button.setStyleSheet("""
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
        self.send_code_button.clicked.connect(self.send_verification_code)
        button_layout.addWidget(self.send_code_button)
        
        self.register_button = QPushButton("注册")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.register_button.clicked.connect(self.register)
        button_layout.addWidget(self.register_button)
        
        main_layout.addLayout(button_layout)
        
        # 返回登录按钮
        back_layout = QVBoxLayout()
        back_button = QPushButton("已有账户? 返回登录")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                text-decoration: underline;
                padding: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        back_button.clicked.connect(self.go_back_to_login)
        back_layout.addWidget(back_button)
        main_layout.addLayout(back_layout)
        main_layout.addStretch(1)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁止水平滚动

        # 设置主窗口布局
        final_layout = QVBoxLayout()
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.addWidget(scroll_area)
        self.setLayout(final_layout)

        # 增加默认窗口尺寸
        self.resize(450, 650)
        self.setMinimumSize(400, 500)
        
        # 居中显示
        self.center()
    
    def center(self):
        """窗口居中显示"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def send_verification_code(self):
        """发送验证码"""
        email = self.email_input.text().strip()
        
        # 验证邮箱格式
        if not email or "@" not in email:
            QMessageBox.warning(self, "输入错误", "请输入有效的邮箱地址")
            return
        
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/auth/send-verification-code",
                data={"email": email}
            )
            
            if response.status_code == 200:
                # 禁用发送按钮，启动倒计时
                self.send_code_button.setEnabled(False)
                self.remaining_time = 60
                self.countdown_label.setText(f"请 {self.remaining_time} 秒后重试")
                self.countdown_timer.start(1000)
                
                QMessageBox.information(self, "验证码已发送", "验证码已发送至您的邮箱，请查收")
            else:
                error_msg = response.json().get("detail", "发送验证码失败")
                QMessageBox.warning(self, "发送失败", error_msg)
        except Exception as e:
            QMessageBox.critical(self, "网络错误", f"无法连接到服务器: {str(e)}")
    
    def update_countdown(self):
        """更新倒计时"""
        self.remaining_time -= 1
        if self.remaining_time <= 0:
            self.countdown_timer.stop()
            self.send_code_button.setEnabled(True)
            self.countdown_label.setText("")
        else:
            self.countdown_label.setText(f"请 {self.remaining_time} 秒后重试")
    
    def register(self):
        """处理注册逻辑"""
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        display_name = self.display_name_input.text()
        verification_code = self.verification_code_input.text()
        
        # 验证输入
        if not email or not password or not confirm_password or not display_name or not verification_code:
            QMessageBox.warning(self, "输入错误", "所有字段都必须填写")
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
            return
            
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/auth/register",
                data={ 
                    "email": email,
                    "password": password,
                    "display_name": display_name,
                    "verification_code": verification_code
                }
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "注册成功", "您的账户已成功创建，请登录")
                self.go_back_to_login()
            else:
                error_msg = response.json().get("detail", "注册失败")
                QMessageBox.warning(self, "注册失败", error_msg)
        except Exception as e:
            QMessageBox.critical(self, "网络错误", f"无法连接到服务器: {str(e)}")
    
    def go_back_to_login(self):
        """返回登录界面"""
        if self.main_window:
            self.main_window.show_login()
        self.close()

    def reset_fields(self):
        """重置所有输入字段和界面状态"""
        self.email_input.clear()
        self.display_name_input.clear() 
        self.password_input.clear()
        self.verification_code_input.clear()
        self.confirm_password_input.clear()
        self.send_code_button.setEnabled(True)
        self.countdown_timer.stop()
        self.countdown_label.setText("")
    def showEvent(self, event):
        """窗口显示时自动调整大小"""
        self.reset_fields()
        super().showEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec_())