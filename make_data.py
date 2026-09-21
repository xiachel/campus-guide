
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

spots = [
    {"name": "东门", "rating": 4.2},
    {"name": "南门", "rating": 4.5},
    {"name": "图书馆", "rating": 4.8},
    {"name": "第一教学楼", "rating": 4.0},
    {"name": "第二教学楼", "rating": 3.9},
    {"name": "体育馆", "rating": 4.3},
    {"name": "田径场", "rating": 4.1},
    {"name": "第一食堂", "rating": 3.8},
    {"name": "第二食堂", "rating": 4.0},
    {"name": "樱花谷", "rating": 4.7},
    {"name": "宿舍区", "rating": 3.5},
    {"name": "校医院", "rating": 3.6},
]

roads = [
    ["东门", "图书馆", 300],
    ["东门", "第一教学楼", 500],
    ["南门", "樱花谷", 200],
    ["南门", "第二食堂", 400],
    ["图书馆", "第一教学楼", 250],
    ["图书馆", "樱花谷", 600],
    ["第一教学楼", "第二教学楼", 150],
    ["第二教学楼", "田径场", 350],
    ["体育馆", "田径场", 200],
    ["体育馆", "宿舍区", 300],
    ["第一食堂", "宿舍区", 250],
    ["第一食堂", "第二教学楼", 450],
    ["樱花谷", "第二食堂", 300],
    ["田径场", "校医院", 400],
    ["宿舍区", "校医院", 350],
]

with open(os.path.join(BASE_DIR, "spots.json"), "w", encoding="utf-8") as f:
    json.dump(spots, f, ensure_ascii=False, indent=2)

with open(os.path.join(BASE_DIR, "roads.json"), "w", encoding="utf-8") as f:
    json.dump(roads, f, ensure_ascii=False, indent=2)

print("数据文件已生成：spots.json / roads.json")
