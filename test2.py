from genetic.rank import  Ranker
from genetic.people import Genetic
import os

data = None
if len(os.listdir("./log"))>0:
    listfiles = os.listdir("./log")
    files_filtred = [name[10:] for name in listfiles]
    index = files_filtred.index(max(files_filtred))
    data = "./log" + listfiles[index]


r = Ranker()
r.add_computer("127.0.0.1")
r.add_computer("192.168.12.36")
r.add_computer("192.168.12.44")
r.add_computer("192.168.12.38")

print("computers addded !")

gene = Genetic(r, "./log", people_data=data)
gene.compute()
