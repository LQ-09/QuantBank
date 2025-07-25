# ui/stats_page.py

import datetime
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox)
from PyQt6.QtGui import QFont

# --- 【核心】引入matplotlib和它与PyQt的集成组件 ---
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体为黑体
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

# 确保matplotlib使用Qt Agg后端
matplotlib.use('QtAgg')

# 从我们的逻辑层导入新的聚合函数
from logic.data_manager import get_game_sessions

class StatsPage(QWidget):
    """用于显示游戏历史分数走势图的页面"""
    navigateToWelcome = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.sessions_data = []
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        # --- 1. 顶部标题和控制区 ---
        top_layout = QHBoxLayout()
        title = QLabel("游戏得分走势")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        
        self.refresh_button = QPushButton("刷新数据")
        self.back_button = QPushButton("返回主菜单")
        
        top_layout.addWidget(title); top_layout.addStretch()
        top_layout.addWidget(self.refresh_button); top_layout.addWidget(self.back_button)
        main_layout.addLayout(top_layout)
        
        # --- 2. 统计摘要区 ---
        self.summary_label = QLabel("摘要: 暂无数据")
        main_layout.addWidget(self.summary_label)
        
        # --- 3. Matplotlib 图表画布 ---
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        main_layout.addWidget(self.canvas)
        
        # --- 连接信号 ---
        self.refresh_button.clicked.connect(self.load_and_display_stats)
        self.back_button.clicked.connect(self.navigateToWelcome.emit)
     

     # 在 StatsPage 类中

    def load_and_display_stats(self):
        """从文件加载统计数据并刷新图表 (已更新为使用局数作为X轴)"""
        self.sessions_data = get_game_sessions()
        
        if not self.sessions_data:
            self.ax.clear()
            self.ax.text(0.5, 0.5, '暂无游戏记录', horizontalalignment='center', verticalalignment='center')
            self.canvas.draw()
            self.summary_label.setText("摘要: 暂无数据")
            return

        # --- 【核心改动】准备绘图数据 ---
        # 按时间顺序排序，确保局数是正确的先后顺序
        self.sessions_data.sort(key=lambda x: x['timestamp'])
        
        scores = [session["total_score"] for session in self.sessions_data]
        # X轴现在是简单的局数序号 (1, 2, 3, ...)
        session_numbers = list(range(1, len(scores) + 1))

        # --- 绘制图表 ---
        self.ax.clear()
        self.ax.plot(session_numbers, scores, marker='o', linestyle='-', color='b')
        
        # --- 美化图表 (更新标签) ---
        self.ax.set_title("每局游戏总分走势", fontsize=16)
        self.ax.set_xlabel("游戏局数", fontsize=12) # <-- X轴标签已修改
        self.ax.set_ylabel("总分 (10轮)", fontsize=12)
        self.ax.grid(True)
        # self.figure.autofmt_xdate() # <-- 不再需要日期格式化

        # 让X轴的刻度显示为整数
        if session_numbers:
            self.ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        
        self.canvas.draw()
        
        # --- 更新摘要 ---
        total_sessions = len(scores)
        avg_score = sum(scores) / total_sessions if total_sessions > 0 else 0
        self.summary_label.setText(f"总局数: {total_sessions} | 平均每局得分: {avg_score:.0f}")

        