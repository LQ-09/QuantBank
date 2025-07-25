# logic/data_manager.py

import json
import os
import sys

def get_base_path():
    """获取项目根目录的路径"""
    if hasattr(sys, '_MEIPASS'):
        # 如果程序被打包了，基础路径是_MEIPASS
        return sys._MEIPASS
    else:
        # 如果是正常运行的脚本，向上回退一级到项目根目录
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 在这里定义所有的全局文件名常量 ---
PROBLEMS_FILE = os.path.join(get_base_path(), 'quant_problems.json')
GAME_STATS_FILE = os.path.join(get_base_path(), 'game_stats.json')

# --- 题库相关函数 ---
def load_problems():
    """从JSON文件加载所有题目"""
    if not os.path.exists(PROBLEMS_FILE):
        with open(PROBLEMS_FILE, 'w') as f:
            json.dump([], f)
        return []
    with open(PROBLEMS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_problems(problems):
    """将所有题目保存到JSON文件"""
    with open(PROBLEMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(problems, f, ensure_ascii=False, indent=4)

def update_problem_stats(problem_id, was_correct):
    """更新一道题的尝试次数和正确次数"""
    problems = load_problems()
    problem_found = False
    for p in problems:
        if p.get('id') == problem_id:
            p['attempts'] = p.get('attempts', 0) + 1
            if was_correct:
                p['correct'] = p.get('correct', 0) + 1
            problem_found = True
            break
    if problem_found:
        save_problems(problems)
    return problem_found

def toggle_problem_saved_status(problem_id):
    """切换一道题的is_saved布尔值"""
    problems = load_problems()
    problem_found = False
    new_status = False
    for p in problems:
        if p.get('id') == problem_id:
            current_status = p.get('is_saved', False)
            p['is_saved'] = not current_status
            new_status = p['is_saved']
            problem_found = True
            break
    if problem_found:
        save_problems(problems)
    return new_status

# --- 游戏统计相关函数 ---
def load_game_stats():
    """从JSON文件加载所有游戏记录"""
    if not os.path.exists(GAME_STATS_FILE):
        return []
    with open(GAME_STATS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_game_stats(stats):
    """将所有游戏记录保存到JSON文件"""
    with open(GAME_STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

def add_game_record(record):
    """添加一条新的游戏记录"""
    stats = load_game_stats()
    stats.append(record)
    save_game_stats(stats)

def clear_game_stats():
    """清空所有的游戏得分/历史记录"""
    save_game_stats([]) # 直接保存一个空列表

def reset_problem_practice_stats():
    """重置所有题目的练习统计（尝试次数和正确次数），但不改变收藏状态"""
    problems = load_problems()
    for p in problems:
        p['attempts'] = 0
        p['correct'] = 0
    save_problems(problems)


def get_game_sessions():
    """
    加载所有游戏回合记录，并将它们按10个一组进行聚合。
    返回一个包含每局游戏信息的列表。
    """
    stats = load_game_stats()
    sessions = []
    
    # 每10个记录为一局
    session_length = 10
    for i in range(0, len(stats), session_length):
        session_records = stats[i:i+session_length]
        
        # 确保这是一组完整的10局（或最后一组不完整的）
        if not session_records:
            continue
            
        total_score = sum(r.get("score", 0) for r in session_records)
        # 使用这一局第一条记录的时间戳
        timestamp = session_records[0].get("timestamp")
        
        sessions.append({
            "timestamp": timestamp,
            "total_score": total_score,
            "num_rounds": len(session_records)
        })
        
    return sessions