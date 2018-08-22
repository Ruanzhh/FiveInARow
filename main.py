import sys
import re
from PyQt5.QtWidgets import *  # QApplication, QWidget, QPushButton
from PyQt5.QtGui import *  # QPainter, QPixmap, QBrush
from PyQt5.QtCore import *  # Qt, QPoint, QRect

N = 19  # 棋盘的行/列数
SIZE = 40  # 棋盘上相邻两条线之间的距离
MARGIN = 80  # 棋盘下边距
DIA = SIZE * 9 // 10  # 棋子的直径
BOARD_COLOR = QColor(249, 214, 91)  # 棋盘颜色
VACANT = 0
BLACK = 1
WHITE = 2


def judge(table):
    """
    判断是否已分出胜负
    :param table: N*N列表，用于存储棋盘上各位置的信息，VACANT表示无棋子，BLACK表示黑子，WHITE表示白子
    :return: 若未分出胜负，则返回None，否则返回五个连着的相同颜色棋子的首尾坐标
    """

    pattern1 = str(BLACK) + '{5}'
    pattern2 = str(WHITE) + '{5}'

    # 检查所有横行
    for i in range(N):
        to_string = ''.join([str(_) for _ in table[i]])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return i, search1.start(), i, search1.end() - 1, BLACK
        if search2:
            return i, search2.start(), i, search2.end() - 1, WHITE

    # 检查所有竖列
    for j in range(N):
        to_string = ''.join([str(table[i][j]) for i in range(N)])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return search1.start(), j, search1.end() - 1, j, BLACK
        if search2:
            return search2.start(), j, search2.end() - 1, j, WHITE

    # 检查右上三角
    for k in range(N - 4):
        to_string = ''.join([str(table[h][k + h]) for h in range(N - k)])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return search1.start(), k + search1.start(), search1.end() - 1, k + search1.end() - 1, BLACK
        if search2:
            return search2.start(), k + search2.start(), search2.end() - 1, k + search2.end() - 1, WHITE

    # 检查左下三角
    for k in range(1, N - 4):
        to_string = ''.join([str(table[k + h][h]) for h in range(N - k)])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return k + search1.start(), search1.start(), k + search1.end() - 1, search1.end() - 1, BLACK
        if search2:
            return k + search2.start(), search2.start(), k + search2.end() - 1, search2.end() - 1, WHITE

    # 检查左上三角
    for k in range(N - 4):
        to_string = ''.join([str(table[N - 1 - k - h][h]) for h in range(N - k)])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return N - 1 - k - search1.start(), search1.start(), N - k - search1.end(), search1.end() - 1, BLACK
        if search2:
            return N - 1 - k - search2.start(), search2.start(), N - k - search2.end(), search2.end() - 1, WHITE

    # 检查右下三角
    for k in range(1, N - 4):
        to_string = ''.join([str(table[N - 1 - h][k + h]) for h in range(N - k)])
        search1 = re.search(pattern1, to_string)
        search2 = re.search(pattern2, to_string)
        if search1:
            return N - 1 - search1.start(), k + search1.start(), N - search1.end(), k + search1.end() - 1, BLACK
        if search2:
            return N - 1 - search2.start(), k + search2.start(), N - search2.end(), k + search2.end() - 1, WHITE
    return None


class Button(QToolButton):
    def __init__(self, parent=None):
        super(Button, self).__init__(parent)
        self.setFont(QFont("Bold", 20))
        self.setFixedSize(QSize(100, 60))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(True)
            self.parent().mousePressEvent(event)


