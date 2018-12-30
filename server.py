from argparse import ArgumentParser
from learning.master import Master


parser = ArgumentParser()
name = parser.add_argument('-p', '--path', type=str, default=None)

args = parser.parse_args()

server = Master(nb_clients=50, path=args.path)

server.start()
server.wait()