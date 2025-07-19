# ui/game_page.py

import random
import time
import datetime
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette, QDrag, QPixmap
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QFrame
from logic.data_manager import add_game_record

# 文件: ui/game_page.py

# ... (imports) ...

# 【最终修正版】关卡库 - 严格遵守所有规则（单列<=4, 总数3-9）
LEVELS = {
    "easy": [
        {"id": "E01", "initial": [[1], [2], [3]], "target": [[3, 2, 1], [], []], "optimal": 5},
        {"id": "E02", "initial": [[2, 1], [], []], "target": [[], [1, 2], []], "optimal": 3},
        {"id": "E03", "initial": [[3, 1], [2], []], "target": [[3, 2, 1], [], []], "optimal": 4},
        {"id": "E04", "initial": [[4, 1], [2], [3]], "target": [[4, 3, 2, 1], [], []], "optimal": 6},
        {"id": "E05", "initial": [[3, 2, 1], [], []], "target": [[1], [2], [3]], "optimal": 8}
    ],
    "medium": [
        {"id": "M01", "initial": [[1, 2, 3], [], []], "target": [[3, 2, 1], [], []], "optimal": 7},
        {"id": "M02", "initial": [[4, 3, 2, 1], [], []], "target": [[4, 3], [2, 1], []], "optimal": 7},
        {"id": "M03", "initial": [[3], [2], [4, 1]], "target": [[4, 3, 2, 1], [], []], "optimal": 9},
        {"id": "M04", "initial": [[2, 1], [4, 3], []], "target": [[1, 2], [3, 4], []], "optimal": 8},
        {"id": "M05", "initial": [[5, 1], [4, 2], [3]], "target": [[4, 3, 2, 1], [5], []], "optimal": 12}
    ],
    "hard": [
        # Hard关卡现在使用了更多的方块总数，且目标状态也遵守规则
        {"id": "H01", "initial": [[6, 5, 4], [3, 2, 1], []], "target": [[], [6, 5, 4], [3, 2, 1]], "optimal": 13},
        {"id": "H02", "initial": [[4, 3], [5, 2], [1]], "target": [[5, 4], [3, 2], [1]], "optimal": 15},
        {"id": "H03", "initial": [[1, 2, 3, 4], [5, 6, 7], []], "target": [[7, 6, 5], [4, 3, 2, 1], []], "optimal": 18},
        {"id": "H04", "initial": [[8, 7], [6, 5], [4, 3, 2, 1]], "target": [[8, 7, 6, 5], [4, 3, 2, 1], []], "optimal": 10},
        {"id": "H05", "initial": [[3, 2, 1], [6, 5, 4], [9, 8, 7]], "target": [[9, 6, 3], [8, 5, 2], [7, 4, 1]], "optimal": 24}
    ]
}

# ... (后续所有类的代码，如 BlockWidget, ColumnWidget, GamePage 等，都保持不变) ...

class BlockWidget(QLabel):
    # (这个类和之前完全一样，无需改动)
    def __init__(self, block_id, color, game_page):
        super().__init__(f"Block {block_id}"); self.block_id = block_id; self.game_page = game_page
        self.setAlignment(Qt.AlignmentFlag.AlignCenter); self.setFont(QFont("Arial", 12, QFont.Weight.Bold)); self.setFixedSize(120, 40)
        palette = self.palette(); palette.setColor(QPalette.ColorRole.Window, QColor(color)); palette.setColor(QPalette.ColorRole.WindowText, QColor("black"))
        self.setAutoFillBackground(True); self.setPalette(palette)
        
    def mousePressEvent(self, event):
        parent_column_widget = self.parentWidget();
        if not isinstance(parent_column_widget, ColumnWidget): return
        column_index = parent_column_widget.index; column_data = self.game_page.current_columns[column_index]
        if column_data and column_data[-1] == self.block_id:
            drag = QDrag(self); mime_data = QMimeData()
            mime_data.setText(f"{self.block_id},{column_index}"); drag.setMimeData(mime_data)
            pixmap = QPixmap(self.size()); self.render(pixmap)
            drag.setPixmap(pixmap); drag.setHotSpot(event.position().toPoint()); drag.exec(Qt.DropAction.MoveAction)

