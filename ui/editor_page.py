# ui/editor_page.py

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit,
    QPushButton, QSplitter, QListWidgetItem, QDialog, QFormLayout,
    QLineEdit, QDialogButtonBox, QMessageBox, QCheckBox, QLabel, QComboBox,
    QCompleter # <-- 引入自动补全组件
)
from logic.data_manager import load_problems, save_problems

PREDEFINED_TAGS = ["", "Math", "Probability", "Coding", "Finance", "Brain Teaser"]

class AddProblemDialog(QDialog):
    """对话框已更新，“公司”字段支持自动补全"""
    # --- 【改动1】构造函数现在需要接收所有题目，以便提取公司列表 ---
    def __init__(self, all_problems, problem_data=None, parent=None):
        super().__init__(parent)
        self.problem_data = problem_data
        self.setWindowTitle("编辑题目" if self.problem_data else "添加新题目")
        self.setMinimumWidth(600)
        
        self.layout = QFormLayout(self)
        self.title = QLineEdit(self)
        
        # --- 【改动2】创建公司输入框和自动补全器 ---
        self.company_input = QLineEdit(self)
        # 从所有题目中动态生成一个不重复的公司列表
        all_companies = sorted(list({p.get("source", "").strip() for p in all_problems if p.get("source", "").strip()}))
        completer = QCompleter(all_companies, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive) # 不区分大小写
        completer.setFilterMode(Qt.MatchFlag.MatchContains) # 包含即可，更友好
        self.company_input.setCompleter(completer)
        
        # --- 其他组件和之前一样 ---
        self.tags_selector = QComboBox(self); self.tags_selector.addItems(PREDEFINED_TAGS)
        self.description = QTextEdit(self); self.notes = QTextEdit(self)
        self.is_programming_checkbox = QCheckBox("Coding", self)
        self.answer_label = QLabel("答案与解析:"); self.answer_input = QTextEdit(self)
        self.code_input_layout = QHBoxLayout(); self.language_selector = QComboBox()
        self.language_selector.addItems(["Python", "C++"])
        self.code_input_layout.addWidget(self.language_selector)
        self.code_label = QLabel("解法:"); self.code_input_area = QTextEdit(); self.code_input_area.setFontFamily("Courier New")
        self.python_code_buffer = ""; self.cpp_code_buffer = ""; self.current_language = "Python"

        # --- 布局 ---
        self.layout.addRow("标题:", self.title)
        # --- 【改动3】修改标签文本，并使用新的company_input ---
        self.layout.addRow("公司:", self.company_input)
        self.layout.addRow("标签:", self.tags_selector)
        self.layout.addRow("描述:", self.description)
        self.layout.addRow(self.is_programming_checkbox); self.layout.addRow(self.answer_label, self.answer_input)
        self.layout.addRow(self.code_label, self.code_input_layout); self.layout.addRow(self.code_input_area)
        self.layout.addRow("备注:", self.notes)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttons.accepted.connect(self.accept); self.buttons.rejected.connect(self.reject)
        self.layout.addRow(self.buttons)
        
        self.is_programming_checkbox.stateChanged.connect(self.toggle_solution_fields)
        self.language_selector.currentTextChanged.connect(self.on_language_changed)
        if self.problem_data: self.populate_data()
        self.toggle_solution_fields()

    def populate_data(self):
        """用现有数据填充对话框，已更新"""
        self.title.setText(self.problem_data.get("title", ""))
        self.company_input.setText(self.problem_data.get("source", "")) # <-- 使用 company_input
        tag = self.problem_data.get("tags", [""])[0]
        if tag in PREDEFINED_TAGS: self.tags_selector.setCurrentText(tag)
        self.description.setPlainText(self.problem_data.get("description", "")); self.notes.setPlainText(self.problem_data.get("notes", ""))
        is_coding = self.problem_data.get("is_programming", False)
        self.is_programming_checkbox.setChecked(is_coding)
        if is_coding:
            self.python_code_buffer = self.problem_data.get("python_solution", ""); self.cpp_code_buffer = self.problem_data.get("cpp_solution", "")
            self.code_input_area.setPlainText(self.python_code_buffer)
        else: self.answer_input.setPlainText(self.problem_data.get("answer", ""))

    def get_data(self):
        """获取用户输入的数据，已更新"""
        self.on_language_changed(self.language_selector.currentText())
        selected_tag = self.tags_selector.currentText()
        data = {
            "title": self.title.text(),
            "source": self.company_input.text(), # <-- 使用 company_input
            "tags": [selected_tag] if selected_tag else [],
            "description": self.description.toPlainText(), "notes": self.notes.toPlainText(),
            "is_programming": self.is_programming_checkbox.isChecked()
        }
        if data["is_programming"]: data["python_solution"] = self.python_code_buffer; data["cpp_solution"] = self.cpp_code_buffer; data["answer"] = ""
        else: data["python_solution"] = ""; data["cpp_solution"] = ""; data["answer"] = self.answer_input.toPlainText()
        return data
        
    def toggle_solution_fields(self):
        is_coding = self.is_programming_checkbox.isChecked()
        self.code_label.setVisible(is_coding); self.language_selector.setVisible(is_coding); self.code_input_area.setVisible(is_coding)
        self.answer_label.setVisible(not is_coding); self.answer_input.setVisible(not is_coding)
    def on_language_changed(self, new_language):
        if self.current_language == "Python": self.python_code_buffer = self.code_input_area.toPlainText()
        elif self.current_language == "C++": self.cpp_code_buffer = self.code_input_area.toPlainText()
        if new_language == "Python": self.code_input_area.setPlainText(self.python_code_buffer)
        elif new_language == "C++": self.code_input_area.setPlainText(self.cpp_code_buffer)
        self.current_language = new_language

