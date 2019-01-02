
from math import inf, sqrt, log, isinf
from random import choice
from copy import deepcopy
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
        self.nb_visit = 0
        self.total_score = 0 

    def getChildren(self, cur_board):
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
            if cur_board.state[0]==2:
                next_player = (next_player+1)%2
            self.childrens = [Node(action, self, next_player)  for action in cur_board.getActions()]
        return self.childrens

    def apply(self, board):
        """
        Permet d'appliquer l'action stockée.
        
        param :
            board: Board à utiliser
        """
        self.action.do(board=board)

    def rollback(self, board):
        """
        Permet d'annuler l'action stockée sur ce noeud.

        board: Board à utiliser
        """
        self.action.undo(board=board)

    def __repr__(self):
        return "< Node s:"+ str(self.total_score)+" n:"+  str(self.nb_visit) +" act: " + str(self.action)+"at "+ hex(id(self))+">"


class Tree:
    """
    Classe support pour effectuer le parcourt d'arbre.
    On notera que cet objet est jetable. (CAD cet objet ne fait q'une seule recherche)
    """
    def __init__(self, init_board, ia, side):
        # TODO il faut prendre plus en compte les tours (CAD les tours intermédiaires).
        """
        Constructeur de Tree

        param: 
            init_board: Board inital pour la recherche
            ia : Ia à utiliser pour faire le parcourt d'arbre et la valuation
            side: joueur qui à la main.
        """
        self.N = 0
        self.init_board = deepcopy(init_board)
        self.root = Node(None, None, 0)
        self.ia = ia
        self.side = side # 1 = j1  |  -1 = j2


    def compute(self):
        """
        Méthode principal permettant de réaliser une itération de l'algorithme.
        Les méthodes de résultat sont appelables après le premier appel de compute()
        """
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
        """
        Retourne la meilleur action à faire à partir de la sitation donnée dans le constructeur
        """
        return max(self.root.childrens, key=lambda element: self.side*element.total_score/element.nb_visit).action


    def do_best(self, board):
        """
        Applique la meilleur action à faire à partir de la sitation donnée dans le constructeur sur board

        param:
            board: Board à utiliser pour appliquer la meilleur action trouvée.
        """
        action = max(self.root.childrens, key=lambda element:self.side*element.total_score/element.nb_visit).action
        action.do(board=board)
    