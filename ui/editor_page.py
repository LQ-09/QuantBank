# ui/editor_page.py

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit,
    QPushButton, QSplitter, QListWidgetItem, QDialog, QFormLayout,
    QLineEdit, QDialogButtonBox, QMessageBox, QCheckBox, QLabel, QComboBox,
    QCompleter
)
from logic.data_manager import load_problems, save_problems, toggle_problem_saved_status
import re
import html

def natural_sort_key(problem):
    """为列表排序生成一个“自然排序”的键"""
    title = problem.get('title', '').lower()
    # 使用正则表达式尝试从标题末尾匹配 '#数字' 模式
    match = re.search(r'#(\d+)$', title)
    if match:
        # 如果匹配成功，返回一个元组 (文本部分, 数字部分)
        # 比如 "coin problem #10" -> ("coin problem #", 10)
        number = int(match.group(1))
        text_part = title[:match.start()]
        return (text_part, number)
    else:
        # 如果不匹配，返回 (标题, 0) 以便和其他项一起排序
        return (title, 0)

def format_text_for_display(text):
    """一个辅助函数，用于将简单的标记转换为HTML富文本"""
    if not isinstance(text, str):
        return ""
    # 替换换行符为<br>
    formatted_text = text.replace('\n', '<br>')
    # 使用正则表达式替换上标 (e.g., A^2 -> A<sup>2</sup>, B^n -> B<sup>n</sup>)
    formatted_text = re.sub(r'(\w+)\^([\w\d]+)', r'\1<sup>\2</sup>', formatted_text)
    # 使用正则表达式替换下标 (e.g., X_i -> X<sub>i</sub>, Y_1 -> Y<sub>1</sub>)
    formatted_text = re.sub(r'(\w+)_([\w\d]+)', r'\1<sub>\2</sub>', formatted_text)
    return formatted_text

def display_problem_details(self, item):
    problem_id = item.data(Qt.ItemDataRle.UserRole)
    problem = next((p for p in self.problems if p['id'] == problem_id), None)
    if not problem: self.details_area.setText("未找到题目详情。"); return
    
    # ... (获取统计数据的代码和之前一样) ...
    attempts = problem.get("attempts", 0); correct = problem.get("correct", 0)
    accuracy = f"{(correct / attempts * 100):.1f}%" if attempts > 0 else "N/A"
    is_saved = problem.get("is_saved", False); is_completed = correct > 0
    status_text = f"✅ 已完成" if is_completed else "❌ 未完成"; saved_text = "❤️ 已收藏" if is_saved else "🤍 未收藏"
    is_programming = problem.get("is_programming", False)
    
    # --- 【核心改动】在放入HTML前，对所有数据进行转义 ---
    title = html.escape(problem.get('title', ''))
    company = html.escape(problem.get('source', ''))
    tags = html.escape(', '.join(problem.get('tags', [])))
    description = html.escape(problem.get('description', '')).replace('\n', '<br>')
    
    html_content = f"""<h3>{title}</h3><p><b>公司:</b> {company}</p><p><b>标签:</b> {tags}</p><p><b>状态:</b> {status_text} | {saved_text} | <b>正确率:</b> {accuracy} ({correct}/{attempts})</p><hr><h3>描述</h3><p>{description}</p>"""
    
    if is_programming:
        # 代码部分不需要转义，<pre>标签会保留其格式
        py_solution = problem.get('python_solution', '')
        cpp_solution = problem.get('cpp_solution', '')
        html_content += f"""<hr><h3>Python 解法</h3><pre><code>{html.escape(py_solution)}</code></pre><hr><h3>C++ 解法</h3><pre><code>{html.escape(cpp_solution)}</code></pre>"""
    else:
        answer = html.escape(problem.get('answer', '')).replace('\n', '<br>')
        html_content += f"""<hr><h3>答案与解析</h3><p>{answer}</p>"""
        
    notes = html.escape(problem.get('notes', '')).replace('\n', '<br>')
    html_content += f"""<hr><h3>备注</h3><p>{notes}</p>"""
    self.details_area.setHtml(html_content)

