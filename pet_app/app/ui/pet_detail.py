from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFormLayout, QComboBox, QDateEdit,QLineEdit,QMessageBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

class PetDetailWindow(QWidget):
    """宠物详情界面组件"""
    
    def __init__(self, parent, pet_data=None):
        """
        Args:
            parent: 主窗口
            pet_data: 宠物数据字典，None表示新建宠物
        """
        super().__init__()
        self.parent = parent
        self.pet_data = pet_data
        self.setup_ui()
        
        if pet_data:
            self.load_pet_data(pet_data)
    
    def setup_ui(self):
        """构建宠物详情UI"""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # 标题
        self.title = QLabel("宠物详情")
        self.title.setFont(QFont("Arial", 20, QFont.Bold))
        self.title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(self.title)
        
        # 表单
        form = QFormLayout()
        form.setSpacing(15)
        
        self.name_input = QLineEdit()
        form.addRow("宠物名称:", self.name_input)
        
        self.species_combo = QComboBox()
        self.species_combo.addItems(["狗", "猫", "兔子", "仓鼠", "鸟"])
        form.addRow("宠物种类:", self.species_combo)
        
        self.breed_input = QLineEdit()
        form.addRow("品种:", self.breed_input)
        
        self.sex_combo = QComboBox()
        self.sex_combo.addItems(["公", "母", "未知"])
        form.addRow("性别:", self.sex_combo)
        
        self.birth_date = QDateEdit(QDate.currentDate())
        self.birth_date.setCalendarPopup(True)
        form.addRow("出生日期:", self.birth_date)
        
        self.weight_input = QLineEdit()
        form.addRow("体重(kg):", self.weight_input)
        
        layout.addLayout(form)
        
        # 按钮
        self.save_btn = QPushButton("保存宠物")
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
        self.save_btn.clicked.connect(self.save_pet)
        layout.addWidget(self.save_btn)
        
        back_btn = QPushButton("返回")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7f8c8d;
                border: none;
                padding: 5px;
                font-size: 14px;
            }
        """)
        back_btn.clicked.connect(self.parent.show_dashboard)
        layout.addWidget(back_btn)
        
        # 删除按钮
        self.delete_btn = QPushButton("删除宠物")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_pet)
        # 只有在编辑现有宠物时显示删除按钮
        if self.pet_data:
            layout.addWidget(self.delete_btn)
        self.setLayout(layout)
        self.setMinimumSize(400, 500)
    
    def load_pet_data(self, pet_data):
        """加载现有宠物数据到表单"""
        self.name_input.setText(pet_data.get('name', ''))
        species = pet_data.get('species', '')
        if species in ["狗", "猫", "兔子", "仓鼠", "鸟"]:
            self.species_combo.setCurrentText(species)
        self.breed_input.setText(pet_data.get('breed', ''))
        
        sex = pet_data.get('sex', '')
        if sex in ["公", "母", "未知"]:
            self.sex_combo.setCurrentText(sex)
        
        birth_date = pet_data.get('birth_date')
        if birth_date:
            try:
                self.birth_date.setDate(QDate.fromString(birth_date, "yyyy-MM-dd"))
            except:
                pass
        
        self.weight_input.setText(pet_data.get('weight_kg', ''))
        
        # 修改标题为编辑模式
        self.title.setText(f"编辑 {pet_data['name']}")
    
    def save_pet(self):
        """保存宠物数据到API"""
        name = self.name_input.text()
        species = self.species_combo.currentText()
        
        if not name:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "输入错误", "宠物名称不能为空")
            return
            
        try:
            import requests
            url = "http://127.0.0.1:8000/api/pets"
            headers = {"Authorization": f"Bearer {self.parent.token}"}
            
            data = {
                "name": name,
                "species": species,
                "breed": self.breed_input.text(),
                "sex": self.sex_combo.currentText(),
                "birth_date": self.birth_date.date().toString("yyyy-MM-dd"),
                "weight_kg": self.weight_input.text()
            }
            
            if self.pet_data and 'id' in self.pet_data:
                # 更新现有宠物（实际API需要实现PUT方法）
                url += f"/{self.pet_data['id']}"
                response = requests.put(url, json=data, headers=headers)
            else:
                # 创建新宠物
                response = requests.post(url, json=data, headers=headers)
            
            if response.status_code in (200, 201):
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "保存成功", "宠物信息已保存")
                self.parent.show_dashboard()
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "保存失败", "无法保存宠物信息")
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "连接错误", f"无法连接到服务: {str(e)}")


    def delete_pet(self):
        """删除宠物"""
        if not self.pet_data or 'id' not in self.pet_data:
            return
    
        print(f"尝试删除宠物，ID: {self.pet_data['id']}，类型: {type(self.pet_data['id'])}")
        print(f"当前token: {self.parent.token[:10]}...")  # 打印部分token用于调试
    
        reply = QMessageBox.question(self, "确认删除", 
                             f"确定要删除 {self.pet_data['name']} 吗？此操作不可恢复。",
                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    
        if reply == QMessageBox.Yes:
            try:
                import requests
                url = f"http://127.0.0.1:8000/api/pets/{self.pet_data['id']}"
                print(f"请求URL: {url}")
                headers = {"Authorization": f"Bearer {self.parent.token}"}
                print(f"请求头: {headers}")
            
                response = requests.delete(url, headers=headers)
                print(f"响应状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
            
                if response.status_code == 200:
                    QMessageBox.information(self, "删除成功", "宠物已成功删除")
                    self.parent.show_dashboard()
                else:
                    error_msg = response.json().get("detail", "删除失败")
                    QMessageBox.critical(self, "删除失败", error_msg)
            except Exception as e:
                QMessageBox.critical(self, "连接错误", f"无法连接到服务: {str(e)}")