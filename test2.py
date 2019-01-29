from genetic.rank import  Ranker
from genetic.people import Genetic

r = Ranker()
r.add_computer("127.0.0.1")
print("computer addded !")
gene = Genetic(r, "./log")
gene.compute()
