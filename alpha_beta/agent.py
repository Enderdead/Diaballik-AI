#!/usr/bin/python3
from model.board import Board,HEIGHT
from alpha_beta.tree import Node
from math import inf
from copy import deepcopy




### Heuristique 
MAX = 200

def heuristique(funct):
    def result(board, side):
        if(board.winner()==side):
            return MAX 
        result = funct(board, side)
        return result
    return result

def _heuristicPawnAdvance(board, side):
    result = 0
    for pawn in board.pawns[side]:
        result += 2*(1 + pawn[1])*(side==0) + (side==1)*(HEIGHT-pawn[1])*2
    return result

def _heuristicBallAdvance(board, side):
    result = (1 + board.balls[side][1])*(side==0) + (side==1)*(HEIGHT-board.balls[side][1])
    return result

def _heuristicPawnBlocked(board, side):
    result = 0
    for pawn in board.pawns[side]:
        x,y = pawn
        close_dist = HEIGHT
        """
        for own_pawn in board.pawns[0]:
            if own_pawn == pawn :
                continue
            if (own_pawn[0] == x) and (side*-2+1)*(own_pawn[1]-y)>0 and close_dist>abs(own_pawn[1]-y):
                close_dist = abs(own_pawn[1]-y)
        """
        for own_pawn in board.pawns[(side+1)%2]:
            if own_pawn == pawn :
                continue
            if (own_pawn[0] == x) and (side*-2+1)*(own_pawn[1]-y)>0 and close_dist>abs(own_pawn[1]-y):
                close_dist = abs(own_pawn[1]-y)
        result += close_dist
    return result

def _heuristicBallcanMove(board, side):
    to_reverse = board.current_player!=side
    board.current_player = side
    actions = board.getActions()
    result = len(list(filter(lambda x : x.type=="moveBall", actions)))
    if to_reverse:
        board.changePlayer()
    return result

def _heuristicBallcanAdvance(board, side):
    to_reverse = board.current_player!=side
    board.current_player = side
    actions = board.getActions()
    moveBall_act = list(filter(lambda x : x.type=="moveBall", actions))
    result = len(list(filter(lambda x : ((side*-2+1)*(x.final_pos[1] - x.init_pos[1]))>0, moveBall_act)))
    if to_reverse:
        board.changePlayer()
    return result
    
#def _heuristicPawnsConnected(board, side):
#TODO

class MinMaxIa():
    def __init__(self, init_board, weight=[1,1,0,0,0]):
        self.init_board = init_board
        # Le meilleur max trouvé 
        self.alpha = -inf
        # Le meilleur min trouvé 
        self.beta = +inf
        self.heuristiques = {
         _heuristicPawnAdvance: weight[0],
         _heuristicBallAdvance: weight[1],
         _heuristicPawnBlocked: weight[2],
         _heuristicBallcanMove: weight[3],
         _heuristicBallcanAdvance: weight[4],
        }

    def compute(self, nb_plays):
        self.nb_plays = nb_plays
        board = deepcopy(self.init_board)
        self.root = Node(None,None,board.current_player)
        if board.current_player==0:
            self._max(board, self.root, -inf, inf, 0)
        else:
            self._min(board, self.root, -inf, inf, 0)


    def do_best(self, board):
        # On fait les 1 actions
        try:
            if board.current_player ==1:
                mini = min([fils.score for fils in self.root.childrens])
                cur = self.root.childrens[[fils.score for fils in self.root.childrens].index(mini)]
                cur.apply(board)
            else:
                mini = max([fils.score for fils in self.root.childrens])
                cur = self.root.childrens[[fils.score for fils in self.root.childrens].index(mini)]
                cur.apply(board)
        except TypeError:
            if board.current_player ==1:
                cur = self.root.childrens([fils.score for fils in self.root.childrens].index(-inf))
                cur.apply(board)
            else:
                cur = self.root.childrens([fils.score for fils in self.root.childrens].index(inf))
                cur.apply(board)

                
    # Méthode appelé quand c'est à J2 de jouer
    def _min(self, curBoard, parent, alpha, beta, height):
        # si il trouve un truc en dessous de alpha je stop de retour ce min
        # Quand j'appel max, je donne mon meilleur min au travers de beta
        if height>=self.nb_plays:
            #print(self._eval(curBoard, 1)- self._eval(curBoard,-1))
            #curBoard.show()
            return  self._eval(curBoard)

        childrens = parent.getChildren(curBoard,-1)
        result = inf
        for children in childrens:
            # on applique l'action
            children.apply(curBoard)
            # on eval
            children.score = self._max(curBoard, children, alpha, beta, height+1)
            # On annule l'action
            children.rollback(curBoard)
            
            result = min(result, children.score)
            if result <= alpha:
                return result
            
            beta = min(beta, result)

        
        return result

        

    # Méthode appelé quand c'est à J1 de jouer
    def _max(self, curBoard, parent, alpha, beta, height):
        # si il trouve un truc en dessus de beta je stop de retour ce max
        # Quand j'appel min, je donne mon meilleur max au travers de alpha
        if height>=self.nb_plays:
            #print(self._eval(curBoard, 1)- self._eval(curBoard,-1))
            #curBoard.show()
            return self._eval(curBoard)
        result = -inf
        
        childrens = parent.getChildren(curBoard,1)
        for children in childrens:
            children.apply(curBoard)
            children.score = self._min(curBoard, children, alpha, beta, height+1)
            children.rollback(curBoard)
            result = max(result, children.score)
            if result>= beta:
                return result
            
            if result>=alpha:
                alpha = result

        return result

    def _eval(self, board):
        if(board.winner()!=-1):
            return inf if board.winner()==0 else -inf

        result = 0
        for heuristique in self.heuristiques:
            result +=heuristique(board, 0)*self.heuristiques[heuristique]
            result -=heuristique(board, 1)*self.heuristiques[heuristique]
        return result

if __name__ == "__main__":
    a = Board()
    ia = MinMaxIa(a)
    ia.compute(6)
    ia.do_best(a)
