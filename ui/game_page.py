# ui/game_page.py

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QFont

class GamePage(QWidget):
    """游戏练习页面 (占位符)"""
    navigateToWelcome = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("游戏页面\n功能开发中...")
        label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        back_button = QPushButton("返回主菜单")
        back_button.setFixedSize(200, 50)
        back_button.clicked.connect(self.navigateToWelcome.emit)
        
        layout.addWidget(label)
        layout.addSpacing(40)
        layout.addWidget(back_button)