# ui/editor_page.py

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit,
    QPushButton, QSplitter, QListWidgetItem, QDialog, QFormLayout,
    QLineEdit, QDialogButtonBox, QMessageBox, QCheckBox, QLabel, QComboBox
)
from logic.data_manager import load_problems, save_problems

# 【改动1】定义预设标签列表
PREDEFINED_TAGS = ["", "Math", "Probability", "Coding", "Finance", "Brain Teaser"]

class AddProblemDialog(QDialog):
    """用于添加或编辑新题目的对话框 (已更新为标签下拉选择)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # ... (除了tags相关的部分，其他组件的创建和之前一样) ...
        self.setWindowTitle("添加新题目"); self.setMinimumWidth(600); self.layout = QFormLayout(self)
        self.title = QLineEdit(self); self.source = QLineEdit(self)
        
        # --- 【改动2】用QComboBox替换QLineEdit ---
        self.tags_selector = QComboBox(self)
        self.tags_selector.addItems(PREDEFINED_TAGS)
        
        self.description = QTextEdit(self); self.notes = QTextEdit(self)
        self.is_programming_checkbox = QCheckBox("Coding", self)
        self.code_input_layout = QHBoxLayout(); self.language_selector = QComboBox()
        self.language_selector.addItems(["Python", "C++"])
        self.code_input_layout.addWidget(self.language_selector)
        self.code_label = QLabel("解法:"); self.code_input_area = QTextEdit(); self.code_input_area.setFontFamily("Courier New")
        self.python_code_buffer = ""; self.cpp_code_buffer = ""; self.current_language = "Python"
        
        # --- 布局 ---
        self.layout.addRow("标题:", self.title)
        self.layout.addRow("来源:", self.source)
        # --- 【改动3】更新布局中的标签组件 ---
        self.layout.addRow("标签:", self.tags_selector)
        self.layout.addRow("描述:", self.description)
        self.layout.addRow(self.is_programming_checkbox)
        self.layout.addRow(self.code_label, self.code_input_layout)
        self.layout.addRow(self.code_input_area)
        self.layout.addRow("备注:", self.notes)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttons.accepted.connect(self.accept); self.buttons.rejected.connect(self.reject)
        self.layout.addRow(self.buttons)
        self.is_programming_checkbox.stateChanged.connect(self.toggle_solution_fields)
        self.language_selector.currentTextChanged.connect(self.on_language_changed)
        self.toggle_solution_fields()

    def get_data(self):
        """获取用户输入的数据 (已更新)"""
        self.on_language_changed(self.language_selector.currentText())
        
        # --- 【改动4】从下拉菜单获取标签 ---
        selected_tag = self.tags_selector.currentText()

        data = {
            "title": self.title.text(),
            "source": self.source.text(),
            # 如果选择了有效标签，则保存为列表；否则保存为空列表
            "tags": [selected_tag] if selected_tag else [],
            "description": self.description.toPlainText(),
            "notes": self.notes.toPlainText(),
            "is_programming": self.is_programming_checkbox.isChecked()
        }
        if data["is_programming"]:
            data["python_solution"] = self.python_code_buffer
            data["cpp_solution"] = self.cpp_code_buffer
        else:
            data["python_solution"] = ""; data["cpp_solution"] = ""
        return data
        
    # (on_language_changed, toggle_solution_fields 方法和之前完全一样，无需改动)
    def on_language_changed(self, new_language):
        if self.current_language == "Python": self.python_code_buffer = self.code_input_area.toPlainText()
        elif self.current_language == "C++": self.cpp_code_buffer = self.code_input_area.toPlainText()
        if new_language == "Python": self.code_input_area.setPlainText(self.python_code_buffer)
        elif new_language == "C++": self.code_input_area.setPlainText(self.cpp_code_buffer)
        self.current_language = new_language
    def toggle_solution_fields(self):
        is_checked = self.is_programming_checkbox.isChecked()
        self.code_label.setVisible(is_checked); self.language_selector.setVisible(is_checked); self.code_input_area.setVisible(is_checked)

class EditorPage(QWidget):
    # ... EditorPage 类的所有代码都和之前完全一样，无需改动 ...
    navigateToWelcome = pyqtSignal()
    def __init__(self): super().__init__(); self.problems = []; self.initUI()
    def initUI(self):
        main_layout = QVBoxLayout(self); button_layout = QHBoxLayout()
        self.add_button = QPushButton("添加题目"); self.delete_button = QPushButton("删除题目"); self.back_button = QPushButton("返回主菜单")
        button_layout.addWidget(self.add_button); button_layout.addWidget(self.delete_button); button_layout.addStretch(); button_layout.addWidget(self.back_button)
        main_layout.addLayout(button_layout)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.problem_list_widget = QListWidget(); self.details_area = QTextEdit(); self.details_area.setReadOnly(True)
        splitter.addWidget(self.problem_list_widget); splitter.addWidget(self.details_area); splitter.setSizes([300, 900])
        main_layout.addWidget(splitter)
        self.problem_list_widget.itemClicked.connect(self.display_problem_details); self.add_button.clicked.connect(self.show_add_dialog)
        self.delete_button.clicked.connect(self.delete_selected_problem); self.back_button.clicked.connect(self.navigateToWelcome.emit)
    def load_and_display_problems(self):
        self.problems = load_problems(); self.problem_list_widget.clear()
        for problem in self.problems:
            item = QListWidgetItem(problem['title']); item.setData(Qt.ItemDataRole.UserRole, problem['id']); self.problem_list_widget.addItem(item)
    def display_problem_details(self, item):
        problem_id = item.data(Qt.ItemDataRole.UserRole)
        problem = next((p for p in self.problems if p['id'] == problem_id), None)
        if not problem: self.details_area.setText("未找到题目详情。"); return
        is_programming = problem.get("is_programming", False)
        html_content = f"""<h1>{problem.get('title', '')}</h1><p><b>来源:</b> {problem.get('source', '')}</p><p><b>标签:</b> {', '.join(problem.get('tags', []))}</p><hr><h3>描述</h3><p>{problem.get('description', '').replace('\\n', '<br>')}</p>"""
        if is_programming: html_content += f"""<hr><h3>Python 解法</h3><pre><code>{problem.get('python_solution', '')}</code></pre><hr><h3>C++ 解法</h3><pre><code>{problem.get('cpp_solution', '')}</code></pre>"""
        html_content += f"""<hr><h3>备注</h3><p>{problem.get('notes', '').replace('\\n', '<br>')}</p>"""
        self.details_area.setHtml(html_content)
    def show_add_dialog(self):
        dialog = AddProblemDialog(self)
        if dialog.exec():
            new_data = dialog.get_data()
            if not new_data['title']: QMessageBox.warning(self, "错误", "标题不能为空！"); return
            new_id = max([p['id'] for p in self.problems], default=0) + 1; new_data['id'] = new_id
            self.problems.append(new_data); save_problems(self.problems); self.load_and_display_problems()
    def delete_selected_problem(self):
        selected_items = self.problem_list_widget.selectedItems()
        if not selected_items: QMessageBox.information(self, "提示", "请先在左侧列表中选择一个要删除的题目。"); return
        selected_item = selected_items[0]; problem_id = selected_item.data(Qt.ItemDataRole.UserRole); problem_title = selected_item.text()
        reply = QMessageBox.question(self, '确认删除', f"你确定要删除题目 '{problem_title}' 吗？\n这个操作无法撤销。", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.problems = [p for p in self.problems if p['id'] != problem_id]
            save_problems(self.problems); self.load_and_display_problems(); self.details_area.clear()