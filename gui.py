# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *  # QApplication, QWidget, QPushButton
from PyQt5.QtGui import *  # QPainter, QPixmap, QBrush
from PyQt5.QtCore import *  # Qt, QPoint, QRect
from function import judge, search
from config import VACANT, BLACK, WHITE

BOARD_COLOR = QColor(249, 214, 91)  # 棋盘颜色


class Button(QToolButton):
    def __init__(self, parent=None):
        super(Button, self).__init__(parent)
        self.setFont(QFont("Microsoft YaHei", 18))
        self.setFixedSize(QSize(100, 60))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(True)
            self.parent().mousePressEvent(event)


class Setting(QWidget):
    def __init__(self, parent=None):
        super(Setting, self).__init__(parent)
        self.setWindowTitle("设置")
        self.setWindowModality(Qt.ApplicationModal)


class Board(QWidget):
    def __init__(self, n, width, margin, parent=None):
        super(Board, self).__init__(parent)
        self.n = n
        self.size = width // self.n
        self.dia = self.size * 9 // 10
        self.margin = margin

        self.start = False
        self.count = 0
        self.black = True
        self.finish = False
        self.sequence = []
        self.table = [[VACANT for j in range(self.n)] for i in range(self.n)]
        for i, j in self.sequence:
            self.table[i][j] = BLACK if self.black else WHITE
            self.black = not self.black
        self.withdraw_point = None
        self.winner = VACANT

        self.show_step = True

        self.setWindowTitle("五子棋")
        self.setFixedSize(self.size * self.n, self.size * self.n + self.margin)
        self.pix = QPixmap(self.size * self.n, self.size * self.n + self.margin)
        self.point = None

        self.newgame_button = Button(self)
        self.newgame_button.setText("新局")
        self.newgame_button.setStyleSheet("color:white; background-color:blue")
        self.newgame_button.move(self.size * self.n // 4, self.size * self.n)
        self.newgame_button.clicked.connect(self.newgame)

        self.setting_button = Button(self)
        self.setting_button.setText("设置")
        self.setting_button.setStyleSheet("color:white; background-color:blue")
        self.setting_button.move(self.size * self.n * 2 // 4, self.size * self.n)
        self.setting_button.clicked.connect(self.setting)
        self.setting_window = Setting()

        self.withdraw_button = Button(self)
        self.withdraw_button.setText("悔棋")
        self.withdraw_button.setStyleSheet("color:white; background-color:gray")
        self.withdraw_button.move(self.size * self.n * 3 // 4, self.size * self.n)
        self.withdraw_button.clicked.connect(self.withdraw)

    def paintEvent(self, event):
        painter = QPainter(self)
        p = QPainter(self.pix)

        if not self.start:
            p.setPen(BOARD_COLOR)
            p.setBrush(QBrush(BOARD_COLOR))
            p.drawRect(0, 0, self.size * self.n, self.size * self.n + self.margin)
            p.setPen(Qt.black)
            for i in range(self.n):
                p.drawLine(self.size * i + self.size // 2, self.size // 2,
                           self.size * i + self.size // 2, self.size * self.n - self.size // 2)
                p.drawLine(self.size // 2, self.size * i + self.size // 2,
                           self.size * self.n - self.size // 2, self.size * i + self.size // 2)

            for i, j in self.sequence:
                if self.table[i][j] == VACANT:
                    continue
                color = Qt.black if self.table[i][j] == BLACK else Qt.white
                p.setPen(color)
                p.setBrush(QBrush(color))
                self.count += 1
                p.drawEllipse(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                              self.dia, self.dia)

                if self.show_step:
                    color = Qt.white if self.table[i][j] == BLACK else Qt.black
                    p.setPen(color)
                    p.setFont(QFont("Bold", 16))
                    p.drawText(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                               self.dia, self.dia, Qt.AlignCenter, str(self.count))

        # 若当前轮到白棋，则计算出下一步的落子位置
        if not self.finish and not self.black:
            i, j = search(self.table, self.sequence)
            self.point = (i, j)

        if self.point:
            color = Qt.black if self.black else Qt.white
            p.setPen(color)
            p.setBrush(QBrush(color))
            i, j = self.point
            if (i, j) not in self.sequence and 0 <= i < self.n and 0 <= j < self.n:
                self.count += 1
                if not self.start:
                    self.start = True
                    self.withdraw_button.setStyleSheet("color:white; background-color:blue")
                self.sequence.append((i, j))
                self.table[i][j] = BLACK if self.black else WHITE
                p.drawEllipse(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                              self.dia, self.dia)

                if self.show_step:
                    color = Qt.white if self.black else Qt.black
                    p.setPen(color)
                    p.setFont(QFont("Bold", 16))
                    p.drawText(j * self.size + (self.size - self.dia) // 2, i * self.size + (self.size - self.dia) // 2,
                               self.dia, self.dia, Qt.AlignCenter, str(self.count))

                self.black = not self.black

            result = judge(self.table)
            if result:
                p.setPen(Qt.red)
                i1, j1, i2, j2, self.winner = result
                x1 = j1 * self.size + self.size // 2
                y1 = i1 * self.size + self.size // 2
                x2 = j2 * self.size + self.size // 2
                y2 = i2 * self.size + self.size // 2
                p.drawLine(x1, y1, x2, y2)
                self.finish = True
            self.point = None

        if self.withdraw_point:
            p.setBrush(QBrush(BOARD_COLOR))
            for (i, j) in self.withdraw_point:
                p.setPen(BOARD_COLOR)
                p.drawEllipse(j * self.size, i * self.size, self.size, self.size)
                p.setPen(Qt.black)
                p.drawLine(j * self.size, i * self.size + self.size // 2,
                           (j + 1) * self.size, i * self.size + self.size // 2)
                p.drawLine(j * self.size + self.size // 2, i * self.size,
                           j * self.size + self.size // 2, (i + 1) * self.size)
            self.withdraw_point = None

        if not self.finish:
            color = Qt.black if self.black else Qt.white
        else:
            color = Qt.black if self.winner == BLACK else Qt.white
        p.setPen(color)
        p.setBrush(QBrush(color))
        p.drawEllipse(self.size * self.n // 10 - self.dia * 3 // 4, self.size * self.n,
                      self.dia * 3 // 2, self.dia * 3 // 2)
        if self.finish:
            p.setPen(Qt.red)
            p.setFont(QFont("Microsoft YaHei", 20))
            p.drawText(QRectF(self.size * self.n // 10 - self.dia * 3 // 4, self.size * self.n,
                              self.dia * 3 // 2, self.dia * 3 // 2), Qt.AlignCenter, "胜")
            self.withdraw_button.setStyleSheet("color:white; background-color:gray")

        painter.drawPixmap(0, 0, self.pix)

        # 若之后轮到白棋，则直接update（而不是等待鼠标点击）
        if not self.black:
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.finish:
                x, y = event.pos().x(), event.pos().y()
                j, i = x // self.size, y // self.size
                self.point = (i, j)
            self.update()

    def newgame(self):
        self.start = False
        self.count = 0
        self.black = True
        self.finish = False
        self.sequence = []
        self.table = [[VACANT for j in range(self.n)] for i in range(self.n)]
        self.withdraw_point = None
        self.withdraw_button.setStyleSheet("color:white; background-color:gray")

    def setting(self):
        self.setting_window.show()

    def withdraw(self):
        if self.start and not self.finish:
            i1, j1 = self.sequence.pop()
            i2, j2 = self.sequence.pop()
            self.withdraw_point = [(i1, j1), (i2, j2)]
            self.table[i1][j1] = VACANT
            self.table[i2][j2] = VACANT
            self.count -= 2
            if not self.sequence:
                self.start = False
                self.withdraw_button.setStyleSheet("color:white; background-color:gray")
