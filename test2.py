from genetic.rank import  Ranker
from genetic.people import Genetic

r = Ranker()
r.add_computer("192.168.12.36")
r.add_computer("192.168.12.44")
r.add_computer("192.168.12.38")

print("computers addded !")
gene = Genetic(r, "./log")
gene.compute()
