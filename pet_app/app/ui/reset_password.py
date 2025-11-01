# c:\SoftwareTask-main\app\reset_password.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
    QMessageBox, QDesktopWidget,QScrollArea,QSizePolicy,QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
import requests
import time

class ResetPasswordWindow(QWidget):
    """密码重置界面"""
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("智慧宠物管家 - 忘记密码")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # 创建UI
        self.create_ui()
        self.main_layout = self.layout()
        
        # 初始化计时器
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.remaining_time = 0
    
    def create_ui(self):
        """创建UI界面"""
        # 创建主容器widget
        container = QWidget()
        container.setStyleSheet("background-color: white;")
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 主布局
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # 标题
        title_label = QLabel("忘记密码")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("请输入您的注册邮箱，我们将发送验证码到该邮箱")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 14px; margin-bottom: 20px;")
        main_layout.addWidget(desc_label)
        
        # 邮箱输入
        self.email_label = QLabel("注册邮箱:")
        self.email_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(self.email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("请输入您的注册邮箱")
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
        
        # 验证码输入区域（默认隐藏）
        self.code_area = QWidget()
        code_layout = QVBoxLayout()
        code_layout.setContentsMargins(0, 0, 0, 0)
        
        self.verification_label = QLabel("验证码:")
        self.verification_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        code_layout.addWidget(self.verification_label)
        
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
        
        code_layout.addLayout(code_input_layout)
        self.code_area.setLayout(code_layout)
        self.code_area.setVisible(False)  # 默认隐藏
        main_layout.addWidget(self.code_area)
        
        # 新密码输入区域（默认隐藏）
        self.new_password_area = QWidget()
        new_password_layout = QVBoxLayout()
        new_password_layout.setContentsMargins(0, 0, 0, 0)
        
        self.new_password_label = QLabel("新密码:")
        self.new_password_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        new_password_layout.addWidget(self.new_password_label)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("请输入新密码（至少6位）")
        self.new_password_input.setEchoMode(QLineEdit.Password)
        self.new_password_input.setStyleSheet("""
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
        new_password_layout.addWidget(self.new_password_input)
        
        self.confirm_password_label = QLabel("确认新密码:")
        self.confirm_password_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        new_password_layout.addWidget(self.confirm_password_label)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("请再次输入新密码")
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
        new_password_layout.addWidget(self.confirm_password_input)
        
        self.new_password_area.setLayout(new_password_layout)
        self.new_password_area.setVisible(False)  # 默认隐藏
        main_layout.addWidget(self.new_password_area)
        
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
        
        self.verify_code_button = QPushButton("验证验证码")
        self.verify_code_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
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
        self.verify_code_button.clicked.connect(self.verify_code)
        self.verify_code_button.setVisible(False)  # 默认隐藏
        button_layout.addWidget(self.verify_code_button)
        
        self.reset_password_button = QPushButton("重置密码")
        self.reset_password_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.reset_password_button.clicked.connect(self.reset_password)
        self.reset_password_button.setVisible(False)  # 默认隐藏
        button_layout.addWidget(self.reset_password_button)
        
        main_layout.addLayout(button_layout)
        
        # 返回登录按钮
        back_layout = QVBoxLayout()
        back_button = QPushButton("返回登录")
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
        
        # 添加垂直弹簧保持顶部对齐
        main_layout.addStretch(1)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # 设置主窗口布局
        final_layout = QVBoxLayout(self)
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.setSpacing(0)
        final_layout.addWidget(scroll_area)
        final_layout.setStretch(0, 1)  # 让滚动区域占据所有可用空间
        self.setLayout(final_layout)

        # 调整窗口尺寸
        self.resize(450, 550)
        self.setMinimumSize(400, 450)
        
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
            # 发送请求
            response = requests.post(
                "http://127.0.0.1:8000/api/auth/forgot-password",
                data={"email": email}
            )
            
            if response.status_code == 200:
                # 显示验证码输入区域
                self.code_area.setVisible(True)
                self.verify_code_button.setVisible(True)
                
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
    
    def verify_code(self):
        """验证验证码"""
        email = self.email_input.text().strip()
        verification_code = self.verification_code_input.text().strip()
        
        # 验证输入
        if not verification_code:
            QMessageBox.warning(self, "输入错误", "请输入验证码")
            return
        
        try:
            # 这里只是验证格式，实际验证在重置密码时进行
            # 显示新密码输入区域
            self.new_password_area.setVisible(True)
            self.reset_password_button.setVisible(True)
            self.verify_code_button.setVisible(False)
            
            QMessageBox.information(self, "验证码验证", "验证码格式正确，请设置新密码")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"验证过程中出错: {str(e)}")
    
    def reset_password(self):
        """重置密码"""
        email = self.email_input.text().strip()
        verification_code = self.verification_code_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        # 验证输入
        if not verification_code:
            QMessageBox.warning(self, "输入错误", "请输入验证码")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "输入错误", "密码长度至少为6位")
            return
        
        if new_password != confirm_password:
            QMessageBox.warning(self, "输入错误", "两次输入的密码不一致")
            return
        
        try:
            # 发送重置请求
            response = requests.post(
                "http://127.0.0.1:8000/api/auth/reset-password",
                data={
                    "email": email,
                    "verification_code": verification_code,
                    "new_password": new_password,
                    "confirm_password": confirm_password
                }
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "重置成功", "密码重置成功，请使用新密码登录")
                self.go_back_to_login()
            else:
                error_msg = response.json().get("detail", "密码重置失败")
                QMessageBox.warning(self, "重置失败", error_msg)
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
        self.verification_code_input.clear()
        self.new_password_input.clear()
        self.confirm_password_input.clear()
        self.code_area.setVisible(False)
        self.new_password_area.setVisible(False)
        self.verify_code_button.setVisible(False)
        self.reset_password_button.setVisible(False)
        self.send_code_button.setEnabled(True)
        self.countdown_timer.stop()
        self.countdown_label.setText("")

    def showEvent(self, event):
        """窗口显示时自动重置界面"""
        self.reset_fields()
        super().showEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResetPasswordWindow()
    window.show()
    sys.exit(app.exec_())