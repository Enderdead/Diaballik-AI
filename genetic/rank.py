from network.tcptalks import TCPTalks, NotConnectedError
from threading import Thread, Lock, Semaphore
from time import sleep
from random import randint
from multiprocessing import Process
from model.board import Board
from alpha_beta.agent import MinMaxIa
from copy import deepcopy
from random import shuffle


GET_THREAD_OPCODE = 0x11
COMPUTE_OPCODE    = 0x12
RETURN_OPCODE     = 0X13

TREE_DEPTH = 4

class Ranker:
    class ComputerProxy(TCPTalks):
        def __init__(self, parent, ip, port=25565, name=None, password=None):
            TCPTalks.__init__(self, ip, port,id=name, password=password)
            self.parent = parent
            self.bind(RETURN_OPCODE, self.receive_data)

        def compute(self, first, second, thread_id):
            self.send(COMPUTE_OPCODE, thread_id, first, second)

        def receive_data(self,  thread_id, winner, looser):
            self.parent.receive_data(self, thread_id, winner, looser)

    def __init__(self):
        self.computers = list() # Liste des calculateurs (TCP, thread_id)
        self.ready_computers = list() #  Liste des calculateur en attente
        self.receive_lock = Lock() # Lock pour la reception des données
        self.computers_semaphore = Semaphore(0)  # Semaphore pour l'attente du Ranker


    def add_computer(self, ip, port=25565, name=None, password=None):
        """
        Permet d'ajouter des calculateur, ne peux pas etre fait pendant un calcul
        """
        temp_computer = Ranker.ComputerProxy(self, ip, port, name=name, password=password)
        temp_computer.connect()

        if not temp_computer.is_connected:
            raise NotConnectedError()

        threads = temp_computer.execute(GET_THREAD_OPCODE)
        for thread in range(threads):
            self.computers.append((temp_computer,thread))
            self.ready_computers.append((temp_computer,thread))
            self.computers_semaphore.release()


    def rank(self, people, limit=1 ):
        self.epoch = list() # Liste de list. Chaque sous list représente les perdant de la vagues
        self.next_wave = list()
        
        while len(people)>limit:
            # Si c'est impaire j'en enleve un, il est auto dans la prochaine vague
            if (len(people)%2!=0):
                self.next_wave.append(people.pop(randint(0,len(people)-1)))

            self.epoch.append([]) # Ajout de l'epoch courant
            for i in range(len(people)//2): # Je parcourts les matchs
                self.computers_semaphore.acquire() # J'attend un serveur dispo
                self.receive_lock.acquire()
                server, thread_id = self.ready_computers.pop(0)
                server.compute(people[i*2], people[i*2+1], thread_id)
                self.receive_lock.release()
            while len(self.computers)!=len(self.ready_computers):
                sleep(1) # TODO changer ca !
            people = self.next_wave
            shuffle(people)
            self.next_wave = list()
        self.epoch.append(people)
        return self.epoch


    def receive_data(self,computer, thread_id, winner, looser): 
        """
        Méthode pour les computers afin de reporter leurs résultat
        """
        self.receive_lock.acquire()
        self.ready_computers.append((computer, thread_id))
        self.epoch[-1].append(looser)
        self.next_wave.append(winner)
        self.computers_semaphore.release()
        self.receive_lock.release()



class ComputeServer(TCPTalks):
    class Thread():
        def __init__(self, thread_id, p1, p2, recall):
            self.thread_id = thread_id
            self.players = [p1,p2]
            self.recall = recall
            self.proco = Process(target=self.run, args=())
            self.proco.start()

        def run(self):
            curBoard = Board()

            i = 0
            while curBoard.winner()==-1 and i<100:
                i+=1
                ia = MinMaxIa(curBoard,weight= self.players[curBoard.current_player])
                ia.compute(TREE_DEPTH)
                ia.do_best(curBoard)
                del ia

            winner = None
            looser = None
            if (i>=100):
                print("Match nul")
                #Match nul
                score = 0
                for pawn in curBoard.pawns[0]:
                    score+= 1+pawn[1]
                for pawn in curBoard.pawns[1]:
                    score-= 7-pawn[1]

                score += (1+curBoard.balls[0][1])*3
                score -= (7-curBoard.balls[1][1])*3
                if score>0:
                    winner = self.players[0]
                    looser = self.players[1]
                else:
                    winner = self.players[1]
                    looser = self.players[0]
            else:
                print("Match fini")
                winner = self.players[curBoard.winner()]
                looser = self.players[(curBoard.winner()+1)%2]
            self.recall(RETURN_OPCODE, self.thread_id, winner, looser)

    def __init__(self, port=25565, password=None, nb_thread=1):
        TCPTalks.__init__(self, port=port,password=password)
        self.nb_thread = nb_thread
        self.bind(GET_THREAD_OPCODE,self.get_thread_number)
        self.bind(COMPUTE_OPCODE, self.compute)
        self.threads = list()

    def get_thread_number(self):
        return self.nb_thread
    
    def compute(self, thread_id, first, second):
        ComputeServer.Thread(thread_id, first, second, self.send)
