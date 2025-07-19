# ui/welcome_page.py

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QFont

class WelcomePage(QWidget):
    """欢迎页面，提供导航按钮"""
    # 自定义信号，用于通知主窗口切换页面
    navigateToEditor = pyqtSignal()
    navigateToPractice = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("欢迎使用 Quant 题库")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_edit = QPushButton("1. 修改题库")
        btn_practice = QPushButton("2. 开始练习")
        
        btn_edit.setFixedSize(200, 50)
        btn_practice.setFixedSize(200, 50)

        # 连接按钮点击事件到信号的发射
        btn_edit.clicked.connect(self.navigateToEditor.emit)
        btn_practice.clicked.connect(self.navigateToPractice.emit)

        layout.addWidget(title)
        layout.addSpacing(40)
        layout.addWidget(btn_edit)
        layout.addSpacing(20)
        layout.addWidget(btn_practice)