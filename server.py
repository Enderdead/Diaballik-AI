from learning.master import Master


server = Master(nb_clients=2)

server.start()
server.wait()