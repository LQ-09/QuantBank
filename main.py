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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Quant 面试题库')
        self.setGeometry(100, 100, 900, 700)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.welcome_page = WelcomePage()
        self.editor_page = EditorPage()
        self.practice_menu_page = PracticeMenuPage()
        self.practice_page = PracticePage()
        self.game_page = GamePage()
        
        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.editor_page)
        self.stacked_widget.addWidget(self.practice_menu_page)
        self.stacked_widget.addWidget(self.practice_page)
        self.stacked_widget.addWidget(self.game_page)

        self.welcome_page.navigateToEditor.connect(self.go_to_editor_page)
        self.welcome_page.navigateToPractice.connect(self.go_to_practice_menu_page)
        
        self.practice_menu_page.navigateToWelcome.connect(self.go_to_welcome_page)
        self.practice_menu_page.startPracticeSession.connect(self.start_actual_practice_session)
        self.practice_menu_page.navigateToGame.connect(self.go_to_game_page)
        
        self.editor_page.navigateToWelcome.connect(self.go_to_welcome_page)
        self.practice_page.navigateToWelcome.connect(self.go_to_welcome_page)
        self.game_page.navigateToWelcome.connect(self.go_to_welcome_page)
        
        self.go_to_welcome_page()

    def go_to_welcome_page(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def go_to_editor_page(self):
        self.editor_page.load_and_display_problems()
        self.stacked_widget.setCurrentIndex(1)
        
    def go_to_practice_menu_page(self):
        self.stacked_widget.setCurrentIndex(2)

    def start_actual_practice_session(self, category):
        self.practice_page.set_practice_category(category)
        # --- 【改动在这里】使用正确的函数名 ---
        self.practice_page.show_next_problem()
        self.stacked_widget.setCurrentIndex(3)

    def go_to_game_page(self):
        self.stacked_widget.setCurrentIndex(4)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())