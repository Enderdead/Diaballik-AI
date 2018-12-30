from argparse import ArgumentParser
from learning.client import Client


parser = ArgumentParser()
name = parser.add_argument('-n', '--name', type=str, default=None)
name = parser.add_argument('-i', '--ip', type=str, default="127.0.0.1")

args = parser.parse_args()


a = Client(args.ip,ids=args.name)
a.init()
a.compute()