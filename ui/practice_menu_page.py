# ui/practice_menu_page.py

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QFont

class PracticeMenuPage(QWidget):
    """练习子菜单页面 (已更新类别)"""
    startPracticeSession = pyqtSignal(str)
    navigateToGame = pyqtSignal()
    navigateToWelcome = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("请选择练习类别")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- 【改动1】修改和新增按钮 ---
        btn_math = QPushButton("1. Math") # <-- 文本已修改
        btn_prob = QPushButton("2. Probability")
        btn_coding = QPushButton("3. Coding")
        btn_finance = QPushButton("4. Finance") # <-- 新增按钮
        btn_game = QPushButton("5. Game")
        btn_back = QPushButton("返回主菜单")
        
        button_size = (250, 50)
        btn_math.setFixedSize(*button_size)
        btn_prob.setFixedSize(*button_size)
        btn_coding.setFixedSize(*button_size)
        btn_finance.setFixedSize(*button_size) # 设置大小
        btn_game.setFixedSize(*button_size)
        btn_back.setFixedSize(*button_size)

        # --- 【改动2】连接新按钮的信号 ---
        btn_math.clicked.connect(lambda: self.startPracticeSession.emit("math"))
        btn_prob.clicked.connect(lambda: self.startPracticeSession.emit("probability"))
        btn_coding.clicked.connect(lambda: self.startPracticeSession.emit("coding"))
        btn_finance.clicked.connect(lambda: self.startPracticeSession.emit("finance")) # <-- 新增连接
        btn_game.clicked.connect(self.navigateToGame.emit)
        btn_back.clicked.connect(self.navigateToWelcome.emit)

        # --- 【改动3】更新布局 ---
        layout.addWidget(title)
        layout.addSpacing(40)
        layout.addWidget(btn_math)
        layout.addSpacing(20)
        layout.addWidget(btn_prob)
        layout.addSpacing(20)
        layout.addWidget(btn_coding)
        layout.addSpacing(20)
        layout.addWidget(btn_finance) # <-- 添加到布局
        layout.addSpacing(20)
        layout.addWidget(btn_game)
        layout.addSpacing(40)
        layout.addWidget(btn_back)