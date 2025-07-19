# logic/data_manager.py

import json
import os
import sys

def get_base_path():
    """获取项目根目录的路径"""
    if getattr(sys, 'frozen', False):
        # 如果程序被打包了
        return os.path.dirname(sys.executable)
    else:
        # 如果是正常运行的脚本，向上回退一级
        # 因为这个文件在 logic/ 目录里
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROBLEMS_FILE = os.path.join(get_base_path(), 'quant_problems.json')

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