PREDEFINED_TAGS = ["", "Math", "Probability", "Coding", "Finance", "Brain Teaser"]
class AddProblemDialog(QDialog):

    def __init__(self, all_problems, problem_data=None, parent=None):
        super().__init__(parent); self.problem_data = problem_data
        self.setWindowTitle("编辑题目" if self.problem_data else "添加新题目"); self.setMinimumWidth(600)
        self.layout = QFormLayout(self); self.title = QLineEdit(self)
        self.company_input = QLineEdit(self)
        all_companies = sorted(list({p.get("source", "").strip() for p in all_problems if p.get("source", "").strip()}))
        completer = QCompleter(all_companies, self); completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive); completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.company_input.setCompleter(completer)
        self.tags_selector = QComboBox(self); self.tags_selector.addItems(PREDEFINED_TAGS)
        self.description = QTextEdit(self); self.notes = QTextEdit(self)
        self.is_programming_checkbox = QCheckBox("Coding", self)
        self.answer_label = QLabel("答案与解析:"); self.answer_input = QTextEdit(self)
        self.code_input_layout = QHBoxLayout(); self.language_selector = QComboBox()
        self.language_selector.addItems(["Python", "C++"]); self.code_input_layout.addWidget(self.language_selector)
        self.code_label = QLabel("解法:"); self.code_input_area = QTextEdit(); self.code_input_area.setFontFamily("Courier New")
        self.python_code_buffer = ""; self.cpp_code_buffer = ""; self.current_language = "Python"
        self.layout.addRow("标题:", self.title); self.layout.addRow("公司:", self.company_input); self.layout.addRow("标签:", self.tags_selector)
        self.layout.addRow("描述:", self.description); self.layout.addRow(self.is_programming_checkbox); self.layout.addRow(self.answer_label, self.answer_input)
        self.layout.addRow(self.code_label, self.code_input_layout); self.layout.addRow(self.code_input_area)
        self.layout.addRow("备注:", self.notes)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.buttons.accepted.connect(self.accept); self.buttons.rejected.connect(self.reject)
        self.layout.addRow(self.buttons)
        self.is_programming_checkbox.stateChanged.connect(self.toggle_solution_fields); self.language_selector.currentTextChanged.connect(self.on_language_changed)
        if self.problem_data: self.populate_data()
        self.toggle_solution_fields()
    
    def get_data(self):
        self.on_language_changed(self.language_selector.currentText()); selected_tag = self.tags_selector.currentText()
        data = {"title": self.title.text().strip(), "source": self.company_input.text().strip(), "tags": [selected_tag] if selected_tag else [], "description": self.description.toPlainText().strip(), "notes": self.notes.toPlainText().strip(), "is_programming": self.is_programming_checkbox.isChecked()}
        if data["is_programming"]: data["python_solution"] = self.python_code_buffer.strip(); data["cpp_solution"] = self.cpp_code_buffer.strip(); data["answer"] = ""
        else: data["python_solution"] = ""; data["cpp_solution"] = ""; data["answer"] = self.answer_input.toPlainText().strip()
        if self.problem_data: data["attempts"] = self.problem_data.get("attempts", 0); data["correct"] = self.problem_data.get("correct", 0); data["is_saved"] = self.problem_data.get("is_saved", False)
        else: data["attempts"] = 0; data["correct"] = 0; data["is_saved"] = False
        return data
    
    def populate_data(self):
        self.title.setText(self.problem_data.get("title", "")); self.company_input.setText(self.problem_data.get("source", ""))
        tag = self.problem_data.get("tags", [""])[0]
        if tag in PREDEFINED_TAGS: self.tags_selector.setCurrentText(tag)
        self.description.setPlainText(self.problem_data.get("description", "")); self.notes.setPlainText(self.problem_data.get("notes", ""))
        is_coding = self.problem_data.get("is_programming", False); self.is_programming_checkbox.setChecked(is_coding)
        if is_coding: self.python_code_buffer = self.problem_data.get("python_solution", ""); self.cpp_code_buffer = self.problem_data.get("cpp_solution", ""); self.code_input_area.setPlainText(self.python_code_buffer)
        else: self.answer_input.setPlainText(self.problem_data.get("answer", ""))
    
    def on_language_changed(self, new_language):
        if self.current_language == "Python": self.python_code_buffer = self.code_input_area.toPlainText()
        elif self.current_language == "C++": self.cpp_code_buffer = self.code_input_area.toPlainText()
        if new_language == "Python": self.code_input_area.setPlainText(self.python_code_buffer)
        elif new_language == "C++": self.code_input_area.setPlainText(self.cpp_code_buffer)
        self.current_language = new_language
    
    def toggle_solution_fields(self):
        is_coding = self.is_programming_checkbox.isChecked()
        self.code_label.setVisible(is_coding); self.language_selector.setVisible(is_coding); self.code_input_area.setVisible(is_coding)
        self.answer_label.setVisible(not is_coding); self.answer_input.setVisible(not is_coding)

