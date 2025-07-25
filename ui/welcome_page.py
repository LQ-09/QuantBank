# ui/welcome_page.py

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QInputDialog
from PyQt6.QtGui import QFont
from logic.data_manager import clear_game_stats, reset_problem_practice_stats

class WelcomePage(QWidget):
    """欢迎页面，已增加统计页面入口"""
    navigateToEditor = pyqtSignal()
    navigateToPractice = pyqtSignal()
    navigateToStats = pyqtSignal() # <-- 新增信号

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("欢迎使用 Quant 题库")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_edit = QPushButton("1. 修改题库")
        btn_practice = QPushButton("2. 开始练习")
        btn_stats = QPushButton("3. 查看统计") # <-- 新增按钮
        btn_clear = QPushButton("清除记录")
        
        button_size = (200, 50)
        btn_edit.setFixedSize(*button_size)
        btn_practice.setFixedSize(*button_size)
        btn_stats.setFixedSize(*button_size)
        btn_clear.setFixedSize(*button_size)

        btn_edit.clicked.connect(self.navigateToEditor.emit)
        btn_practice.clicked.connect(self.navigateToPractice.emit)
        btn_stats.clicked.connect(self.navigateToStats.emit) # <-- 连接新信号
        btn_clear.clicked.connect(self.handle_clear_records)

        layout.addWidget(title); layout.addSpacing(40)
        layout.addWidget(btn_edit); layout.addSpacing(20)
        layout.addWidget(btn_practice); layout.addSpacing(20)
        layout.addWidget(btn_stats); layout.addSpacing(20) # <-- 添加到布局
        layout.addWidget(btn_clear)

    def handle_clear_records(self):
        # ... (这个方法和之前一样，无需改动) ...
        options = ["清除所有游戏历史记录 (Game Stats)", "重置所有题目练习统计 (Problem Stats)", "取消"]
        choice, ok = QInputDialog.getItem(self, "选择要清除的记录", "请选择一项操作:", options, 0, False)
        if ok and choice:
            if choice == options[0]:
                reply = QMessageBox.question(self, "确认操作", "你确定要删除所有的游戏得分和历史记录吗？\n这个操作无法撤销。", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes: clear_game_stats(); QMessageBox.information(self, "成功", "所有游戏历史记录已被清空。")
            elif choice == options[1]:
                reply = QMessageBox.question(self, "确认操作", "你确定要将所有题目的练习次数归零吗？\n（收藏状态将保留）这个操作无法撤销。", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes: reset_problem_practice_stats(); QMessageBox.information(self, "成功", "所有题目的练习统计已归零。")