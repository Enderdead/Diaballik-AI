
from math import inf, sqrt, log, isinf
from random import choice
from copy import deepcopy
class Node:
    def __init__(self, action, parent, player):
        self.action = action
        self.player = player
        self.parent = parent
        self.childrens = None
        self.nb_visit = 0
        self.total_score = 0 

    def getChildren(self, cur_board):
        if self.childrens is None:
            next_player = self.player
            if cur_board.state[0]==2:
                next_player = (next_player+1)%2
            self.childrens = [Node(action, self, next_player)  for action in cur_board.getActions()]
        return self.childrens

    def apply(self, board):
        self.action.do(board=board)

    def rollback(self, board):
        self.action.undo(board=board)

    def __repr__(self):
        return "< Node s:"+ str(self.total_score)+" n:"+  str(self.nb_visit) +" act: " + str(self.action)+"at "+ hex(id(self))+">"


class Tree:
    def __init__(self, init_board, ia, side):
        self.N = 0
        self.init_board = deepcopy(init_board)
        self.root = Node(None, None, 0)
        self.ia = ia
        self.side = side # 1 = j1  |  -1 = j2


    def compute(self):
        cur_node = self.root
        cur_board = deepcopy(self.init_board)
        # On cherche le noeud a explorer
        while cur_node.nb_visit!=0:
            childrens = cur_node.getChildren(cur_board)
            actions = [children.action for children in childrens]
            probas, _ = self.ia.eval(cur_board.get_board_raw(), cur_board.get_actions_board_raw(actions))
            weights = [0 for children in childrens]
            for i in range(len(childrens)):
                try: 
                    weights[i]  = self.side*childrens[i].total_score/childrens[i].nb_visit  + probas[i]*sqrt(2) * sqrt(cur_node.nb_visit)/ (1+childrens[i].nb_visit)
                    #weights[i] = childrens[i].total_score/childrens[i].nb_visit + sqrt(2) * sqrt(log(cur_node.nb_visit)/childrens[i].nb_visit)
                except ZeroDivisionError:
                    weights[i] = inf
            
            if max(weights) == inf:
                cur_node = childrens[choice(list(filter(lambda index: isinf(weights[index]), range(len(weights)))))]
            else:
                cur_node =  childrens[weights.index(max(weights))]
            #print(childrens)
            cur_node.apply(cur_board)
        #TODO ce score n'est pas -1 ou 1 mais [-1,1]
        score = self.ia.get_score(cur_board.get_board_raw())
        #ROOL BACK
        while not cur_node is None:
            cur_node.nb_visit+=1
            cur_node.total_score+=score
            cur_node = cur_node.parent          


    def get_best(self):
        return max(self.root.childrens, key=lambda element: self.side*element.total_score/element.nb_visit).action


    def do_best(self, board):
        action = max(self.root.childrens, key=lambda element:self.side*element.total_score/element.nb_visit).action
        action.do(board=board)
    