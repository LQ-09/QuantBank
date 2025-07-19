# ui/practice_page.py

import random
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QMessageBox
from PyQt6.QtGui import QFont

from logic.data_manager import load_problems

class PracticePage(QWidget):
    """实际进行练习的页面 (已更新筛选逻辑)"""
    navigateToWelcome = pyqtSignal()
    # ... (initUI, toggle_solution, display_current_problem等方法和之前一样，除了show_random_problem) ...
    def __init__(self):
        super().__init__()
        self.current_problem = None; self.solution_visible = False; self.current_category = None
        self.initUI()
    def initUI(self):
        main_layout = QVBoxLayout(self)
        control_layout = QHBoxLayout()
        self.random_button = QPushButton("下一题"); self.toggle_solution_button = QPushButton("显示答案"); self.back_button = QPushButton("返回练习菜单")
        control_layout.addWidget(self.random_button); control_layout.addWidget(self.toggle_solution_button)
        control_layout.addStretch(); control_layout.addWidget(self.back_button)
        main_layout.addLayout(control_layout)
        self.details_area = QTextEdit(); self.details_area.setReadOnly(True); self.details_area.setFont(QFont("Arial", 12))
        main_layout.addWidget(self.details_area)
        self.random_button.clicked.connect(self.show_random_problem); self.toggle_solution_button.clicked.connect(self.toggle_solution)
        self.back_button.clicked.connect(self.navigateToWelcome.emit)
        self.details_area.setText("<h1>请选择练习类别开始</h1>")

    def set_practice_category(self, category):
        """从主窗口设置练习类别"""
        self.current_category = category

    def show_random_problem(self):
        """根据设置的类别，获取一个随机问题并显示"""
        all_problems = load_problems()
        
        # --- 【核心改动】更新筛选逻辑 ---
        filtered_problems = []
        category = self.current_category.lower() # 转为小写以方便比较

        if category == "coding":
            filtered_problems = [p for p in all_problems if p.get("is_programming", False)]
        else:
            # 对于其他所有类别，我们都通过tag来筛选
            filtered_problems = [p for p in all_problems for tag in p.get("tags", []) if category in tag.lower()]
        
        if not filtered_problems:
            self.current_problem = None
            QMessageBox.information(self, "提示", f"题库中没有找到“{self.current_category}”类别的题目。")
            self.navigateToWelcome.emit() 
            return
            
        self.current_problem = random.choice(filtered_problems)
        self.solution_visible = False
        is_programming = self.current_problem.get("is_programming", False)
        self.toggle_solution_button.setVisible(is_programming)
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
        if self.solution_visible and is_programming: html_content += f"""<hr><h3>Python 解法</h3><pre><code>{problem.get('python_solution', '')}</code></pre><hr><h3>C++ 解法</h3><pre><code>{problem.get('cpp_solution', '')}</code></pre>"""
        html_content += f"""<hr><h3>备注</h3><p>{self.current_problem.get('notes', '').replace('\\n', '<br>')}</p>"""
        self.details_area.setHtml(html_content)