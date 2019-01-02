#!/usr/bin/python3

moveBall = "moveBall"
movePawn = "movePawn"
class Action:
    """
    Objet pour représenter les actions. 
    """
    def __init__(self, game, x_init, y_init, x_final, y_final, dtype="movePawn"):
        """
        Constructeur d'Action

        param :
            game: Board à utiliser par défault
            x_init, y_init : Position initial pour l'action
            x_final, y_final : Position final pour l'action
            dtype : type de l'action
        """
        self.init_pos = (x_init, y_init)
        self.final_pos = (x_final, y_final)
        self.game = game
        self.type=dtype

    def do(self, board=None, force=False):
        """
        Méthde pour appliquer l'action au Board.

        param :
            board: Board à utiliser pour appliquer l'action (si None, utilisation du board par default)
            force: Boolean pour forcer l'action ou Non, (forcé permet de ne pas faire les vérifications avant application)
        """
        if board is None:
            self.game.__getattribute__(self.type)(*(self.init_pos+self.final_pos ),force=force)
        else:
            board.__getattribute__(self.type)(*(self.init_pos+self.final_pos ),force=force)

    def undo(self, board=None):
        """
        Méthode pour annuler l'action représenter.

        param :
            board: Board à utiliser pour appliquer l'action (si None, utilisation du board par default)
        """
        if board is None:
            self.game.__getattribute__(self.type)(*(self.final_pos+self.init_pos ), force=True)
        else:
            board.__getattribute__(self.type)(*(self.final_pos+self.init_pos ), force=True)
        
    def __eq__(self, other):
        return self.type==other.type and self.init_pos == other.init_pos and self.final_pos==other.final_pos

    def __repr__(self):
        return "<type="+self.type + " "+ str(self.init_pos) + " , "+ str(self.final_pos) +" at "+hex(id(self))+">"