class ColumnWidget(QFrame):
    # (这个类和之前完全一样，无需改动)
    blockDropped = pyqtSignal(int, int, int)

    def __init__(self, index, max_height=4):
        super().__init__(); self.index = index; self.max_height = max_height
        self.setFrameShape(QFrame.Shape.Box); self.setAcceptDrops(True); self.setMinimumWidth(150)
        self.layout = QVBoxLayout(self); self.layout.setContentsMargins(5,5,5,5); self.layout.setSpacing(5)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText(): event.acceptProposedAction()
    def dropEvent(self, event):
        current_block_count = sum(1 for i in range(self.layout.count()) if isinstance(self.layout.itemAt(i).widget(), BlockWidget))
        if current_block_count >= self.max_height: return
        mime_text = event.mimeData().text(); block_id, src_col = map(int, mime_text.split(','))
        self.blockDropped.emit(block_id, src_col, self.index)

    def update_display(self, block_ids, colors, game_page):
        """用新的方块列表更新此列的显示 (最终修正版)"""
        # 1. 清理旧的方块和伸缩条
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else: # 清理伸缩条等非widget项目
                self.layout.removeItem(item)
        
        # 2. 先在布局的顶部添加一个伸缩弹簧
        self.layout.addStretch()

        # 3. 【核心修正】从数据列表的末尾(顶部)开始，反向遍历
        # 这样视觉上最上面的方块，就是数据里最后面的那个
        for block_id in reversed(block_ids):
            block = BlockWidget(block_id, colors.get(block_id, "#AAAAAA"), game_page)
            # 将方块添加到伸缩弹簧的下方，并使其水平居中
            self.layout.addWidget(block, 0, Qt.AlignmentFlag.AlignHCenter)