class EditorPage(QWidget):
    navigateToWelcome = pyqtSignal()
    def __init__(self): super().__init__(); self.problems = []; self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        # --- 按钮和控制区 ---
        controls_layout = QHBoxLayout()
        self.add_button = QPushButton("添加")
        self.edit_button = QPushButton("编辑")
        self.delete_button = QPushButton("删除")
        self.save_button = QPushButton("收藏/取消收藏")
        
        self.sort_label = QLabel("排序:")
        self.sort_combo = QComboBox()
        # --- 【核心改动】确保“按字母排序”是第一个选项 ---
        self.sort_combo.addItems([
            "按字母排序 (A-Z)",
            "正确率 (从低到高)",
            "错误次数 (从多到少)",
            "总次数 (从多到少)"
        ])

        self.filter_label = QLabel("筛选:")
        self.filter_combo = QComboBox()
        
        self.back_button = QPushButton("返回主菜单")

        # --- 布局 ---
        controls_layout.addWidget(self.add_button)
        controls_layout.addWidget(self.edit_button)
        controls_layout.addWidget(self.delete_button)
        controls_layout.addWidget(self.save_button)
        controls_layout.addStretch()
        controls_layout.addWidget(self.sort_label)
        controls_layout.addWidget(self.sort_combo)
        controls_layout.addWidget(self.filter_label)
        controls_layout.addWidget(self.filter_combo)
        controls_layout.addWidget(self.back_button)
        main_layout.addLayout(controls_layout)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.problem_list_widget = QListWidget()
        self.details_area = QTextEdit(); self.details_area.setReadOnly(True)
        splitter.addWidget(self.problem_list_widget); splitter.addWidget(self.details_area); splitter.setSizes([300, 900])
        main_layout.addWidget(splitter)
        
        # --- 连接信号 ---
        self.problem_list_widget.itemClicked.connect(self.display_problem_details)
        self.add_button.clicked.connect(self.show_add_dialog)
        self.edit_button.clicked.connect(self.show_edit_dialog)
        self.delete_button.clicked.connect(self.delete_selected_problem)
        self.save_button.clicked.connect(self.toggle_save_status)
        self.back_button.clicked.connect(self.navigateToWelcome.emit)
        
        self.sort_combo.currentIndexChanged.connect(self._refresh_problem_list)
        self.filter_combo.currentIndexChanged.connect(self._refresh_problem_list)

    def _validate_and_save_data(self, data, problem_id=None):
        if not data['title']:
            QMessageBox.warning(self, "错误", "标题不能为空！"); return False
        is_coding = data['is_programming']
        if is_coding and not data['python_solution'] and not data['cpp_solution']:
            QMessageBox.warning(self, "错误", "编程题至少需要提供一种代码解法！"); return False
        if not is_coding and not data['answer']:
            QMessageBox.warning(self, "错误", "非编程题必须提供答案与解析！"); return False
        
        if problem_id is None:
            new_id = max([p['id'] for p in self.problems], default=0) + 1
            data['id'] = new_id; self.problems.append(data)
        else:
            index_to_update = next((i for i, p in enumerate(self.problems) if p['id'] == problem_id), -1)
            if index_to_update != -1:
                data['id'] = problem_id; self.problems[index_to_update] = data
        save_problems(self.problems)
        return True

    def show_add_dialog(self):
        dialog = AddProblemDialog(self.problems, None, self)
        if dialog.exec():
            new_data = dialog.get_data()
            if self._validate_and_save_data(new_data):
                self.load_and_display_problems()

    def show_edit_dialog(self):
        """【核心改动】修复了编辑后刷新UI导致崩溃的Bug"""
        selected_items = self.problem_list_widget.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提示", "请先在左侧列表中选择一个要编辑的题目。")
            return
        
        problem_id_to_edit = selected_items[0].data(Qt.ItemDataRole.UserRole)
        problem_to_edit = next((p for p in self.problems if p['id'] == problem_id_to_edit), None)
        if not problem_to_edit:
            QMessageBox.critical(self, "错误", "找不到要编辑的题目数据。")
            return
        
        dialog = AddProblemDialog(self.problems, problem_to_edit, self)
        if dialog.exec():
            updated_data = dialog.get_data()
            # 调用验证和保存，如果成功再继续
            if self._validate_and_save_data(updated_data, problem_id_to_edit):
                # 重新加载列表
                self.load_and_display_problems()
                
                # 在新列表中找到并重新选中该项
                new_item_to_select = None
                for i in range(self.problem_list_widget.count()):
                    item = self.problem_list_widget.item(i)
                    if item.data(Qt.ItemDataRole.UserRole) == problem_id_to_edit:
                        new_item_to_select = item
                        break
                
                if new_item_to_select:
                    self.problem_list_widget.setCurrentItem(new_item_to_select)
                    self.display_problem_details(new_item_to_select)

    def toggle_save_status(self):
        selected_items = self.problem_list_widget.selectedItems()
        if not selected_items: QMessageBox.information(self, "提示", "请先在左侧列表中选择一个题目。"); return
        problem_id_to_find = selected_items[0].data(Qt.ItemDataRole.UserRole)
        toggle_problem_saved_status(problem_id_to_find)
        self.load_and_display_problems()
        new_item_to_select = None
        for i in range(self.problem_list_widget.count()):
            item = self.problem_list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == problem_id_to_find:
                new_item_to_select = item; break
        if new_item_to_select:
            self.problem_list_widget.setCurrentItem(new_item_to_select)
            self.display_problem_details(new_item_to_select)
        else: self.details_area.clear()

    def load_and_display_problems(self):
        self.problems = load_problems()
        
        # 动态更新公司筛选列表
        # 先断开信号，避免填充时触发刷新
        self.filter_combo.blockSignals(True)
        current_filter = self.filter_combo.currentText()
        self.filter_combo.clear()
        
        # 添加固定选项
        self.filter_combo.addItem("显示全部")
        self.filter_combo.addItem("只显示收藏的")
        self.filter_combo.addItem("只显示未完成的")
        
        # 添加所有公司作为筛选选项
        all_companies = sorted(list({p.get("source", "").strip() for p in self.problems if p.get("source", "").strip()}))
        self.filter_combo.addItems(all_companies)
        
        # 尝试恢复之前的筛选选项
        if current_filter in [self.filter_combo.itemText(i) for i in range(self.filter_combo.count())]:
            self.filter_combo.setCurrentText(current_filter)
        
        # 重新连接信号
        self.filter_combo.blockSignals(False)
        
        # 调用核心函数刷新列表
        self._refresh_problem_list()

    def display_problem_details(self, item):
        problem_id = item.data(Qt.ItemDataRole.UserRole)
        problem = next((p for p in self.problems if p['id'] == problem_id), None)
        if not problem: self.details_area.setText("未找到题目详情。"); return
        
        attempts = problem.get("attempts", 0); correct = problem.get("correct", 0)
        accuracy = f"{(correct / attempts * 100):.1f}%" if attempts > 0 else "N/A"
        is_saved = problem.get("is_saved", False); is_completed = correct > 0
        status_text = f"✅ 已完成" if is_completed else "❌ 未完成"; saved_text = "❤️ 已收藏" if is_saved else "🤍 未收藏"
        is_programming = problem.get("is_programming", False)
        
        # --- 【核心改动】对所有从json读取的数据进行转义 ---
        title = html.escape(problem.get('title', ''))
        company = html.escape(problem.get('source', ''))
        tags = html.escape(', '.join(problem.get('tags', [])))
        description = html.escape(problem.get('description', '')).replace('\n', '<br>')
        
        # --- 【核心改动】将 <h1> 换成 <h3> ---
        html_content = f"""<h3>{title}</h3><p><b>公司:</b> {company}</p><p><b>标签:</b> {tags}</p><p><b>状态:</b> {status_text} | {saved_text} | <b>正确率:</b> {accuracy} ({correct}/{attempts})</p><hr><h3>描述</h3><p>{description}</p>"""
        
        if is_programming:
            py_solution = problem.get('python_solution', '')
            cpp_solution = problem.get('cpp_solution', '')
            html_content += f"""<hr><h3>Python 解法</h3><pre><code>{html.escape(py_solution)}</code></pre><hr><h3>C++ 解法</h3><pre><code>{html.escape(cpp_solution)}</code></pre>"""
        else:
            answer = html.escape(problem.get('answer', '')).replace('\n', '<br>')
            html_content += f"""<hr><h3>答案与解析</h3><p>{answer}</p>"""
            
        notes = html.escape(problem.get('notes', '')).replace('\n', '<br>')
        html_content += f"""<hr><h3>备注</h3><p>{notes}</p>"""
        self.details_area.setHtml(html_content)

    def delete_selected_problem(self):
        selected_items = self.problem_list_widget.selectedItems();
        if not selected_items: QMessageBox.information(self, "提示", "请先在左侧列表中选择一个要删除的题目。"); return
        selected_item = selected_items[0]; problem_id = selected_item.data(Qt.ItemDataRole.UserRole); problem_title = selected_item.text()
        reply = QMessageBox.question(self, '确认删除', f"你确定要删除题目 '{problem_title}' 吗？\n这个操作无法撤销。", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.problems = [p for p in self.problems if p['id'] != problem_id]
            save_problems(self.problems); self.load_and_display_problems(); self.details_area.clear()

    def _refresh_problem_list(self):
        """核心函数：根据当前的排序和筛选条件，刷新问题列表"""
        filter_text = self.filter_combo.currentText()
        sort_text = self.sort_combo.currentText()
        
        display_list = self.problems.copy()

        # --- 筛选逻辑 (不变) ---
        if filter_text == "只显示收藏的":
            display_list = [p for p in display_list if p.get('is_saved', False)]
        elif filter_text == "只显示未完成的":
            display_list = [p for p in display_list if p.get('correct', 0) == 0]
        elif filter_text not in ["显示全部", ""]:
            display_list = [p for p in display_list if p.get('source', '') == filter_text]
            
        # --- 排序逻辑 ---
        if sort_text == "正确率 (从低到高)":
            def sort_key(p):
                attempts = p.get('attempts', 0)
                return p.get('correct', 0) / attempts if attempts > 0 else 1.0
            display_list.sort(key=sort_key)
        elif sort_text == "错误次数 (从多到少)":
            display_list.sort(key=lambda p: p.get('attempts', 0) - p.get('correct', 0), reverse=True)
        elif sort_text == "总次数 (从多到少)":
            display_list.sort(key=lambda p: p.get('attempts', 0), reverse=True)
        else: # 默认的 "按字母排序 (A-Z)"
            # --- 【核心改动】使用新的自然排序函数 ---
            display_list.sort(key=natural_sort_key)

        # --- 刷新UI列表的逻辑 (不变) ---
        self.problem_list_widget.clear()
        for p in display_list:
            item = QListWidgetItem() 
            item.setData(Qt.ItemDataRole.UserRole, p['id'])
            label = QLabel()
            escaped_title = html.escape(p['title'])
            if p.get('is_saved', False):
                label.setText(f"❤️ {escaped_title}")
            else:
                label.setText(escaped_title)
            self.problem_list_widget.addItem(item)
            self.problem_list_widget.setItemWidget(item, label)

