#!/usr/bin/python3

moveBall = "moveBall"
movePawn = "movePawn"
class Action:
    def __init__(self, game, x_init, y_init, x_final, y_final, dtype="movePawn"):
        self.init_pos = (x_init, y_init)
        self.final_pos = (x_final, y_final)
        self.game = game
        self.type=dtype

    def do(self):
        self.game.__getattribute__(self.type)(*(self.init_pos+self.final_pos ))

    def undo(self):
        self.game.__getattribute__(self.type)(*(self.final_pos+self.init_pos ), force=True)
        
    def __repr__(self):
        return "<type="+self.type + " "+ str(self.init_pos) + " , "+ str(self.final_pos) +" at "+hex(id(self))+">"
