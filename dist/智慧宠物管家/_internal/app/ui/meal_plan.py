from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFormLayout, QTextEdit,QHBoxLayout,QScrollArea,QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class MealPlanWindow(QWidget):
    """食谱计划界面组件"""
    
    def __init__(self, parent, pet_id, pet_name, species):
        """
        Args:
            parent: 主窗口
            pet_id: 宠物ID
            pet_name: 宠物名称
            species: 宠物种类
        """
        super().__init__()
        self.parent = parent
        self.pet_id = pet_id
        self.pet_name = pet_name
        self.species = species
        self.meal_plan = None
        self.feeding_record = None
        self.setup_ui()
        self.load_recommendation()
        self.load_meal_plan()
        self.load_feeding_record()
    
    def setup_ui(self):
        """构建食谱计划UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        # 创建滚动内容
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # 标题
        self.title = QLabel(f"{self.pet_name}的食谱计划")
        self.title.setFont(QFont("Arial", 20, QFont.Bold))
        self.title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self.title)
        
        # 表单
        form = QFormLayout()
        form.setSpacing(15)
        
        # 早餐
        breakfast_layout = QHBoxLayout()
        self.breakfast_input = QTextEdit()
        self.breakfast_input.setPlaceholderText("请输入早餐内容...")
        self.breakfast_input.setMinimumHeight(35)
        self.breakfast_input.setMaximumHeight(70)
        breakfast_layout.addWidget(self.breakfast_input, 1)
        
        # 早餐打卡按钮
        self.breakfast_check_btn = QPushButton("打卡")
        self.breakfast_check_btn.setFixedWidth(60)
        self.breakfast_check_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.breakfast_check_btn.clicked.connect(lambda: self.toggle_meal_check("breakfast"))
        breakfast_layout.addWidget(self.breakfast_check_btn)
        
        form.addRow("早餐:", breakfast_layout)
        
        # 早餐打卡状态
        self.breakfast_status = QLabel("")
        self.breakfast_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
        form.addRow("", self.breakfast_status)
        
        # 早餐推荐
        self.breakfast_recommendation = QLabel("")
        self.breakfast_recommendation.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        self.breakfast_recommendation.setWordWrap(True)
        form.addRow("", self.breakfast_recommendation)
        
        # 午餐
        lunch_layout = QHBoxLayout()
        self.lunch_input = QTextEdit()
        self.lunch_input.setPlaceholderText("请输入午餐内容...")
        self.lunch_input.setMinimumHeight(35)
        self.lunch_input.setMaximumHeight(70)
        lunch_layout.addWidget(self.lunch_input, 1)
        
        # 午餐打卡按钮
        self.lunch_check_btn = QPushButton("打卡")
        self.lunch_check_btn.setFixedWidth(60)
        self.lunch_check_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.lunch_check_btn.clicked.connect(lambda: self.toggle_meal_check("lunch"))
        lunch_layout.addWidget(self.lunch_check_btn)
        
        form.addRow("午餐:", lunch_layout)
        
        # 午餐打卡状态
        self.lunch_status = QLabel("")
        self.lunch_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
        form.addRow("", self.lunch_status)
        
        # 午餐推荐
        self.lunch_recommendation = QLabel("")
        self.lunch_recommendation.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        self.lunch_recommendation.setWordWrap(True)
        form.addRow("", self.lunch_recommendation)
        
        # 晚餐
        dinner_layout = QHBoxLayout()
        self.dinner_input = QTextEdit()
        self.dinner_input.setPlaceholderText("请输入晚餐内容...")
        self.dinner_input.setMinimumHeight(35)
        self.dinner_input.setMaximumHeight(70)
        dinner_layout.addWidget(self.dinner_input, 1)
        
        # 晚餐打卡按钮
        self.dinner_check_btn = QPushButton("打卡")
        self.dinner_check_btn.setFixedWidth(60)
        self.dinner_check_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.dinner_check_btn.clicked.connect(lambda: self.toggle_meal_check("dinner"))
        dinner_layout.addWidget(self.dinner_check_btn)
        
        form.addRow("晚餐:", dinner_layout)
        
        # 晚餐打卡状态
        self.dinner_status = QLabel("")
        self.dinner_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
        form.addRow("", self.dinner_status)
        
        # 晚餐推荐
        self.dinner_recommendation = QLabel("")
        self.dinner_recommendation.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        self.dinner_recommendation.setWordWrap(True)
        form.addRow("", self.dinner_recommendation)
        
        layout.addLayout(form)
 
        # 按钮
        self.save_btn = QPushButton("保存食谱计划")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        self.save_btn.clicked.connect(self.save_meal_plan)
        layout.addWidget(self.save_btn)
        
        back_btn = QPushButton("返回")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 5px;
                font-size: 14px;
            }
        """)
        back_btn.clicked.connect(self.parent.show_dashboard)
        layout.addWidget(back_btn)        
        
        # 设置滚动内容
        scroll.setWidget(scroll_content)
        
        # 将滚动区域添加到主布局
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)
        self.setMinimumSize(500, 550)
    
    def load_meal_plan(self):
        """加载食谱计划数据"""
        try:
            import requests
            response = requests.get(
                f"http://127.0.0.1:8000/api/pets/{self.pet_id}/meal-plan",
                headers={"Authorization": f"Bearer {self.parent.token}"}
            )
            
            if response.status_code == 200:
                self.meal_plan = response.json()
                self.breakfast_input.setText(self.meal_plan.get('breakfast', ''))
                self.lunch_input.setText(self.meal_plan.get('lunch', ''))
                self.dinner_input.setText(self.meal_plan.get('dinner', ''))
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "加载失败", "无法加载食谱计划")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "连接错误", f"无法连接到服务: {str(e)}")
    
    def save_meal_plan(self):
        """保存食谱计划到API"""
        breakfast = self.breakfast_input.toPlainText()
        lunch = self.lunch_input.toPlainText()
        dinner = self.dinner_input.toPlainText()
        
        try:
            import requests
            url = f"http://127.0.0.1:8000/api/pets/{self.pet_id}/meal-plan"
            headers = {
                "Authorization": f"Bearer {self.parent.token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "breakfast": breakfast,
                "lunch": lunch,
                "dinner": dinner
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "保存成功", "食谱计划已保存")
                # 更新本地数据
                if self.meal_plan:
                    self.meal_plan['breakfast'] = breakfast
                    self.meal_plan['lunch'] = lunch
                    self.meal_plan['dinner'] = dinner
            else:
                from PyQt5.QtWidgets import QMessageBox
                error_msg = response.json().get("message", "保存失败")
                QMessageBox.critical(self, "保存失败", error_msg)
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "连接错误", f"无法连接到服务: {str(e)}")


    def load_recommendation(self):
        """加载食物推荐"""
        try:
            import requests
            species_map = {
                "dog": "狗",
                "cat": "猫",
                "rabbit": "兔子",
                "hamster": "仓鼠",
                "bird": "鸟",
                "Dog": "狗",
                "Cat": "猫",
                "Rabbit": "兔子",
                "Hamster": "仓鼠",
                "Bird": "鸟"
            }
            chinese_species = species_map.get(self.species, self.species)
            
            response = requests.get(
                f"http://127.0.0.1:8000/api/meal-plan/recommendations/{chinese_species}"
            )
            print(f"请求食物推荐 - 种类: {self.species} -> {chinese_species}")
            print(f"API响应: {response.status_code}, {response.text}")
            if response.status_code == 200:
                data = response.json()
                
                # 分别设置早中晚三餐的推荐
                self.breakfast_recommendation.setText(data.get("breakfast", ""))
                self.lunch_recommendation.setText(data.get("lunch", ""))
                self.dinner_recommendation.setText(data.get("dinner", ""))
            else:
                # 使用默认推荐
                default_breakfast = f"推荐早餐：{self.species}的常规早餐"
                default_lunch = f"推荐午餐：{self.species}的常规午餐"
                default_dinner = f"推荐晚餐：{self.species}的常规晚餐"
                
                self.breakfast_recommendation.setText(default_breakfast)
                self.lunch_recommendation.setText(default_lunch)
                self.dinner_recommendation.setText(default_dinner)
        except Exception as e:
            print(f"【UI】加载食物推荐失败: {str(e)}")
            default_breakfast = f"推荐早餐：{self.species}的常规早餐"
            default_lunch = f"推荐午餐：{self.species}的常规午餐"
            default_dinner = f"推荐晚餐：{self.species}的常规晚餐"
            
            self.breakfast_recommendation.setText(default_breakfast)
            self.lunch_recommendation.setText(default_lunch)
            self.dinner_recommendation.setText(default_dinner)
    
    def load_feeding_record(self):
        """加载喂食记录"""
        try:
            import requests
            response = requests.get(
                f"http://127.0.0.1:8000/api/pets/{self.pet_id}/feeding-record",
                headers={"Authorization": f"Bearer {self.parent.token}"}
            )
            
            if response.status_code == 200:
                self.feeding_record = response.json()
                self.update_feeding_status()
            else:
                print(f"加载喂食记录失败: {response.status_code}")
        except Exception as e:
            print(f"加载喂食记录失败: {str(e)}")
    
    def update_feeding_status(self):
        """更新喂食状态显示"""
        if not self.feeding_record:
            return
        
        # 更新早餐状态
        if self.feeding_record.get("breakfast_done", False):
            self.breakfast_status.setText("✓ 早餐已打卡")
            self.breakfast_check_btn.setText("取消")
        else:
            self.breakfast_status.setText("")
            self.breakfast_check_btn.setText("打卡")
        
        # 更新午餐状态
        if self.feeding_record.get("lunch_done", False):
            self.lunch_status.setText("✓ 午餐已打卡")
            self.lunch_check_btn.setText("取消")
        else:
            self.lunch_status.setText("")
            self.lunch_check_btn.setText("打卡")
        
        # 更新晚餐状态
        if self.feeding_record.get("dinner_done", False):
            self.dinner_status.setText("✓ 晚餐已打卡")
            self.dinner_check_btn.setText("取消")
        else:
            self.dinner_status.setText("")
            self.dinner_check_btn.setText("打卡")
    
    def toggle_meal_check(self, meal_type):
        """切换餐次打卡状态"""
        current_status = False
        if meal_type == "breakfast":
            current_status = self.feeding_record.get("breakfast_done", False)
        elif meal_type == "lunch":
            current_status = self.feeding_record.get("lunch_done", False)
        elif meal_type == "dinner":
            current_status = self.feeding_record.get("dinner_done", False)
        
        # 切换状态
        new_status = not current_status
        
        try:
            import requests
            response = requests.post(
                f"http://127.0.0.1:8000/api/pets/{self.pet_id}/feeding-record",
                headers={"Authorization": f"Bearer {self.parent.token}"},
                data={
                    "meal_type": meal_type,
                    "done": str(new_status).lower()
                }
            )
            
            if response.status_code == 200:
                self.feeding_record = response.json()
                self.update_feeding_status()
            else:
                print(f"更新喂食记录失败: {response.status_code}")
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "打卡失败", "无法更新打卡状态")
        except Exception as e:
            print(f"更新喂食记录失败: {str(e)}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "连接错误", f"无法连接到服务: {str(e)}")