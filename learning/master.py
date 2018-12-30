#!/usr/bin/python3
from network.tcptalks import TCPTalksServer, ForeverAloneError
from CNN.network import DeepNeuronalNetwork
from learning.constant import *
from threading import Thread
from queue import Queue, Empty
from datetime import datetime, timedelta

class Master(TCPTalksServer):
    def __init__(self, nb_clients=8):
        TCPTalksServer.__init__(self,NbClients=nb_clients)
        self.running = False
        self.connect_thread = None

        self.bind(GET_KERNEL_OPCODE, self._get_kernels)
        self.bind(PUSH_EXEMPLE_OPCODE, self._push_exemple)

        self.ia = DeepNeuronalNetwork()
        self.ia.start()
        self.log_queue = Queue()
        self.get_date = lambda : datetime.now().strftime("%m-%d_%H:%M:%S")

        self.delta_save = timedelta(minutes=20)
        self.cur_save = datetime.now()

    def start(self):
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
        self.log_queue.put("{} - Client {} ask kernel".format(self.get_date(), client_id))
        return self.ia.get_kernel()

    def _push_exemple(self, client_id, coef, board, actions, act_selected, winner):
        self.log_queue.put("{} - Client {} put exemple : winner : {}".format(self.get_date(), client_id, winner))
        self.ia.fit(board, actions, act_selected, winner)

    def wait(self):
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
                    data = self.log_queue.get(False)
                except Empty:
                    continue
                log_file.write(data+"\n")
                
        except KeyboardInterrupt:
            pass
        log_file.close()
