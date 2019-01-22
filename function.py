# -*- coding: utf-8 -*-

import re
from math import inf
from copy import deepcopy
from config import VACANT, BLACK, WHITE


def search_space(table, sequence):
    """
    根据当前棋盘上棋子的落子顺序序列来计算下一步的搜索空间
    若将所有空点作为搜索空间则必然是完备的，但是搜索空间太大会导致计算效率非常低
    因此只有当某个空点在以其为中心的5*5的方格范围内有子的情况下，才将其加入搜索空间
    因此只要对当前落子序列中的每个点，将以其为中心的5*5的方格范围内的空点加入到搜索空间中即可
    但是加入的顺序也会有影响，因为此程序使用了alpha-beta剪枝，要想最大化剪枝的作用，应使先加入更可能是最优解的点
    可以简单地认为，越靠近最近几步的落子点的空点，越有可能是最优解
    因此在扩展搜索空间时，按sequence中顺序的相反顺序搜索
    :param table: 当前棋盘
    :param sequence: 当前棋盘上棋子的落子顺序序列
    :return: 计算出的下一步的搜索空间
    """
    n = len(table)
    space = []
    for i0, j0 in sequence[-1::-1]:
        for delta_i in [0, -1, 1, -2, 2]:
            for delta_j in [0, -1, 1, -2, 2]:
                i1, j1 = i0 + delta_i, j0 + delta_j
                if table[i1][j1] == VACANT and (i1, j1) not in space and 0 <= i1 < n and 0 <= j1 < n:
                    space.append((i1, j1))
    return space


def search(table, sequence):
    n = len(table)
    if not sequence:
        return n // 2, n // 2
    alpha, beta = -inf, inf
    max_ = -inf
    max_i, max_j = 0, 0
    space = search_space(table, sequence)
    for (i, j) in space:
        if table[i][j] == VACANT:
            table[i][j] = WHITE
            new_space = deepcopy(space)
            new_space.remove((i, j))
            for delta_i in [0, -1, 1, -2, 2]:
                for delta_j in [0, -1, 1, -2, 2]:
                    i1, j1 = i + delta_i, j + delta_j
                    if table[i1][j1] == VACANT and (i1, j1) not in space and 0 <= i1 < n and 0 <= j1 < n:
                        new_space = [(i1, j1)] + new_space
            score = min_search(table, alpha, beta, depth=1, space=new_space)
            table[i][j] = VACANT
            if score > max_:
                max_ = score
                max_i, max_j = i, j
            if max_ >= beta:
                return max_i, max_j
            if max_ > alpha:
                alpha = max_
    return max_i, max_j


def max_search(table, alpha, beta, depth, space):
    if depth == 0:
        return evaluate(table)
    n = len(table)
    max_ = -inf
    for (i, j) in space:
        if table[i][j] == VACANT:
            table[i][j] = WHITE
            new_space = deepcopy(space)
            new_space.remove((i, j))
            for delta_i in [0, -1, 1, -2, 2]:
                for delta_j in [0, -1, 1, -2, 2]:
                    i1, j1 = i + delta_i, j + delta_j
                    if table[i1][j1] == VACANT and (i1, j1) not in space and 0 <= i1 < n and 0 <= j1 < n:
                        new_space.append((i1, j1))
            score = min_search(table, alpha, beta, depth=depth - 1, space=new_space)
            table[i][j] = VACANT
            if score > max_:
                max_ = score
            if max_ >= beta:
                return max_
            if max_ > alpha:
                alpha = max_
    return max_


def min_search(table, alpha, beta, depth, space):
    if depth == 0:
        return evaluate(table)
    n = len(table)
    min_ = inf
    for (i, j) in space:
        if table[i][j] == VACANT:
            table[i][j] = BLACK
            new_space = deepcopy(space)
            new_space.remove((i, j))
            for delta_i in [0, -1, 1, -2, 2]:
                for delta_j in [0, -1, 1, -2, 2]:
                    i1, j1 = i + delta_i, j + delta_j
                    if table[i1][j1] == VACANT and (i1, j1) not in space and 0 <= i1 < n and 0 <= j1 < n:
                        new_space.append((i1, j1))
            score = max_search(table, alpha, beta, depth=depth - 1, space=new_space)
            if score < min_:
                min_ = score
            table[i][j] = VACANT
            if min_ <= alpha:
                return min_
            if min_ < beta:
                beta = min_
    return min_


patterns = {}
for color in [BLACK, WHITE]:
    opponent_color = BLACK if color == WHITE else WHITE
    factor = 1 if color == WHITE else -1
    for num in range(1, 5):
        patterns[str(VACANT) + str(color) + '{' + str(num) + '}' + str(opponent_color)] = factor * num ** 2
        patterns[str(opponent_color) + str(color) + '{' + str(num) + '}' + str(VACANT)] = factor * num ** 2
        patterns[str(VACANT) + str(color) + '{' + str(num) + '}' + str(VACANT)] = factor * num ** 2
    # patterns[str(VACANT) + str(color) + '{' + str(4) + '}' + str(opponent_color)] = factor * 16
    # patterns[str(opponent_color) + '{' + str(4) + '}' + str(VACANT)] = factor * 16
    patterns[str(VACANT) + str(color) + '{' + str(4) + '}' + str(VACANT)] = factor * 10000
    patterns[str(color) + '{' + str(5) + '}'] = factor * 10000


def evaluate(table):
    n = len(table)
    score = 0
    strings = []
    for i in range(n):
        strings.append(''.join([str(_) for _ in table[i]]))
    for j in range(n):
        strings.append(''.join([str(table[i][j]) for i in range(n)]))
    for k in range(2 * n - 1):
        if k < n:
            strings.append(''.join([str(table[k - i][i]) for i in range(k + 1)]))
        else:
            strings.append(''.join([str(table[n - 1 - i][k - n + 1 + i]) for i in range(2 * n - k - 1)]))
    for k in range(2 * n - 1):
        if k < n:
            strings.append(''.join([str(table[n - 1 - k + i][i]) for i in range(k + 1)]))
        else:
            strings.append(''.join([str(table[i][k - n + 1 + i]) for i in range(2 * n - k - 1)]))
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
