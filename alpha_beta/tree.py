class Node:
    """
    Classe support pour représenter les noeuds de l'arbre.
    Un noeud contient une action à executer AVANT de rentrer dans ce noeud (poser son pointeur dessus)
    """
    def __init__(self, action, parent, player):
        """
            Constructeur de Node

        param:
            action: Action à stoquer dans ce noeud.
            parent: Noeud parent à ce noeud.
            player: Joueur courant de ce noeud. (pas utilisé)
        """
        self.action = action
        self.player = player
        self.parent = parent
        self.childrens = None
        self.score = None
        self.side = player


    def getChildren(self, cur_board, side):
        #self.side = side
        """
        Cette méthode permet de récupérer une liste des fils de ce noeud. Si c'est le premier appel alors elle va
        utiliser le cur_board pour générer les fils avant de les retourner.

        param :
            cur_board : Board à utiliser pour générer les fils si nécéssaire.

        return : 
            Une liste des Node fils.
        """
        if self.childrens is None:
            next_player = self.player

            next_player = (next_player+1)%2
            self.childrens = [Node(action, self, next_player)  for action in cur_board.getActions()]
        return self.childrens

    def apply(self, board):
        """
        Permet d'appliquer l'action stockée.
        
        param :
            board: Board à utiliser
        """
        return self.action.do(board=board)

    def rollback(self, board):
        """
        Permet d'annuler l'action stockée sur ce noeud.

        board: Board à utiliser
        """
        self.action.undo_safe(board=board)

    def __repr__(self):
        return "< Node side:"+ str(self.side)+" score: "+ str(self.score) +" act: " + str(self.action)+"at "+ hex(id(self))+">"
