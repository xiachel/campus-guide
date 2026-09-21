
from campus_guide import (
    build_graph, dijkstra, heapsort,
    binary_search_first_ge, top_k_spots, parse_score,
)

# 固定测试数据：不依赖 json 文件，只测纯逻辑
SPOTS = [
    {"name": "A", "rating": 4.8},
    {"name": "B", "rating": 3.5},
    {"name": "C", "rating": 4.1},
    {"name": "D", "rating": 2.9},
]
ROADS = [
    ["A", "B", 100],
    ["B", "C", 200],
    ["A", "C", 500],   # 故意设计：A→C 直达500米，绕行B只有300米
    ["C", "D", 50],
]


# ---------- Dijkstra ----------
def test_path_prefers_shorter_detour():
    """直达500米 vs 绕行300米：必须选绕行"""
    index, matrix = build_graph(SPOTS, ROADS)
    dist, path = dijkstra(index, matrix, SPOTS, "A", "C")
    assert dist == 300
    assert path == ["A", "B", "C"]

def test_start_equals_end():
    index, matrix = build_graph(SPOTS, ROADS)
    dist, path = dijkstra(index, matrix, SPOTS, "A", "A")
    assert dist == 0 and path == ["A"]

def test_unknown_name():
    index, matrix = build_graph(SPOTS, ROADS)
    dist, path = dijkstra(index, matrix, SPOTS, "北门", "A")
    assert dist is None and path == []

def test_unreachable():
    spots = SPOTS + [{"name": "孤岛", "rating": 4.0}]
    index, matrix = build_graph(spots, ROADS)
    dist, path = dijkstra(index, matrix, spots, "A", "孤岛")
    assert dist is None and path == []


# ---------- 堆排序 ----------
def test_heapsort_normal():
    assert heapsort([5, 1, 4, 2, 8]) == [1, 2, 4, 5, 8]

def test_heapsort_duplicates():
    assert heapsort([3, 1, 3, 1]) == [1, 1, 3, 3]

def test_heapsort_empty_and_single():
    assert heapsort([]) == []
    assert heapsort([42]) == [42]


# ---------- 折半查找 ----------
def test_search_found():
    assert binary_search_first_ge([1, 3, 5, 7], 5) == 2

def test_search_edges():
    assert binary_search_first_ge([1, 3, 5], 0) == 0    # 比所有元素都小
    assert binary_search_first_ge([1, 3, 5], 10) == -1  # 比所有元素都大


# ---------- Top-K（上次抓到 bug 的地方）----------
def test_top_k_normal():
    assert top_k_spots(SPOTS, 2) == [(4.8, "A"), (4.1, "C")]

def test_top_k_zero():
    assert top_k_spots(SPOTS, 0) == []

def test_top_k_negative():
    """修复前：top_k_spots(SPOTS, -1) 会因负数切片返回错误结果"""
    assert top_k_spots(SPOTS, -1) == []


# ---------- 评分解析（上次崩溃的地方）----------
def test_parse_score_valid():
    assert parse_score("4.5") == 4.5
    assert parse_score("0") == 0

def test_parse_score_invalid():
    assert parse_score("abc") is None
    assert parse_score("9") is None
    assert parse_score("-1") is None
