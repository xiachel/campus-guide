
# -*- coding: utf-8 -*-
"""校园导览系统（核心版）
功能：景点展示 / 最短路径问路 / 评分排序筛选 / 评分管理
数据：spots.json（景点表） + roads.json（路径表）
"""

import json
import heapq
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPOTS_FILE = os.path.join(BASE_DIR, "spots.json")
ROADS_FILE = os.path.join(BASE_DIR, "roads.json")


# ============ 一、数据加载与图建模 ============

def load_data():
    """读取两个 json 文件"""
    with open(SPOTS_FILE, "r", encoding="utf-8") as f:
        spots = json.load(f)
    with open(ROADS_FILE, "r", encoding="utf-8") as f:
        roads = json.load(f)
    return spots, roads


def build_graph(spots, roads):
    """
    邻接矩阵建模：
    matrix[i][j] = 景点 i 到 j 的距离，不相邻记为 None（相当于无穷大）
    index 负责 "景点名 <-> 下标" 的互相转换
    """
    n = len(spots)
    index = {spot["name"]: i for i, spot in enumerate(spots)}
    matrix = [[None] * n for _ in range(n)]
    for name_a, name_b, dist in roads:
        i, j = index[name_a], index[name_b]
        matrix[i][j] = dist       # 无向图，正反两个方向都存
        matrix[j][i] = dist
    return index, matrix


# ============ 二、最短路径：堆优化的 Dijkstra ============

def dijkstra(index, matrix, spots, start_name, end_name):
    """返回 (最短距离, 途经路径列表)；不可达返回 (None, [])"""
    if start_name not in index or end_name not in index:
        return None, []

    start, end = index[start_name], index[end_name]
    n = len(spots)
    dist = [float("inf")] * n     # 起点到各点的当前最短距离
    prev = [-1] * n               # 前驱节点，用于最后还原路径
    visited = [False] * n         # 已确定最短路的点

    dist[start] = 0
    heap = [(0, start)]           # 小顶堆，元素为 (距离, 节点下标)

    while heap:
        d, u = heapq.heappop(heap)
        if visited[u]:
            continue              # 跳过过期条目
        visited[u] = True
        if u == end:
            break                 # 终点出堆时，它的最短路已确定
        for v in range(n):
            w = matrix[u][v]
            if w is None or visited[v]:
                continue
            if d + w < dist[v]:   # "松弛"：经过 u 到 v 比已知的更近
                dist[v] = d + w
                prev[v] = u
                heapq.heappush(heap, (dist[v], v))

    if dist[end] == float("inf"):
        return None, []

    # 从终点沿 prev 一路回溯到起点，再反转
    path = []
    node = end
    while node != -1:
        path.append(spots[node]["name"])
        node = prev[node]
    path.reverse()
    return dist[end], path


# ============ 三、堆排序（手写实现） ============

