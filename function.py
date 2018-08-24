import re


def judge(table, n, BLACK, WHITE):
    """
    判断是否已分出胜负
    :param table: n*n列表，用于存储棋盘上各位置的信息，BLACK表示黑子，WHITE表示白子
    :return: 若未分出胜负，则返回none，否则返回五个连着的相同颜色棋子的首尾坐标
    """

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
