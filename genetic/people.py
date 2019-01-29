from pickle import dump
from random import random, shuffle
from datetime import datetime
from os.path import join
from copy import deepcopy
import numpy as np
MAX_WEIGHT = 10
MIN_WEIGHT =-10

class Genetic:
    def __init__(self, ranker, path, people_size=40, people_data=None, nb_param=5):
        self.save_path = path
        self.ranker = ranker
        self.gen = 0
        if not people_data:
            self.people = list()
            for _ in range(people_size):
                self.people.append(list(np.random.random(nb_param)*(MAX_WEIGHT-MIN_WEIGHT)+(MIN_WEIGHT-0)))  
        else:
            self.people = people_data
            self.people_size = len(self.people)
    
    def save(self, people):
        file_name = "saveGen_"+str(self.gen) + datetime.now().strftime("%m_%d_%H_%M")
        with open(join(self.save_path,file_name),"wb") as file_save:
            dump(people,file_save)
        

    def compute(self):
        self.gen +=1
        ranked_people = self.ranker.rank(self.people)
        # [[[1, 1, 0, -1, 0], [1, 1, 1, 1, 1], [-1, -1, 0, 0, 0], [1, 0, 1, 1, 0]], [[1, 0.5, 0, 0, 0], [1, 0.5, 1, 1, 1]], [[1, 0.5, 0, 0, -1]]]
        saved_people = list()
        # keep best 20%
        while len(saved_people)<(self.people_size*0.2):
            saved_people.append(ranked_people[-1].pop)
            if ranked_people[-1] == list():
                ranked_people = ranked_people[:-1]

        # muted people from best element 20%
        muted_people = list()
        for good_guy in saved_people:
            temp = deepcopy(good_guy)
            for i in range(len(temp)):
                if random()>0.7:
                    temp[i]+=random()*4-2
            muted_people.append(temp)
        
        # twisted people from best element 20%
        twisted_people = list()
        for _ in range(len(saved_people)):
            first_guy = int(random()*len(saved_people))
            second_guy = int(random()*len(saved_people))
            temp  = deepcopy(saved_people[first_guy])
            for i in range(len(temp)):
                if random()>0.5:
                    temp[i] = saved_people[second_guy]
        
        random_people = list()
        for _ in range(self.people_size*0.4):
            random_people.append(list(np.random.random(nb_param)*(MAX_WEIGHT-MIN_WEIGHT)+(MIN_WEIGHT-0)))
        
        self.people =shuffle( saved_people + twisted_people + random_people + muted_people)
        self.save(self.people)