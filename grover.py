import matplotlib.pyplot as plt
import numpy as np
from functools import reduce

from player import Player

def epoch(n = 256, m = 2**256 / 1e15, num_players = 600, GIPS = 224):
    probs = [0 for x in range(num_players)]

    for t in range(1, num_players + 1):
        measuring_players = [Player(x) for x in list(factors(t))]


        outcomes = []
        for pl in measuring_players:
            outcome = pl.make_measure(t, n, m, GIPS)[0]
            outcomes.append(outcome)
       
        if True in outcomes:
            '''
            ret_val = []
            for i, player in enumerate(outcomes):
                if player:
                    ret_val.append(measuring_players[i].get_max_t())


            return ret_val
            '''

            return [measuring_players[i].get_max_t() for i, player in enumerate(outcomes) if player]

    return None

def factors(n):
    return set(reduce(list.__add__,
                ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))

data = []
for i in range(1000000):
    x = epoch(m = (2**256) / 1e20)
    if x is not None:
        data.extend(x)

bins = np.linspace(min(data), max(data), max(data))
plt.figure()
plt.hist(data, bins = bins)
plt.show()


