import sys
import argparse
from PyQt5.QtWidgets import QApplication
from gui import Board

parser = argparse.ArgumentParser(description='五子棋')
parser.add_argument('--n', type=int, default=19, metavar='N', help='棋盘的行/列数（默认：19）')
parser.add_argument('--width', type=int, default=800, metavar='N', help='棋盘的宽度（默认：800）')
parser.add_argument('--margin', type=int, default=80, metavar='N',
                    help='棋盘的下边距，棋盘的高度等于棋盘的宽度+下边距（默认：80）')
# parser.add_argument('--cuda', action='store_true', default=True, help='是否使用CUDA加速（默认：是）')
args = parser.parse_args()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    board = Board(args.n, args.width, args.margin)
    board.show()
    sys.exit(app.exec_())
