import re
from math import inf
from config import VACANT, BLACK, WHITE


def search(table, sequence):
    n = len(table)
    if not sequence:
        return n // 2, n // 2
    left = min([j for i, j in sequence])
    right = max([j for i, j in sequence])
    up = min([i for i, j in sequence])
    down = max([i for i, j in sequence])
    left, right, up, down = max(0, left - 1), min(n - 1, right + 1), max(0, up - 1), min(n - 1, down + 1)
    sub_table = [_[left: right + 1] for _ in table[up: down + 1]]
    scores = {}
    for i in range(down - up + 1):
        for j in range(right - left + 1):
            if sub_table[i][j] == VACANT:
                sub_table[i][j] = WHITE
                scores[i, j] = min_search(sub_table, 0)
                sub_table[i][j] = VACANT
    max_ = -inf
    i_max, j_max = 0, 0
    for i, j in scores:
        if scores[i, j] > max_:
            max_ = scores[i, j]
            i_max, j_max = i, j
    return i_max + up, j_max + left


def max_search(table, depth):
    m, n = len(table), len(table[0])
    scores = {}
    for i in range(m):
        for j in range(n):
            if table[i][j] == VACANT:
                table[i][j] = WHITE
                if depth == 0:
                    scores[i, j] = evaluate(table)
                else:
                    scores[i, j] = min_search(table, depth - 1)
                table[i][j] = VACANT
    max_ = -inf
    for i, j in scores:
        if scores[i, j] > max_:
            max_ = scores[i, j]
    return max_


def min_search(table, depth):
    m, n = len(table), len(table[0])
    scores = {}
    for i in range(m):
        for j in range(n):
            if table[i][j] == VACANT:
                table[i][j] = BLACK
                if depth == 0:
                    scores[i, j] = evaluate(table)
                else:
                    scores[i, j] = max_search(table, depth - 1)
                table[i][j] = VACANT
    min_ = inf
    for i, j in scores:
        if scores[i, j] < min_:
            min_ = scores[i, j]
    return min_


patterns = {}
for color in [BLACK, WHITE]:
    for num in range(1, 6):
        patterns[str(color) + '{' + str(num) + '}'] = num ** 2
        patterns[str(VACANT) + str(color) + '{' + str(num) + '}'] = num ** 2
        patterns[str(color) + '{' + str(num) + '}' + str(VACANT)] = num ** 2
        if color == BLACK:
            patterns[str(color) + '{' + str(num) + '}'] *= -1


def evaluate(table):
    m, n = len(table), len(table[0])
    score = 0
    strings = []
    for i in range(m):
        strings.append(''.join([str(_) for _ in table[i]]))
    for j in range(n):
        strings.append(''.join([str(table[i][j]) for i in range(m)]))
    for k in range(m + n - 1):
        if k < m:
            strings.append(''.join([str(table[k - i][i]) for i in range(min(k + 1, n))]))
        else:
            strings.append(''.join([str(table[m - 1 - i][k - m + 1 + i]) for i in range(m + n - max(k + 1, n))]))
    for k in range(m + n - 1):
        if k < m:
            strings.append(''.join([str(table[m - 1 - k + i][i]) for i in range(min(k + 1, n))]))
        else:
            strings.append(''.join([str(table[i][k - m + 1 + i]) for i in range(m + n - max(k + 1, n))]))
    for string in strings:
        for pattern in patterns:
            if re.search(pattern, string):
                score += patterns[pattern]
    return score


def judge(table):
    """
    判断是否已分出胜负
    :param table: n*n列表，用于存储棋盘上各位置的信息，BLACK表示黑子，WHITE表示白子
    :return: 若未分出胜负，则返回none，否则返回五个连着的相同颜色棋子的首尾坐标
    """
    n = len(table)

    pattern1 = str(BLACK) + '{5}'
    pattern2 = str(WHITE) + '{5}'

    # 检查所有横行
    for i in range(n):
        to_string = ''.join([str(_) for _ in table[i]])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return i, search1.start(), i, search1.end() - 1, BLACK
        if search2:
            return i, search2.start(), i, search2.end() - 1, WHITE

    # 检查所有竖列
    for j in range(n):
        to_string = ''.join([str(table[i][j]) for i in range(n)])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return search1.start(), j, search1.end() - 1, j, BLACK
        if search2:
            return search2.start(), j, search2.end() - 1, j, WHITE

    # 检查右上三角
    for k in range(n - 4):
        to_string = ''.join([str(table[h][k + h]) for h in range(n - k)])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return search1.start(), k + search1.start(), search1.end() - 1, k + search1.end() - 1, BLACK
        if search2:
            return search2.start(), k + search2.start(), search2.end() - 1, k + search2.end() - 1, WHITE

    # 检查左下三角
    for k in range(1, n - 4):
        to_string = ''.join([str(table[k + h][h]) for h in range(n - k)])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return k + search1.start(), search1.start(), k + search1.end() - 1, search1.end() - 1, BLACK
        if search2:
            return k + search2.start(), search2.start(), k + search2.end() - 1, search2.end() - 1, WHITE

    # 检查左上三角
    for k in range(n - 4):
        to_string = ''.join([str(table[n - 1 - k - h][h]) for h in range(n - k)])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return n - 1 - k - search1.start(), search1.start(), n - k - search1.end(), search1.end() - 1, BLACK
        if search2:
            return n - 1 - k - search2.start(), search2.start(), n - k - search2.end(), search2.end() - 1, WHITE

    # 检查右下三角
    for k in range(1, n - 4):
        to_string = ''.join([str(table[n - 1 - h][k + h]) for h in range(n - k)])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return n - 1 - search1.start(), k + search1.start(), n - search1.end(), k + search1.end() - 1, BLACK
        if search2:
            return n - 1 - search2.start(), k + search2.start(), n - search2.end(), k + search2.end() - 1, WHITE

    return None
