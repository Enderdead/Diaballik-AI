#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np
from model.action import Action


HEIGHT = 7
WIDTH = 7

class Board():
    def __init__(self):
        self.pawns = [[ [x,0] for x in range(WIDTH)],\
                      [[x,HEIGHT-1] for x in range(WIDTH)]]
        self.balls  = [[3,0],[3,6]]
        self.current_player = 0  
        self.state = [0,0]

    def movePawn(self, x_init, y_init, x_final, y_final, force=False):
        if force:
            index = self.pawns[self.current_player].index([x_init,y_init])
            self.pawns[self.current_player][index] = [x_final, y_final]
            return True
        # verification de la position initial
        if not [x_init, y_init] in self.pawns[self.current_player]:
            return False
        
        # verif du delta
        if not [x_final-x_init, y_final-y_init] in [[1,0],[0,1],[-1,0],[0,-1]]:
            return False
        
        # Verif d'un element externe
        if [x_final, y_final] in self.pawns[0] or [x_final, y_final] in self.pawns[1]:
            return False
        
        # Verif de la balle
        if [x_init,y_init] in self.balls:
            return False
        
        #Verif des bordures
        if not (  0<=x_final<WIDTH and 0<=y_final<HEIGHT):
            return False

        #Verif des actions déjà faites
        if self.state[0]>=3:
            return False
        
        #Application
        index = self.pawns[self.current_player].index([x_init,y_init])
        self.pawns[self.current_player][index] = [x_final, y_final]

        self.state[0]+=1
        self.updatePlayer()
        return True


    def moveBall(self, x_init, y_init, x_final, y_final, force=False):
        if force:
            self.balls[self.balls.index([x_init,y_init])] = [x_final, y_final]
            return True

        # verification de la position initial
        if not [x_init, y_init] in self.balls:
            return False
        
        # Verif si la destination est sur un pion
        if not [x_final, y_final] in self.pawns[self.current_player]:
            return False

        # Verif si il y a pas de connerie entre les deux 
        coef_x = (x_final - x_init)
        coef_y = (y_final - y_init)

        if coef_x!=0 and coef_y!=0 and abs(coef_x)!=abs(coef_y):
            return False

        if coef_x!=0: coef_x /= abs((x_final - x_init))
        if coef_y!=0: coef_y/=abs((y_final - y_init))

        #print(coef_x, coef_y)
        #print(max(  y_final-y_init , x_final- x_init  ))
        for i in range(max(  y_final-y_init , x_final- x_init  )-1):
            if [x_init + (i+1)*coef_x, y_init + (i+1)*coef_y] in self.pawns[0] or [x_init + (i+1)*coef_x, y_init + (i+1)*coef_y] in self.pawns[1]: 
                return False
        # Application
        self.balls[self.current_player] = [x_final, y_final]
        self.state[0]+=1
        self.updatePlayer()


    def getActions(self):
        # Génération des actions movePawns
        actions = list()
        if self.state[0]<3:
            for [x,y] in self.pawns[self.current_player]:
                # si le pion a la balle

                if [x,y] in self.balls:
                    continue

                for [x_d, y_d] in [1,0],[0,1],[-1,0],[0,-1]:
                    # Si la destination est hors zone
                    if  not ( (0<=x+x_d<WIDTH) and (0<=y+y_d<HEIGHT)):
                        continue
                    
                    # Si il y a un autre pion à la destination
                    if [x+x_d, y+y_d] in self.pawns[0] or [x+x_d, y+y_d] in self.pawns[1]:
                        continue

                    
                    
                    actions.append(Action(self, x, y, x+x_d, y+y_d,dtype="movePawn"))

        if self.state[0]<3:
            x_ball, y_ball = self.balls[self.current_player]
            for [x, y] in self.pawns[self.current_player]:
                # Si je suis le pion osef
                if [x, y] == [x_ball, y_ball]:
                    continue
                # Deux cas de figure, diagonal ou linear
                coef_x = (x - x_ball)
                coef_y = (y - y_ball)

                if coef_x!=0 and coef_y!=0 and abs(coef_x)!=abs(coef_y):
                    continue

                if coef_x!=0: coef_x /= abs((x - x_ball))
                if coef_y!=0: coef_y /=abs((y - y_ball))
                collided = False
                for i in range(max(  abs(y-y_ball) , abs(x- x_ball)  )-1):
                    if [x_ball + (i+1)*coef_x, y_ball + (i+1)*coef_y] in self.pawns[0] or [x_ball + (i+1)*coef_x, y_ball + (i+1)*coef_y] in self.pawns[1]: 
                        collided = True
                        break
                
                if not collided:
                    actions.append(Action(self, x_ball, y_ball, x, y,dtype="moveBall"))

        return actions


    def winner(self):
        if self.balls[0][1] == HEIGHT-1:
            return -1
        if self.balls[1][1] == 0:
            return 1
        return 0

    def updatePlayer(self):
        if self.state[0]>=3:
            self.current_player = (self.current_player+1)%2
            self.state = [0]

    def copy(self):
        bb = Board()
        bb.state = self.state.copy()
        bb.balls = self.balls.copy()
        bb.pawns = self.pawns.copy()
        bb.current_player = self.current_player
        return bb

    def show(self):
        mat = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        for team in range(2):
            for pawn in self.pawns[team]:
                mat[pawn[1]][pawn[0]] = team*2 - 1
        for y in range(len(mat)):
            for x in range(len(mat[y])):
                if [x,y] in self.balls:
                    mat[y][x] = mat[y][x]*2
        plt.matshow(mat)
        plt.show()


    def get_actions_board_raw(self, actions):
        result = list()
        for action in actions:
            action.do(board=self, force=True)
            result.append(self.get_board_raw())
            action.undo(board=self)
        return result


    def get_board_raw(self):
        mat_pawns = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        for team in range(2):
            for pawn in self.pawns[team]:
                mat_pawns[pawn[1]][pawn[0]] = team*-2 + 1  
        mat_balls = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        for ball in self.balls:
            mat_balls[ball[1]][ball[0]] = self.balls.index(ball)*-2 + 1

        return np.dstack([np.array(mat_pawns), np.array(mat_balls)])


if __name__ == "__main__":
    from random import choice
    a = Board()
    
    i = 0
    while a.winner() == -1:
        try:
            choice(a.getActions()).do()
        except:
            break
        i += 1
    print(i)
    print(a.winner())
    a.show()
    #print(a.movePawn(1,0,1,1)) 
    #print(a.movePawn(0,0,0,1, force=True))
    #a.moveBall(3,0,2,1)
