# ui/practice_page.py

import random
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QMessageBox, QLabel, QLineEdit
from PyQt6.QtGui import QFont
from logic.data_manager import load_problems, update_problem_stats, toggle_problem_saved_status
import re

def format_text_for_display(text):
    if not isinstance(text, str): return ""
    formatted_text = text.replace('\n', '<br>')
    formatted_text = re.sub(r'(\w+)\^([\w\d]+)', r'\1<sup>\2</sup>', formatted_text)
    formatted_text = re.sub(r'(\w+)_([\w\d]+)', r'\1<sub>\2</sub>', formatted_text)
    return formatted_text

class PracticePage(QWidget):
    """交互式练习页面，优化了按钮文本"""
    navigateToWelcome = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.current_problem = None
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        # --- 1. 控制区 ---
        control_layout = QHBoxLayout()
        self.next_button = QPushButton("开始随机练习")
        self.save_button = QPushButton("收藏 🤍") # <-- 新增按钮
        self.back_button = QPushButton("返回练习菜单")
        
        control_layout.addWidget(self.next_button)
        control_layout.addWidget(self.save_button) # <-- 添加到布局
        control_layout.addStretch()
        control_layout.addWidget(self.back_button)
        main_layout.addLayout(control_layout)

        # ... (后面其他组件的创建和之前一样) ...
        self.problem_display = QTextEdit(); self.problem_display.setReadOnly(True); self.problem_display.setFont(QFont("Arial", 12))
        main_layout.addWidget(self.problem_display)
        self.answer_widget = QWidget(); answer_layout = QHBoxLayout(self.answer_widget)
        self.user_answer_input = QLineEdit(); self.submit_button = QPushButton("提交答案")
        answer_layout.addWidget(QLabel("你的答案:")); answer_layout.addWidget(self.user_answer_input); answer_layout.addWidget(self.submit_button)
        main_layout.addWidget(self.answer_widget)
        self.self_assess_widget = QWidget(); assess_layout = QHBoxLayout(self.self_assess_widget)
        self.correct_button = QPushButton("我做对了"); self.incorrect_button = QPushButton("我做错了")
        assess_layout.addStretch(); assess_layout.addWidget(self.correct_button); assess_layout.addWidget(self.incorrect_button); assess_layout.addStretch()
        main_layout.addWidget(self.self_assess_widget)
        self.feedback_label = QLabel(""); self.feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.solution_display = QTextEdit(); self.solution_display.setReadOnly(True); self.solution_display.setFont(QFont("Arial", 11))
        main_layout.addWidget(self.feedback_label); main_layout.addWidget(self.solution_display)
        
        # --- 连接信号 ---
        self.next_button.clicked.connect(self.show_next_problem)
        self.save_button.clicked.connect(self.toggle_save_status) # <-- 连接新按钮的信号
        self.submit_button.clicked.connect(self.check_answer)
        self.correct_button.clicked.connect(lambda: self.record_self_assessment(True))
        self.incorrect_button.clicked.connect(lambda: self.record_self_assessment(False))
        self.back_button.clicked.connect(self.navigateToWelcome.emit)
        
        self.problem_display.setText("<h1>请点击“开始随机练习”</h1>")
        self.set_initial_state()

    def set_practice_category(self, category):
        self.current_category = category

    def set_initial_state(self):
        """设置所有组件的初始可见性"""
        self.answer_widget.setVisible(False)
        self.self_assess_widget.setVisible(False)
        self.feedback_label.setVisible(False)
        self.solution_display.setVisible(False)
        self._update_save_button_text() # <-- 在这里也调用一次，处理初始状态

    def show_next_problem(self):
        """获取并显示下一道随机题，并格式化题干"""
        self.set_initial_state()
        all_problems = load_problems()
        category = self.current_category.lower()
        if category == "coding": filtered_problems = [p for p in all_problems if p.get("is_programming", False)]
        else: filtered_problems = [p for p in all_problems for tag in p.get("tags", []) if category in tag.lower()]
        
        if not filtered_problems:
            QMessageBox.information(self, "提示", f"题库中没有找到“{self.current_category}”类别的题目。"); self.navigateToWelcome.emit(); return
        
        self.current_problem = random.choice(filtered_problems)
        
        # --- 【核心改动】使用格式化函数来渲染题干 ---
        title_html = format_text_for_display(self.current_problem.get('title', ''))
        company_html = format_text_for_display(self.current_problem.get('source', ''))
        tags_html = format_text_for_display(', '.join(self.current_problem.get('tags', [])))
        desc_html = format_text_for_display(self.current_problem.get('description', ''))
        
        html_desc = f"""<h1>{title_html}</h1><p><b>公司:</b> {company_html}</p><p><b>标签:</b> {tags_html}</p><hr><h3>描述</h3><p>{desc_html}</p>"""
        self.problem_display.setHtml(html_desc)
        
        self.next_button.setText("下一题")
        self._update_save_button_text()

        if self.current_problem.get("is_programming", False):
            self.self_assess_widget.setVisible(True)
        else:
            self.answer_widget.setVisible(True)
            self.user_answer_input.clear()

    def check_answer(self):
        """检查非编程题答案"""
        user_answer = self.user_answer_input.text().strip()
        correct_answer = self.current_problem.get("answer", "").strip()
        was_correct = user_answer.lower() == correct_answer.lower()
        
        self.feedback_label.setText(f"<font color='green'>回答正确！</font>" if was_correct else f"<font color='red'>回答错误。</font>")
        self.feedback_label.setVisible(True)
        update_problem_stats(self.current_problem['id'], was_correct)
        self.show_solution()
        
    def record_self_assessment(self, was_correct):
        """记录编程题的自我评估结果"""
        update_problem_stats(self.current_problem['id'], was_correct)
        self.show_solution()

    def show_solution(self):
        """显示题目的完整答案/解析，并使用富文本格式化"""
        self.answer_widget.setVisible(False)
        self.self_assess_widget.setVisible(False)

        is_programming = self.current_problem.get("is_programming", False)
        
        html_solution = ""
        if is_programming:
            # 代码部分保持原样，不进行格式化
            py_solution = self.current_problem.get('python_solution', '')
            cpp_solution = self.current_problem.get('cpp_solution', '')
            html_solution = f"""<h3>Python 解法</h3><pre><code>{py_solution}</code></pre><hr><h3>C++ 解法</h3><pre><code>{cpp_solution}</code></pre>"""
        else:
            # --- 【核心改动】使用格式化函数 ---
            answer_html = format_text_for_display(self.current_problem.get('answer', ''))
            html_solution = f"""<h3>答案与解析</h3><p>{answer_html}</p>"""
        
        # --- 【核心改动】使用格式化函数 ---
        notes_html = format_text_for_display(self.current_problem.get('notes', ''))
        html_solution += f"""<hr><h3>备注</h3><p>{notes_html}</p>"""
        
        self.solution_display.setHtml(html_solution)
        self.solution_display.setVisible(True)

    def toggle_save_status(self):
        """处理收藏按钮点击事件"""
        if not self.current_problem:
            QMessageBox.information(self, "提示", "请先开始一道题目。")
            return
        
        problem_id = self.current_problem['id']
        # 调用logic层函数，它会返回更新后的状态 (True/False)
        new_status = toggle_problem_saved_status(problem_id)
        
        # 更新当前内存中的题目信息，避免需要重新加载
        self.current_problem['is_saved'] = new_status
        
        # 更新按钮文本提供即时反馈
        self._update_save_button_text()

    def _update_save_button_text(self):
        """根据当前题目的收藏状态，更新按钮文本和图标"""
        if not self.current_problem:
            self.save_button.setText("收藏 🤍")
            self.save_button.setEnabled(False) # 没有题目时禁用按钮
            return

        self.save_button.setEnabled(True) # 有题目时启用按钮
        if self.current_problem.get('is_saved', False):
            self.save_button.setText("取消收藏 ❤️")
        else:
            self.save_button.setText("收藏 🤍")

    