class EditorPage(QWidget):
    navigateToWelcome = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.problems = []
        self.initUI()
    def initUI(self):
        # ... initUI 方法和之前完全一样 ...
        main_layout = QVBoxLayout(self); button_layout = QHBoxLayout()
        self.add_button = QPushButton("添加题目"); self.edit_button = QPushButton("编辑题目"); self.delete_button = QPushButton("删除题目"); self.back_button = QPushButton("返回主菜单")
        button_layout.addWidget(self.add_button); button_layout.addWidget(self.edit_button); button_layout.addWidget(self.delete_button); button_layout.addStretch(); button_layout.addWidget(self.back_button)
        main_layout.addLayout(button_layout)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.problem_list_widget = QListWidget(); self.details_area = QTextEdit(); self.details_area.setReadOnly(True)
        splitter.addWidget(self.problem_list_widget); splitter.addWidget(self.details_area); splitter.setSizes([300, 900])
        main_layout.addWidget(splitter)
        self.problem_list_widget.itemClicked.connect(self.display_problem_details); self.add_button.clicked.connect(self.show_add_dialog)
        self.edit_button.clicked.connect(self.show_edit_dialog); self.delete_button.clicked.connect(self.delete_selected_problem); self.back_button.clicked.connect(self.navigateToWelcome.emit)
    
    def display_problem_details(self, item):
        """显示题目详情时，将"来源"显示为"公司" """
        problem_id = item.data(Qt.ItemDataRole.UserRole)
        problem = next((p for p in self.problems if p['id'] == problem_id), None)
        if not problem: self.details_area.setText("未找到题目详情。"); return
        is_programming = problem.get("is_programming", False)
        # --- 【改动4】将HTML中的"来源"改为"公司" ---
        html_content = f"""<h1>{problem.get('title', '')}</h1><p><b>公司:</b> {problem.get('source', '')}</p><p><b>标签:</b> {', '.join(problem.get('tags', []))}</p><hr><h3>描述</h3><p>{problem.get('description', '').replace('\\n', '<br>')}</p>"""
        if is_programming: html_content += f"""<hr><h3>Python 解法</h3><pre><code>{problem.get('python_solution', '')}</code></pre><hr><h3>C++ 解法</h3><pre><code>{problem.get('cpp_solution', '')}</code></pre>"""
        else: html_content += f"""<hr><h3>答案与解析</h3><p>{problem.get('answer', '').replace('\\n', '<br>')}</p>"""
        html_content += f"""<hr><h3>备注</h3><p>{problem.get('notes', '').replace('\\n', '<br>')}</p>"""
        self.details_area.setHtml(html_content)

    def show_add_dialog(self):
        """处理“添加”按钮点击，已更新"""
        # --- 【改动5】调用对话框时，传入所有题目列表 ---
        dialog = AddProblemDialog(self.problems, None, self)
        if dialog.exec():
            new_data = dialog.get_data()
            if not new_data['title']: QMessageBox.warning(self, "错误", "标题不能为空！"); return
            new_id = max([p['id'] for p in self.problems], default=0) + 1
            new_data['id'] = new_id
            self.problems.append(new_data); save_problems(self.problems); self.load_and_display_problems()

    def show_edit_dialog(self):
        """处理“编辑”按钮点击，已更新"""
        selected_items = self.problem_list_widget.selectedItems()
        if not selected_items: QMessageBox.information(self, "提示", "请先在左侧列表中选择一个要编辑的题目。"); return
        selected_item = selected_items[0]
        problem_id = selected_item.data(Qt.ItemDataRole.UserRole)
        problem_to_edit = next((p for p in self.problems if p['id'] == problem_id), None)
        if not problem_to_edit: QMessageBox.critical(self, "错误", "找不到要编辑的题目数据。"); return
        
        # --- 【改动6】调用对话框时，传入所有题目列表 ---
        dialog = AddProblemDialog(self.problems, problem_to_edit, self)
        if dialog.exec():
            updated_data = dialog.get_data()
            if not updated_data['title']: QMessageBox.warning(self, "错误", "标题不能为空！"); return
            index_to_update = next((i for i, p in enumerate(self.problems) if p['id'] == problem_id), -1)
            if index_to_update != -1:
                updated_data['id'] = problem_id 
                self.problems[index_to_update] = updated_data
                save_problems(self.problems); self.load_and_display_problems()
                self.display_problem_details(selected_item)

    def load_and_display_problems(self):
        # ... (和之前完全一样) ...
        self.problems = load_problems(); self.problem_list_widget.clear()
        for problem in self.problems: item = QListWidgetItem(problem['title']); item.setData(Qt.ItemDataRole.UserRole, problem['id']); self.problem_list_widget.addItem(item)
    def delete_selected_problem(self):
        # ... (和之前完全一样) ...
        selected_items = self.problem_list_widget.selectedItems()
        if not selected_items: QMessageBox.information(self, "提示", "请先在左侧列表中选择一个要删除的题目。"); return
        selected_item = selected_items[0]; problem_id = selected_item.data(Qt.ItemDataRole.UserRole); problem_title = selected_item.text()
        reply = QMessageBox.question(self, '确认删除', f"你确定要删除题目 '{problem_title}' 吗？\n这个操作无法撤销。", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.problems = [p for p in self.problems if p['id'] != problem_id]
            save_problems(self.problems); self.load_and_display_problems(); self.details_area.clear()