# logic/data_manager.py

import json
import os
import sys

def get_base_path():
    """
    获取资源文件的基础路径。
    如果是打包后的.exe文件，则返回PyInstaller创建的临时文件夹路径。
    否则，返回项目的根目录。
    """
    if hasattr(sys, '_MEIPASS'):
        # 如果程序被打包了，基础路径是_MEIPASS
        return sys._MEIPASS
    else:
        # 如果是正常运行的脚本，向上回退一级到项目根目录
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# PROBLEMS_FILE现在会根据运行模式指向正确的位置
PROBLEMS_FILE = os.path.join(get_base_path(), 'quant_problems.json')

def load_problems():
    """从JSON文件加载所有题目"""
    # 第一次运行时，json文件可能不在，需要从exe的临时目录复制出来
    # 但我们的逻辑是直接在那个目录读写，更简单
    if not os.path.exists(PROBLEMS_FILE):
        # 在打包后的环境中，文件应该存在。如果不存在，则创建一个空的。
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

# (之前新增的 update_problem_stats 和 toggle_problem_saved_status 函数保持不变)
def update_problem_stats(problem_id, was_correct):
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