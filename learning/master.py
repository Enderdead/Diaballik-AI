#!/usr/bin/python3
from network.tcptalks import TCPTalksServer, ForeverAloneError
from CNN.network import DeepNeuronalNetwork
from learning.constant import *
from threading import Thread
from queue import Queue, Empty
from datetime import datetime, timedelta
from pickle import load

class Master(TCPTalksServer):
    """
    Serveur dédié à l'apprentissage du réseau de neurone.
    Cette classe va accepter toutes les connexions et se contenter de répondre aux requetes fait par les clients qui réalisent les calcules.
    """
    def __init__(self, nb_clients=8, path=None):
        """
        Constructeur de cette classe Serveur.

        param:
            nb_clients : Nombre de client max pour ce servueur.
            path : Chemin vers un fichier contenant les kernels à utiliser pour initialiser le réseau de neurones.
        """
        TCPTalksServer.__init__(self,NbClients=nb_clients)
        self.running = False
        self.connect_thread = None

        self.bind(GET_KERNEL_OPCODE, self._get_kernels)
        self.bind(PUSH_EXEMPLE_OPCODE, self._push_exemple)

        self.ia = DeepNeuronalNetwork()
        self.ia.start()
        if not path is None:
            datas = open(path,"rb")
            kernels = load(datas)
            self.ia.load_kernel(kernels)
            print("Kernel loaded !")

        self.log_queue = Queue()
        self.get_date = lambda : datetime.now().strftime("%m-%d_%H:%M:%S")

        self.delta_save = timedelta(minutes=20)
        self.cur_save = datetime.now()

    def start(self):
        """
        Lance un thread pour gérer les connexions avec les clients.
        """
        self.running = True
        def connect_loop():
            while self.running:
                try:
                    self.connect(timeout=5)
                except ForeverAloneError:
                    pass
        self.connect_thread = Thread(target=connect_loop)
        self.connect_thread.start()

    def _get_kernels(self, client_id):
        """
        Méthode interne réservé aux clients.
        Cette méthode permet aux clients de récuperer le kernel à jour.
        """
        self.log_queue.put("{} - Client {} ask kernel".format(self.get_date(), client_id))
        return self.ia.get_kernel()

    def _push_exemple(self, client_id, coef, board, actions, act_selected, winner):
        """
        Méthode interne réservé aux clients.
        Cette méthode va permettre aux clients de donner leurs exemples.
        """
        self.log_queue.put("{} - Client {} put exemple : [winner: {}, coef: {} ]".format(self.get_date(), client_id, winner, coef))
        self.ia.fit(board, actions, act_selected, winner, coef=coef)

    def wait(self):
        """
        Boucle principal de la classe Serveur.
        Cette boucle va générer les logs dans un fichier syslog. Ce fichier Log récapitule toutes les entrées sorties avec ce serveur.
        Cette boucle va également faire des sauvegardes régulière des kernels.
        """
        log_file = open("./log/syslog","a")
        try:
            while True:
                if datetime.now()>(self.cur_save+self.delta_save):
                    kernel_file = open("./log/{}-kernel.data".format(self.get_date()),"bw")
                    data_r = self.ia.get_kernel(dumped=True)
                    kernel_file.write(data_r)
                    kernel_file.close()
                    self.cur_save = datetime.now()
                    log_file.flush()
                try:
                    data = self.log_queue.get(True, timeout=int(self.delta_save.total_seconds()*0.10)) 
                except Empty:
                    continue
                print(data)
                log_file.write(data+"\n")
                
        except KeyboardInterrupt:
            pass
        log_file.close()
