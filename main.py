# main.py

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

# 【改动1】导入新的菜单页面
from ui.welcome_page import WelcomePage
from ui.editor_page import EditorPage
from ui.practice_menu_page import PracticeMenuPage
from ui.practice_page import PracticePage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Quant 面试题库')
        self.setGeometry(100, 100, 1200, 800)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 【改动2】创建所有页面实例，包括新的菜单页
        self.welcome_page = WelcomePage()
        self.editor_page = EditorPage()
        self.practice_menu_page = PracticeMenuPage()
        self.practice_page = PracticePage()
        
        self.stacked_widget.addWidget(self.welcome_page)       # index 0
        self.stacked_widget.addWidget(self.editor_page)        # index 1
        self.stacked_widget.addWidget(self.practice_menu_page) # index 2
        self.stacked_widget.addWidget(self.practice_page)      # index 3

        # 【改动3】连接所有页面的信号
        self.welcome_page.navigateToEditor.connect(self.go_to_editor_page)
        # "开始练习"按钮现在会跳转到练习子菜单
        self.welcome_page.navigateToPractice.connect(self.go_to_practice_menu_page)
        
        # 新的菜单页的信号连接
        self.practice_menu_page.navigateToWelcome.connect(self.go_to_welcome_page)
        self.practice_menu_page.startPracticeSession.connect(self.start_actual_practice_session)
        
        self.editor_page.navigateToWelcome.connect(self.go_to_welcome_page)
        self.practice_page.navigateToWelcome.connect(self.go_to_welcome_page)
        
        self.go_to_welcome_page()

    # --- 【改动4】更新和新增导航方法 ---
    def go_to_welcome_page(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def go_to_editor_page(self):
        self.editor_page.load_and_display_problems()
        self.stacked_widget.setCurrentIndex(1)
        
    def go_to_practice_menu_page(self):
        self.stacked_widget.setCurrentIndex(2)

    def start_actual_practice_session(self, category):
        """启动一个特定类别的练习"""
        # 1. 告诉练习页面要练习哪个类别
        self.practice_page.set_practice_category(category)
        # 2. 让它立即显示第一道随机题
        self.practice_page.show_random_problem()
        # 3. 切换到练习页面
        self.stacked_widget.setCurrentIndex(3)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())