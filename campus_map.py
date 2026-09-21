# -*- coding: utf-8 -*-
"""校园地图可视化
功能：绘制校园地图；查询最短路径并高亮显示
依赖：pip install networkx matplotlib
"""

import json
import os

import matplotlib
import matplotlib.pyplot as plt
import networkx as nx

# 复用主程序里写好的算法 —— 这就是模块化设计，面试可以讲
from campus_guide import build_graph, dijkstra

# ---------- 中文显示设置（Windows 自带微软雅黑） ----------
matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
matplotlib.rcParams["axes.unicode_minus"] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 手工设定的示意坐标（为了让布局好看，不是严格比例，可随意调整）
POSITIONS = {
    "东门": (0, 6),
    "图书馆": (3, 6),
    "第一教学楼": (4.5, 4),
    "第二教学楼": (5.5, 3),
    "田径场": (7.5, 4),
    "体育馆": (9, 2.5),
    "校医院": (9, 5.5),
    "宿舍区": (6.5, 1),
    "第一食堂": (3.5, 1),
    "第二食堂": (2.5, 3),
    "樱花谷": (1.2, 1.8),
    "南门": (0.5, -0.5),
}


def load_data():
    with open(os.path.join(BASE_DIR, "spots.json"), "r", encoding="utf-8") as f:
        spots = json.load(f)
    with open(os.path.join(BASE_DIR, "roads.json"), "r", encoding="utf-8") as f:
        roads = json.load(f)
    return spots, roads


def build_nx_graph(spots, roads):
    """用 networkx 建图：节点=景点，边=道路，权重=距离"""
    G = nx.Graph()
    for s in spots:
        G.add_node(s["name"])
    for a, b, w in roads:
        G.add_edge(a, b, weight=w)
    return G


def draw_map(G, path=None, title="校园导览地图"):
    """画地图；如果传入了 path（景点名列表），高亮显示这条路线"""
    node_colors = ["#a8dadc" for _ in G.nodes]      # 常规节点：浅蓝
    edge_colors = ["#cfcfcf" for _ in G.edges]      # 常规道路：浅灰
    edge_widths = [1.2 for _ in G.edges]

    if path and len(path) > 1:
        path_edges = list(zip(path, path[1:]))
        node_colors = ["#ffd166" if n in path else "#a8dadc" for n in G.nodes]
        edge_colors = [
            "#ef476f" if (u, v) in path_edges or (v, u) in path_edges else "#cfcfcf"
            for u, v in G.edges
        ]
        edge_widths = [
            3.5 if (u, v) in path_edges or (v, u) in path_edges else 1.2
            for u, v in G.edges
        ]

    plt.figure(figsize=(11, 7))
    nx.draw_networkx_nodes(G, POSITIONS, node_color=node_colors,
                           node_size=2000, edgecolors="#404040", linewidths=1.2)
    nx.draw_networkx_edges(G, POSITIONS, edge_color=edge_colors, width=edge_widths)
    nx.draw_networkx_labels(G, POSITIONS, font_size=10)

    # 每条路旁边标注距离
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, POSITIONS, edge_labels=edge_labels, font_size=8)

    plt.title(title, fontsize=14)
    plt.axis("off")
    plt.tight_layout()
    # 顺手存一张图，这就是以后 GitHub 仓库和简历用的截图
    plt.savefig(os.path.join(BASE_DIR, "campus_map.png"), dpi=200, bbox_inches="tight")
    plt.show()


def main():
    spots, roads = load_data()
    G = build_nx_graph(spots, roads)
    print(f"地图已加载：{G.number_of_nodes()} 个景点，{G.number_of_edges()} 条道路")

    while True:
        print("""
========== 校园地图可视化 ==========
 1. 查看整张校园地图
 2. 查询最短路径并高亮显示
 0. 退出""")
        choice = input("请输入功能编号：").strip()

        if choice == "1":
            draw_map(G)
        elif choice == "2":
            start = input("起点：").strip()
            end = input("终点：").strip()
            index, matrix = build_graph(spots, roads)   # 直接复用主程序的函数
            dist, path = dijkstra(index, matrix, spots, start, end)
            if dist is None:
                print("无法到达（请检查景点名是否输入正确）")
            else:
                print(f"最短距离约 {dist} 米，路线：{' → '.join(path)}")
                draw_map(G, path=path, title=f"{start} → {end} 最短路径（约{dist}米）")
        elif choice == "0":
            print("再见！")
            break
        else:
            print("无效输入")


if __name__ == "__main__":
    main()
