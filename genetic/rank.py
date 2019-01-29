from network.tcptalks import TCPTalks, NotConnectedError
from threading import Thread, Lock, Semaphore
from time import sleep
from random import randint
from multiprocessing import Process
from model.board import Board
from alpha_beta.agent import MinMaxIa

GET_THREAD_OPCODE = 0x11
COMPUTE_OPCODE    = 0x12
RETURN_OPCODE     = 0X13

TREE_DEPTH = 6

class Ranker:
    class ComputerProxy(TCPTalks):
        def __init__(self, parent, ip, port=25565, name=None, password=None):
            TCPTalks.__init__(self, ip, port,id=name, password=password)
            self.parent = parent
            self.bind(RETURN_OPCODE, self.receive_data)

        def compute(self, first, second, thread_id):
            self.send(COMPUTE_OPCODE, thread_id, first, second)

        def receive_data(self,  thread_id, winner, looser):
            print("lol")
            print(self.parent)
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


    def rank(self, people):
        self.epoch = list() # Liste de list. Chaque sous list représente les perdant de la vagues
        self.next_wave = list()
        
        while len(people)!=1:
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
            self.next_wave = list()
        return self.epoch


    def receive_data(self,computer, thread_id, winner, looser): 
        """
        Méthode pour les computers afin de reporter leurs résultat
        """
        print("lol")
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
            print("mdr")
            self.proco = Process(target=self.run, args=())
            self.proco.start()

        def run(self):
            print("COUCOU")
            curBoard = Board()
            i = 0
            while curBoard.winner()==-1:
                i+=1
                ia = MinMaxIa(curBoard,weight= self.players[curBoard.current_player])
                ia.compute(TREE_DEPTH)
                ia.do_best(curBoard)
                print(i)
                del ia
                if (i%10 )== 0:
                    curBoard.show()
            
            self.recall(RETURN_OPCODE, self.thread_id, self.players[0], self.players[1])

    def __init__(self, port=25565, password=None, nb_thread=1):
        TCPTalks.__init__(self, port=port,password=password)
        self.nb_thread = nb_thread
        self.bind(GET_THREAD_OPCODE,self.get_thread_number)
        self.bind(COMPUTE_OPCODE, self.compute)
        self.threads = list()

    def get_thread_number(self):
        return self.nb_thread
    
    def compute(self, thread_id, first, second):
        print("pardon ?")
        ComputeServer.Thread(thread_id, first, second, self.send)
        print("ccoucou")