def heapsort(items):
    """堆排序，升序输出，时间复杂度 O(n log n)"""
    arr = list(items)
    n = len(arr)

    def sift_down(root, end):
        """下沉操作：让 arr[root..end] 满足最大堆"""
        while True:
            child = root * 2 + 1            # 左孩子
            if child > end:
                return
            if child + 1 <= end and arr[child + 1] > arr[child]:
                child += 1                  # 右孩子更大就选右孩子
            if arr[child] > arr[root]:      # 孩子比父节点大：交换并继续下沉
                arr[root], arr[child] = arr[child], arr[root]
                root = child
            else:
                return

    for i in range(n // 2 - 1, -1, -1):     # 第一步：建最大堆
        sift_down(i, n - 1)
    for end in range(n - 1, 0, -1):         # 第二步：堆顶换到末尾，堆缩小一位
        arr[0], arr[end] = arr[end], arr[0]
        sift_down(0, end - 1)
    return arr


# ============ 四、折半查找 + 评分筛选 ============

def binary_search_first_ge(keys, target):
    """折半查找：在升序列表 keys 中返回第一个 >= target 的下标，找不到返回 -1"""
    lo, hi = 0, len(keys) - 1
    ans = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if keys[mid] >= target:
            ans = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return ans


def filter_by_rating(spots, min_rating):
    """筛选评分 >= min_rating 的景点，按评分从高到低返回"""
    sorted_pairs = heapsort([(s["rating"], s["name"]) for s in spots])
    keys = [rating for rating, _ in sorted_pairs]
    pos = binary_search_first_ge(keys, min_rating)
    if pos == -1:
        return []
    found = sorted_pairs[pos:]
    found.reverse()                         # 降序展示：评分高的在前
    return found


def top_k_spots(spots, k):
    """评分最高的 k 个景点；k 不合法时返回空列表"""
    if k <= 0:
        return []                           # 修复：防住 0 和负数（负数切片bug）
    pairs = heapsort([(s["rating"], s["name"]) for s in spots])
    pairs.reverse()
    return pairs[:k]


# ============ 五、输入解析与评分管理 ============

def parse_score(text):
    """把输入文本解析成 0~5 的评分，非法输入返回 None"""
    try:
        value = float(text)
    except ValueError:
        return None
    return value if 0 <= value <= 5 else None


def rate_spot(spots, index, name, score):
    """给景点打分，并写回 spots.json"""
    if name not in index:
        print("没有这个景点")
        return
    if not 0 <= score <= 5:
        print("评分范围是 0~5")
        return
    spots[index[name]]["rating"] = score
    with open(SPOTS_FILE, "w", encoding="utf-8") as f:
        json.dump(spots, f, ensure_ascii=False, indent=2)
    print(f"已保存：{name} 评分更新为 {score}")


# ============ 六、命令行菜单 ============

def show_all(spots):
    print(f"\n共 {len(spots)} 个景点：")
    for s in spots:
        print(f"  {s['name']:<8}评分 {s['rating']}")


def main():
    spots, roads = load_data()
    index, matrix = build_graph(spots, roads)
    print(f"校园导览系统已启动（{len(spots)} 个景点，{len(roads)} 条路径）")

    while True:
        print("""
========== 校园导览系统 ==========
 1. 显示所有景点及评分
 2. 问路（任意两景点最短路径）
 3. 按最低评分筛选景点
 4. 评分 Top-K 推荐
 5. 给景点评分（保存到文件）
 0. 退出""")
        choice = input("请输入功能编号：").strip()

        if choice == "1":
            show_all(spots)

        elif choice == "2":
            start = input("起点：").strip()
            end = input("终点：").strip()
            if start == end:
                print("起点和终点相同，无需导航")
                continue
            dist, path = dijkstra(index, matrix, spots, start, end)
            if dist is None:
                print("无法到达（请检查景点名是否输入正确）")
            else:
                print(f"最短距离约 {dist} 米")
                print("路线：" + " → ".join(path))

        elif choice == "3":
            r = parse_score(input("最低评分（0~5）：").strip())
            if r is None:
                print("评分必须是 0~5 之间的数字")
            else:
                result = filter_by_rating(spots, r)
                if not result:
                    print("没有符合条件的景点")
                for rating, name in result:
                    print(f"  {name}  评分 {rating}")

        elif choice == "4":
            text = input("推荐几个？").strip()
            if not text.isdigit():
                print("请输入正整数")
                continue
            result = top_k_spots(spots, int(text))
            if not result:
                print(f"请输入 1~{len(spots)} 之间的数字")
            for rating, name in result:
                print(f"  {name}  评分 {rating}")

        elif choice == "5":
            name = input("景点名：").strip()
            score = parse_score(input("新评分（0~5）：").strip())
            if score is None:
                print("评分必须是 0~5 之间的数字")
            else:
                rate_spot(spots, index, name, score)

        elif choice == "0":
            print("再见！")
            break

        else:
            print("无效输入，请重新输入")


if __name__ == "__main__":
    main()