class Board(QWidget):
    def __init__(self, parent=None):
        super(Board, self).__init__(parent)
        self.start = False
        self.count = 0
        self.black = True
        self.finish = False
        self.sequence = []
        self.table = [[VACANT for j in range(N)] for i in range(N)]
        self.withdraw_point = None
        self.winner = VACANT

        self.setWindowTitle("五子棋")
        self.setFixedSize(SIZE * N, SIZE * N + MARGIN)
        self.pix = QPixmap(SIZE * N, SIZE * N + MARGIN)
        self.pix.fill(BOARD_COLOR)
        self.point = None

        self.newgame_button = Button(self)
        self.newgame_button.setText("新局")
        self.newgame_button.setStyleSheet("color:white; background-color:blue")
        self.newgame_button.move(SIZE * N // 5, SIZE * N)
        self.newgame_button.clicked.connect(self.newgame)

        self.setting_button = Button(self)
        self.setting_button.setText("设置")
        self.setting_button.setStyleSheet("color:white; background-color:blue")
        self.setting_button.move(SIZE * N * 2 // 5, SIZE * N)
        #self.newgame_button.clicked.connect(self.newgame)

        self.withdraw_button = Button(self)
        self.withdraw_button.setText("悔棋")
        self.withdraw_button.setStyleSheet("color:white; background-color:gray")
        self.withdraw_button.move(SIZE * N * 3 // 5, SIZE * N)
        self.withdraw_button.clicked.connect(self.withdraw)

        self.suggest_button = Button(self)
        self.suggest_button.setText("提示")
        self.suggest_button.setStyleSheet("color:white; background-color:blue")
        self.suggest_button.move(SIZE * N * 4 // 5, SIZE * N)
        #self.newgame_button.clicked.connect(self.newgame)

    def paintEvent(self, event):
        painter = QPainter(self)
        pp = QPainter(self.pix)

        if not self.start:
            pp.setPen(BOARD_COLOR)
            pp.setBrush(QBrush(BOARD_COLOR))
            pp.drawRect(0, 0, SIZE * N, SIZE * N + MARGIN)
            pp.setPen(Qt.black)
            for i in range(N):
                pp.drawLine(SIZE * i + SIZE // 2, SIZE // 2, SIZE * i + SIZE // 2, SIZE * N - SIZE // 2)
                pp.drawLine(SIZE // 2, SIZE * i + SIZE // 2, SIZE * N - SIZE // 2, SIZE * i + SIZE // 2)

        if self.point:
            color = Qt.black if self.black else Qt.white
            pp.setPen(color)
            pp.setBrush(QBrush(color))
            x, y = self.point.x(), self.point.y()
            j, i = x // SIZE, y // SIZE
            if (i, j) not in self.sequence and 0 <= i < N and 0 <= j < N:
                self.count += 1
                if not self.start:
                    self.start = True
                    self.withdraw_button.setStyleSheet("color:white; background-color:blue")
                self.sequence.append((i, j))
                self.table[i][j] = BLACK if self.black else WHITE
                pp.drawEllipse(j * SIZE + (SIZE - DIA) // 2, i * SIZE + (SIZE - DIA) // 2, DIA, DIA)
                self.black = not self.black

            result = judge(self.table)
            if result:
                pp.setPen(Qt.red)
                i1, j1, i2, j2, self.winner = result
                x1 = j1 * SIZE + SIZE // 2
                y1 = i1 * SIZE + SIZE // 2
                x2 = j2 * SIZE + SIZE // 2
                y2 = i2 * SIZE + SIZE // 2
                pp.drawLine(x1, y1, x2, y2)
                self.finish = True
            self.point = None

        if self.withdraw_point:
            i, j = self.withdraw_point
            pp.setPen(BOARD_COLOR)
            pp.setBrush(QBrush(BOARD_COLOR))
            pp.drawEllipse(j * SIZE + (SIZE - DIA) // 2, i * SIZE + (SIZE - DIA) // 2, DIA, DIA)
            pp.setPen(Qt.black)
            pp.drawLine(j * SIZE + (SIZE - DIA) // 2, i * SIZE + SIZE // 2,
                        j * SIZE + (SIZE + DIA) // 2, i * SIZE + SIZE // 2)
            pp.drawLine(j * SIZE + SIZE // 2, i * SIZE + (SIZE - DIA) // 2,
                        j * SIZE + SIZE // 2, i * SIZE + (SIZE + DIA) // 2)
            self.withdraw_point = None

        if not self.finish:
            color = Qt.black if self.count % 2 == 0 else Qt.white
            pp.setPen(color)
            pp.setBrush(QBrush(color))
            pp.drawEllipse(SIZE * N // 10 - DIA * 3 // 4, SIZE * N, DIA * 3 // 2, DIA * 3 // 2)
            pp.setPen(Qt.black if self.count % 2 == 1 else Qt.white)
            pp.setFont(QFont("Bold", 20))
            pp.drawText(QRectF(SIZE * N // 10 - DIA * 3 // 4, SIZE * N, DIA * 3 // 2, DIA * 3 // 2),
                        Qt.AlignCenter, str(self.count + 1))
        else:
            color = Qt.black if self.winner == BLACK else Qt.white
            pp.setPen(color)
            pp.setBrush(QBrush(color))
            pp.drawEllipse(SIZE * N // 10 - DIA * 3 // 4, SIZE * N, DIA * 3 // 2, DIA * 3 // 2)
            pp.setPen(Qt.red)
            pp.setFont(QFont("Bold", 20))
            pp.drawText(QRectF(SIZE * N // 10 - DIA * 3 // 4, SIZE * N, DIA * 3 // 2, DIA * 3 // 2),
                        Qt.AlignCenter, "胜")

        painter.drawPixmap(0, 0, self.pix)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.finish:
                self.point = event.pos()
            self.update()

    def newgame(self):
        self.start = False
        self.count = 0
        self.black = True
        self.finish = False
        self.sequence = []
        self.table = [[VACANT for j in range(N)] for i in range(N)]
        self.withdraw_point = None
        self.withdraw_button.setStyleSheet("color:white; background-color:gray")

    def withdraw(self):
        if self.start and not self.finish:
            i, j = self.sequence.pop()
            self.withdraw_point = (i, j)
            self.table[i][j] = VACANT
            self.count -= 2
            self.black = not self.black
            if not self.sequence:
                self.start = False
                self.withdraw_button.setStyleSheet("color:white; background-color:gray")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    board = Board()
    board.show()
    sys.exit(app.exec_())
