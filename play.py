from model.board import Board
from interface.window import Window
from mcts import tree

board = Board()

win = Window(board)
win.show()

#TODO faire = 0 quand je perd