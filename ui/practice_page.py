# ui/practice_page.py

import random
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QMessageBox
from PyQt6.QtGui import QFont
from logic.data_manager import load_problems

class PracticePage(QWidget):
    navigateToWelcome = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.current_problem = None; self.solution_visible = False; self.current_category = None
        self.initUI()
    def initUI(self):
        main_layout = QVBoxLayout(self)
        control_layout = QHBoxLayout()
        self.random_button = QPushButton("下一题"); self.toggle_solution_button = QPushButton("显示答案"); self.back_button = QPushButton("返回练习菜单")
        control_layout.addWidget(self.random_button); control_layout.addWidget(self.toggle_solution_button); control_layout.addStretch(); control_layout.addWidget(self.back_button)
        main_layout.addLayout(control_layout)
        self.details_area = QTextEdit(); self.details_area.setReadOnly(True); self.details_area.setFont(QFont("Arial", 12))
        main_layout.addWidget(self.details_area)
        self.random_button.clicked.connect(self.show_random_problem); self.toggle_solution_button.clicked.connect(self.toggle_solution)
        self.back_button.clicked.connect(self.navigateToWelcome.emit)
        self.details_area.setText("<h1>请选择练习类别开始</h1>")

    def set_practice_category(self, category):
        self.current_category = category

    def show_random_problem(self):
        all_problems = load_problems()
        category = self.current_category.lower()
        if category == "coding": filtered_problems = [p for p in all_problems if p.get("is_programming", False)]
        else: filtered_problems = [p for p in all_problems for tag in p.get("tags", []) if category in tag.lower()]
        
        if not filtered_problems:
            self.current_problem = None
            QMessageBox.information(self, "提示", f"题库中没有找到“{self.current_category}”类别的题目。")
            self.navigateToWelcome.emit(); return
            
        self.current_problem = random.choice(filtered_problems)
        self.solution_visible = False
        
        self.toggle_solution_button.setVisible(True)
        self.toggle_solution_button.setText("显示答案")
        self.display_current_problem()
    
    def toggle_solution(self):
        if self.current_problem is None: return
        self.solution_visible = not self.solution_visible
        self.toggle_solution_button.setText("隐藏答案" if self.solution_visible else "显示答案")
        self.display_current_problem()

    def display_current_problem(self):
        if self.current_problem is None: return
        
        is_programming = self.current_problem.get("is_programming", False)
        html_content = f"""<h1>{self.current_problem.get('title', '')}</h1><p><b>来源:</b> {self.current_problem.get('source', '')}</p><p><b>标签:</b> {', '.join(self.current_problem.get('tags', []))}</p><hr><h3>描述</h3><p>{self.current_problem.get('description', '').replace('\\n', '<br>')}</p>"""
        
        if self.solution_visible:
            if is_programming:
                html_content += f"""<hr><h3>Python 解法</h3><pre><code>{self.current_problem.get('python_solution', '')}</code></pre><hr><h3>C++ 解法</h3><pre><code>{self.current_problem.get('cpp_solution', '')}</code></pre>"""
            else:
                html_content += f"""<hr><h3>答案与解析</h3><p>{self.current_problem.get('answer', '（没有提供答案）').replace('\\n', '<br>')}</p>"""
                
        html_content += f"""<hr><h3>备注</h3><p>{self.current_problem.get('notes', '').replace('\\n', '<br>')}</p>"""
        self.details_area.setHtml(html_content)