class GamePage(QWidget):
    navigateToWelcome = pyqtSignal()
    def __init__(self):
        super().__init__()
        # --- 【核心改动】扩展颜色字典以支持最多9个方块 ---
        self.colors = {
            1: "#33C4FF", 2: "#A2FF33", 3: "#FFC300", 4: "#FF5733", 5:"#C70039",
            6:"#900C3F", 7:"#581845", 8:"#DAF7A6", 9:"#FFC0CB"
        }
        self.levels = LEVELS; self.column_widgets = []
        self.session_length = 10; self.current_round = 0; self.session_score = 0
        self.score_map = {"easy": 100, "medium": 300, "hard": 500}
        self.current_difficulty = "medium"; self.current_level_data = None; self.game_in_progress = False
        self.timer = QTimer(self); self.timer.timeout.connect(self._update_timer_display); self.start_time = 0
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        # --- 状态栏 ---
        status_layout = QHBoxLayout()
        self.round_label = QLabel("回合: 0/10")
        self.score_label = QLabel("本局得分: 0")
        self.difficulty_label = QLabel(f"当前难度: Medium")
        self.timer_label = QLabel("时间: 0.0s")
        self.status_label = QLabel("移动次数: 0")
        self.start_button = QPushButton("开始10轮挑战")
        self.skip_button = QPushButton("跳过本轮") # <-- 新增按钮
        self.back_button = QPushButton("返回主菜单")
        
        status_layout.addWidget(self.round_label)
        status_layout.addWidget(self.score_label)
        status_layout.addWidget(self.difficulty_label)
        status_layout.addWidget(self.timer_label)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.start_button)
        status_layout.addWidget(self.skip_button) # <-- 添加到布局
        status_layout.addWidget(self.back_button)
        main_layout.addLayout(status_layout)
        
        # ... (后续的游戏区域布局和之前完全一样) ...
        game_area_layout = QVBoxLayout(); target_group = QFrame(); target_group.setFrameShape(QFrame.Shape.StyledPanel)
        target_layout = QVBoxLayout(target_group); self.target_display_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("目标状态 (Target)")); target_layout.addLayout(self.target_display_layout)
        current_group = QFrame(); current_group.setFrameShape(QFrame.Shape.StyledPanel)
        current_layout = QVBoxLayout(current_group); self.current_display_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("你的操作区 (Current)")); current_layout.addLayout(self.current_display_layout)
        for i in range(3):
            column_widget = ColumnWidget(index=i); column_widget.blockDropped.connect(self.handle_drop)
            self.current_display_layout.addWidget(column_widget); self.column_widgets.append(column_widget)
        game_area_layout.addWidget(target_group, stretch=1); game_area_layout.addWidget(current_group, stretch=2)
        main_layout.addLayout(game_area_layout)

        self.start_button.clicked.connect(self.start_game_session)
        self.skip_button.clicked.connect(self.skip_level) # <-- 连接新按钮的信号
        self.back_button.clicked.connect(self.navigateToWelcome.emit)

    def start_game_session(self):
        self.current_round = 0; self.session_score = 0; self.current_difficulty = "medium"
        self.start_button.setText("重新开始本局"); self._load_next_round()
    
    def _load_next_round(self):
        self.game_in_progress = True; self.current_round += 1
        level_pool = self.levels.get(self.current_difficulty, self.levels['medium'])
        self.current_level_data = random.choice(level_pool)
        initial = self.current_level_data['initial']; target = self.current_level_data['target']
        self.target_columns = target; self.current_columns = [list(col) for col in initial]
        self.move_count = 0; self.start_time = time.time(); self.timer.start(100)
        self.round_label.setText(f"回合: {self.current_round}/{self.session_length}")
        self.score_label.setText(f"本局得分: {self.session_score}")
        self.difficulty_label.setText(f"当前难度: {self.current_difficulty.capitalize()}"); self._update_ui()
    
    def check_win_condition(self):
        if self.current_columns == self.target_columns:
            self.game_in_progress = False; self.timer.stop(); time_taken = time.time() - self.start_time
            optimal_moves = self.current_level_data.get('optimal', self.move_count)
            base_score = self.score_map.get(self.current_difficulty, 100)
            penalty = max(0, self.move_count - optimal_moves) * 10
            final_score = max(0, base_score - penalty); self.session_score += final_score
            record = {"timestamp": datetime.datetime.utcnow().isoformat(), "level_id": self.current_level_data.get('id', 'unknown'), "difficulty": self.current_difficulty, "time_taken": round(time_taken, 2), "moves_taken": self.move_count, "optimal_moves": optimal_moves, "score": final_score }
            add_game_record(record)
            previous_difficulty = self.current_difficulty
            if time_taken < 30: self.current_difficulty = "hard" if self.current_difficulty == "medium" else "medium"
            elif time_taken > 60: self.current_difficulty = "easy" if self.current_difficulty == "medium" else "medium"
            if self.current_round >= self.session_length:
                self.score_label.setText(f"最终得分: {self.session_score}")
                QMessageBox.information(self, "本局结束！", f"恭喜你完成了10轮挑战！\n\n你的最终总分是: {self.session_score}")
                self.start_button.setText("开始新一局游戏")
            else: self._load_next_round()
    
    def _update_ui(self):
        self._draw_static_towers(self.target_display_layout, self.target_columns)
        for i, column_widget in enumerate(self.column_widgets): column_widget.update_display(self.current_columns[i], self.colors, self)
        self.status_label.setText(f"移动次数: {self.move_count}")
    
    def _update_timer_display(self):
        if self.game_in_progress: elapsed = time.time() - self.start_time; self.timer_label.setText(f"时间: {elapsed:.1f}s")
    
    def handle_drop(self, block_id, src_col, dest_col):
        if not self.game_in_progress or src_col == dest_col: return
        if self.current_columns[src_col] and self.current_columns[src_col][-1] == block_id:
            block = self.current_columns[src_col].pop()
            self.current_columns[dest_col].append(block)
            self.move_count += 1; self._update_ui(); self.check_win_condition()
    
    def _draw_static_towers(self, parent_layout, columns_data):
        while parent_layout.count() > 0:
            item = parent_layout.takeAt(0); widget = item.widget()
            if widget: widget.deleteLater()
            else: parent_layout.removeItem(item)
        parent_layout.addStretch()
        for column_list in columns_data:
            col_container = QFrame(); col_container.setFrameShape(QFrame.Shape.Box); col_container.setMinimumWidth(150)
            col_v_layout = QVBoxLayout(col_container); col_v_layout.addStretch()
            for block_id in reversed(column_list):
                block = QLabel(f"Block {block_id}"); block.setAlignment(Qt.AlignmentFlag.AlignCenter); block.setFont(QFont("Arial", 12, QFont.Weight.Bold)); block.setFixedSize(120, 40)
                palette = block.palette(); palette.setColor(QPalette.ColorRole.Window, QColor(self.colors.get(block_id))); palette.setColor(QPalette.ColorRole.WindowText, QColor("black"))
                block.setAutoFillBackground(True); block.setPalette(palette)
                col_v_layout.addWidget(block, 0, Qt.AlignmentFlag.AlignHCenter)
            parent_layout.addWidget(col_container)
        parent_layout.addStretch()

    # 在 GamePage 类中 (这是一个全新的方法)

    def skip_level(self):
        """处理“跳过本轮”按钮的点击事件"""
        if not self.game_in_progress:
            QMessageBox.information(self, "提示", "请先开始一局游戏。")
            return

        self.game_in_progress = False
        self.timer.stop()
        
        # --- 1. 记录后台数据 ---
        record = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "level_id": self.current_level_data.get('id', 'unknown'),
            "difficulty": self.current_difficulty,
            "time_taken": "skipped",
            "moves_taken": self.move_count,
            "optimal_moves": self.current_level_data.get('optimal', -1),
            "score": 0 # 跳过得0分
        }
        add_game_record(record)

        # --- 2. 降低下一轮难度 ---
        if self.current_difficulty == "hard":
            self.current_difficulty = "medium"
        elif self.current_difficulty == "medium":
            self.current_difficulty = "easy"
        # 如果已经是 "easy"，则保持不变
        
        # --- 3. 检查是否整局游戏结束 ---
        if self.current_round >= self.session_length:
            self.score_label.setText(f"最终得分: {self.session_score}")
            QMessageBox.information(self, "本局结束！", f"恭喜你完成了10轮挑战！\n\n你的最终总分是: {self.session_score}")
            self.start_button.setText("开始新一局游戏")
        else:
            # 继续下一回合
            self._load_next_round()