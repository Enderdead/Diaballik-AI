from tkinter import * 
from random import choice
from mcts.tree import *
from CNN.network import DeepNeuronalNetwork
from pickle import load

class Window():
    def __init__(self, board, width=600, height=600, margin=10, width_board=7, height_board=7):
        self.root = Tk()
        self.game = board
        self.width = width
        self.height = height
        self.margin = margin
        self.width_board = width_board
        self.height_board = height_board


        self.canvas =  Canvas(self.root,width=self.width, height=self.height, background='white')
        self.canvas.pack()
        # Cadre
        self.canvas.create_line(self.margin,self.margin,self.width-self.margin,self.margin,self.width-self.margin,self.height-self.margin,self.margin,self.height-self.margin,self.margin,self.margin,width=3)

        self.button = Button(self.root,text="IA play", command=self.compute_button)
        self.button.pack()

        for i in range(self.width_board):
            self.canvas.create_line(self.margin+i*((self.width-self.margin*2)/self.width_board),self.margin,self.margin+i*((self.width-self.margin*2)/self.width_board),self.height-self.margin,width=3)

        for i in range(self.height_board):
            self.canvas.create_line(self.margin,self.margin+ i*((self.height-self.margin*2)/self.height_board),self.width-self.margin,self.margin+ i*((self.height-self.margin*2)/self.height_board),width=3)

        #              j1     j2     ghost
        self.pawns = [list(),list(),list()]

        for i in range(self.width_board):
            self.pawns[0].append(self._write_dot(i, 0, 10, fill="blue"))
        
        for i in range(self.width_board):
            self.pawns[1].append(self._write_dot(i, self.height_board-1, 10, fill="red"))
                
        self.balls = list()
        self.balls.append(self._write_dot(3,0,25,fill="white"))
        self.balls.append(self._write_dot(3,6,25,fill="white"))

        self.ghost = list()

        self.state = "select"
        self.pos_selected = [-1,-1]
        self.ghost_pos = list()

        self.ia = DeepNeuronalNetwork()
        self.ia.start()
        datas = open("./log/12-30_23:03:43-kernel.data","rb")
        kernels = load(datas)
        self.ia.load_kernel(kernels)

        self.human_player = 0
        self.root.bind("<Button 1>", self.compute_click)


    def _write_dot(self, x, y, margin, **kwargs):
        return self.canvas.create_oval(self.margin+0.2*x + margin +x * (self.width-self.margin*2)/self.width_board ,\
                        self.margin+0.2*y + margin + y*(self.height-self.margin*2)/self.height_board ,\
                        self.margin+0.2*x -margin + (x+1) * (self.width-self.margin*2)/self.width_board ,\
                        self.margin+0.2*y - margin + (y+1)*(self.height-self.margin*2)/self.height_board , **kwargs)


    def compute_click(self, event):
        if self.game.current_player!=self.human_player:
            return
        x, y = event.x, event.y
        x_temp = int(x*self.width_board/self.width)
        y_temp = int(y*self.height_board/self.height)
        x = int( (x+1.2*x_temp)*self.width_board/self.width)
        y = int( (y+1.2*y_temp)*self.height_board/self.height)
        print(x,y)
        if self.state == "select":
            
            if [x,y] in self.game.pawns[self.human_player]:
                self.state= "choose"
                self.pos_selected =[x,y]
                self.show_actions()
            return 

        if self.state =="choose":
            if not [x,y] in self.ghost_pos:
                self.clean_ghost()
                self.state = "select"
                return 
            # On réalise l'action

            action = list(filter(lambda action: action.init_pos ==tuple(self.pos_selected) and action.final_pos ==(x,y) ,self.game.getActions()))[0]
            action.do()
            self.state = "select"
            self.clean_ghost()

            self.update()

    def show_actions(self):
        actions = list(filter(lambda element: element.init_pos ==tuple(self.pos_selected) ,self.game.getActions()))
        movePawns = list(filter(lambda element: element.type=="movePawn",actions))
        moveBalls = list(filter(lambda element: element.type=="moveBall",actions))
        print(movePawns)
        for action in movePawns:
            self.ghost.append(self._write_dot(*action.final_pos, 10, fill="gray"))
            self.ghost_pos.append(list(action.final_pos))

        for action in moveBalls:
            self.ghost.append(self._write_dot(*action.final_pos, 25, fill="gray"))
            self.ghost_pos.append(list(action.final_pos))

    def clean_ghost(self):
        self.ghost_pos = list()
        for element in self.ghost:
            self.canvas.delete(element)
        self.ghost = list()

    def update(self):
        for i in range(len(self.game.pawns[0])):
            x, y = self.game.pawns[0][i]
            self.canvas.coords(self.pawns[0][i], self.margin+0.2*x + 10 +x * (self.width-self.margin*2)/self.width_board ,\
                        self.margin+0.2*y + 10 + y*(self.height-self.margin*2)/self.height_board ,\
                        self.margin+0.2*x -10 + (x+1) * (self.width-self.margin*2)/self.width_board ,\
                        self.margin+0.2*y - 10 + (y+1)*(self.height-self.margin*2)/self.height_board)

        for i in range(len(self.game.pawns[1])):
            x, y = self.game.pawns[1][i]
            self.canvas.coords(self.pawns[1][i], self.margin+0.2*x + 10 +x * (self.width-self.margin*2)/self.width_board ,\
                        self.margin+0.2*y + 10 + y*(self.height-self.margin*2)/self.height_board ,\
                        self.margin+0.2*x -10 + (x+1) * (self.width-self.margin*2)/self.width_board ,\
                        self.margin+0.2*y - 10 + (y+1)*(self.height-self.margin*2)/self.height_board)

        for i in range(2):
            x,y = self.game.balls[i]
            self.canvas.coords(self.balls[i],self.margin+0.2*x + 25 +x * (self.width-self.margin*2)/self.width_board ,\
                        self.margin+0.2*y + 25 + y*(self.height-self.margin*2)/self.height_board ,\
                        self.margin+0.2*x -25 + (x+1) * (self.width-self.margin*2)/self.width_board ,\
                        self.margin+0.2*y - 25 + (y+1)*(self.height-self.margin*2)/self.height_board)
            


    def compute_button(self):
        if self.game.current_player!= (self.human_player+1%2):
            return
        tree =Tree(self.game, self.ia, {0:1,1:-1}[self.game.current_player])
        for _ in range(1000):
            tree.compute()
        tree.do_best(self.game)
        self.update()
        

    def show(self):
        self.root.mainloop()


