from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class DashboardWindow(QWidget):
    """主仪表盘界面组件"""
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setup_ui()

    def showEvent(self, event):
        """当窗口显示时加载数据"""
        self.load_pets()
        super().showEvent(event)
    def setup_ui(self):
        """构建仪表盘UI"""
        layout = QVBoxLayout()
        
        # 顶部导航
        header = QWidget()
        header.setStyleSheet("background-color: #3498db; color: white; padding: 10px;")
        header_layout = QVBoxLayout(header)
        
        title = QLabel("智慧宠物管家")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # 宠物列表容器
        self.pet_container = QVBoxLayout()
        self.pet_container.setSpacing(15)
        
        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setLayout(self.pet_container)
        scroll.setWidget(scroll_content)
        
        layout.addWidget(scroll, 1)
        
        # 添加宠物按钮
        add_btn = QPushButton("+ 添加新宠物")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 16px;
                margin: 20px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        add_btn.clicked.connect(self.parent.show_add_pet)
        layout.addWidget(add_btn)
        
        self.setLayout(layout)
    
    def load_pets(self):
        """从API加载宠物列表"""
        # 检查token是否存在
        if not hasattr(self.parent, 'token') or not self.parent.token:
            return  # 没有token时不进行请求
        
        # 清空现有宠物
        while self.pet_container.count():
            child = self.pet_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        try:
            import requests
            response = requests.get(
                "http://127.0.0.1:8000/api/pets",
                headers={"Authorization": f"Bearer {self.parent.token}"}
            )
            
            if response.status_code == 200:
                pets = response.json()
                if not pets:
                    empty_label = QLabel("还没有添加宠物，点击下方按钮添加")
                    empty_label.setAlignment(Qt.AlignCenter)
                    empty_label.setStyleSheet("font-size: 16px; color: #7f8c8d;")
                    self.pet_container.addWidget(empty_label)
                else:
                    for pet in pets:
                        self.add_pet_card(pet)
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "加载失败", "无法加载宠物列表")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "连接错误", f"无法连接到服务: {str(e)}")
    
    def add_pet_card(self, pet):
        """创建单个宠物卡片"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                border: 1px solid #ecf0f1;
            }
            QFrame:hover {
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # 宠物信息
        name_label = QLabel(f"{pet['name']} ({pet['species']})")
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(name_label)
        
        if pet.get('breed'):
            layout.addWidget(QLabel(f"品种: {pet['breed']}"))
        if pet.get('sex'):
            layout.addWidget(QLabel(f"性别: {pet['sex']}"))
        if pet.get('birth_date'):
            layout.addWidget(QLabel(f"出生日期: {pet['birth_date']}"))
        
        # 操作按钮
        btn_layout = QVBoxLayout()
        
        health_btn = QPushButton("查看健康建议")
        health_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        health_btn.clicked.connect(lambda: self.show_health_advice(pet['species']))
        btn_layout.addWidget(health_btn)
        
        detail_btn = QPushButton("查看详情")
        detail_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        detail_btn.clicked.connect(lambda: self.parent.show_pet_detail(pet))
        btn_layout.addWidget(detail_btn)

        meal_plan_btn = QPushButton("食谱计划")
        meal_plan_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
        """)
        meal_plan_btn.clicked.connect(lambda: self.parent.show_meal_plan(pet))
        btn_layout.addWidget(meal_plan_btn)

        layout.addLayout(btn_layout)
        self.pet_container.addWidget(card)
    
    def show_health_advice(self, species):
        """获取并显示健康建议"""
        try:
            import requests
            response = requests.get(
                f"http://127.0.0.1:8000/api/health/advice/{species}"
            )
            
            if response.status_code == 200:
                advice = response.json()["advice"]
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, f"{species}健康建议", advice)
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "建议获取失败", "无法获取健康建议")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "连接错误", f"无法连接到服务: {str(e)}")

    def show_meal_plan(self, pet):
        """显示食谱计划界面"""
        try:
            # 导入MealPlanWindow（延迟导入避免循环依赖）
            from app.ui.meal_plan import MealPlanWindow
        
            # 移除旧的详情窗口（如果存在）
            if hasattr(self.parent, 'meal_plan_window') and self.parent.meal_plan_window:
                self.parent.removeWidget(self.parent.meal_plan_window)
                self.parent.meal_plan_window.deleteLater()
        
            # 创建新的详情窗口，传递宠物种类
            self.parent.meal_plan_window = MealPlanWindow(
               self.parent, 
               pet['id'], 
               pet['name'],
               pet['species']
            )
            self.parent.addWidget(self.parent.meal_plan_window)
            self.parent.setCurrentIndex(self.parent.count() - 1)
        except Exception as e:
            print(f"创建食谱计划界面失败: {str(e)}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "错误", f"无法创建食谱计划界面: {str(e)}")
