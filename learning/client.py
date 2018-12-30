from network.tcptalks import TCPTalks, NotConnectedError
from CNN.network import DeepNeuronalNetwork 
from learning.constant import *
from model.board import Board
from mcts.tree import Tree
from pickle import dumps

class Client(TCPTalks):
    
    def __init__(self, ip, port=25565, ids=None):
        TCPTalks.__init__(self, ip, port, ids)
        self.ia = DeepNeuronalNetwork()
        self.ia.start()

    def init(self):
        self.connect()
        kernels = self.execute(GET_KERNEL_OPCODE)
        self.ia.load_kernel(kernels)

    def compute(self):
        if not self.is_connected:
            raise NotConnectedError()

        try:
            while True:
                # Initialisation : 
                board = Board()
                history_board = list()
                history_choice = list()
                history_actions = list()
                i = 0
                while board.winner() ==0:
                    i+=1
                    # On joue selon l'IA
                    self.tree =Tree(board, self.ia, {0:1,1:-1}[board.current_player])
                    for _ in range(100):
                        self.tree.compute()
                    act = self.tree.get_best()
                    history_board.append(board.get_board_raw())
                    actions = board.getActions()
                    history_choice.append(actions.index(act))
                    history_actions.append(board.get_actions_board_raw(actions))
                    act.do(board=board)

                print("Finish")                    
                self.send(PUSH_EXEMPLE_OPCODE, 1, history_board[-1], history_actions[-1], history_choice[-1],board.winner())
                save_file = open("./log-client/{}-{}.data".format( datetime.now().strftime("%m-%d_%H:%M:%S"),self.id),"wb")
                save_file.write(dumps((history_board, history_choice, history_actions, board.winner())))
                save_file.close()

        except KeyboardInterrupt:
            pass

    

