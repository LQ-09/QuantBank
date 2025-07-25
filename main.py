# main.py

# 打包指令
# pyinstaller --distpath "./output/dist" --workpath "./output/build" QuantApp.spec


import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui.welcome_page import WelcomePage
from ui.editor_page import EditorPage
from ui.practice_menu_page import PracticeMenuPage
from ui.practice_page import PracticePage
from ui.game_page import GamePage
from ui.stats_page import StatsPage # <-- 导入新页面


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Quant 面试题库'); self.setGeometry(100, 100, 900, 700)
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.welcome_page = WelcomePage(); self.editor_page = EditorPage()
        self.practice_menu_page = PracticeMenuPage(); self.practice_page = PracticePage()
        self.game_page = GamePage(); self.stats_page = StatsPage() # <-- 创建新页面实例
        
        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.editor_page)
        self.stacked_widget.addWidget(self.practice_menu_page)
        self.stacked_widget.addWidget(self.practice_page)
        self.stacked_widget.addWidget(self.game_page)
        self.stacked_widget.addWidget(self.stats_page) # <-- 添加到页面栈
        
        self.welcome_page.navigateToEditor.connect(self.go_to_editor_page)
        self.welcome_page.navigateToPractice.connect(self.go_to_practice_menu_page)
        self.welcome_page.navigateToStats.connect(self.go_to_stats_page) # <-- 连接新信号
        
        self.practice_menu_page.navigateToWelcome.connect(self.go_to_welcome_page)
        self.practice_menu_page.startPracticeSession.connect(self.start_actual_practice_session)
        self.practice_menu_page.navigateToGame.connect(self.go_to_game_page)
        
        self.editor_page.navigateToWelcome.connect(self.go_to_welcome_page)
        self.practice_page.navigateToWelcome.connect(self.go_to_welcome_page)
        self.game_page.navigateToWelcome.connect(self.go_to_welcome_page)
        self.stats_page.navigateToWelcome.connect(self.go_to_welcome_page) # <-- 连接新页面的返回信号
        
        self.go_to_welcome_page()

    def go_to_stats_page(self): # <-- 新增跳转方法
        """跳转到统计页面并刷新数据"""
        self.stats_page.load_and_display_stats()
        self.stacked_widget.setCurrentWidget(self.stats_page)

    # (其他跳转方法和之前一样)
    def go_to_welcome_page(self): self.stacked_widget.setCurrentWidget(self.welcome_page)
    def go_to_editor_page(self):
        self.editor_page.load_and_display_problems()
        self.stacked_widget.setCurrentWidget(self.editor_page)
    def go_to_practice_menu_page(self): self.stacked_widget.setCurrentWidget(self.practice_menu_page)
    def start_actual_practice_session(self, category):
        self.practice_page.set_practice_category(category)
        self.practice_page.show_next_problem()
        self.stacked_widget.setCurrentWidget(self.practice_page)
    def go_to_game_page(self):
        self.stacked_widget.setCurrentWidget(self.game_page)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())