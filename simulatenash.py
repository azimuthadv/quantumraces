from random import randrange, choices, uniform
import twoplayer as tp
from itertools import chain

D = tp.D


fname = 'output.txt'
num_simulations = 100

def read_from_file(fname):
    c = 0
    alice_strat = []
    bob_strat = []
    alice_prob = []
    bob_prob = []
    strats = {}
    with open(fname) as f:
        line = f.readline()
        while line:
            data = line.strip().split(' ')
            data = [x.strip('[,]') for x in data]
            if data[0] == 'Alice':
                alice_strat.append([int(x) for x in data[1:-1]])
                alice_prob.append(float(data[-1]))
            elif data[0] == 'Bob':
                bob_strat.append([int(x) for x in data[1:-1]])
                bob_prob.append(float(data[-1]))
            elif(data[0] == '-----' and f.readline().split(' ')[0] != '-----'):
                strats[c] = [alice_strat, bob_strat, alice_prob, bob_prob]
                c += 1
                alice_strat = []
                bob_strat = []
                alice_prob = []
                bob_prob = []
            line = f.readline()
    return strats

def simulate_strats(fname):
    strats = read_from_file(fname)
    for sim in range(num_simulations):
        idx = randrange(len(strats))
        strat_to_play = strats[idx]
        alice_strat = list(chain(*choices(strat_to_play[0], weights = strat_to_play[2])))
        bob_strat = list(chain(*choices(strat_to_play[1], weights = strat_to_play[3])))
        strat_length = len(alice_strat)
        num_forks = 0
        tat, tbt = 0, 0

        for i in strat_length:
            a = alice_strat[i]
            b = bob_strat[i]
            r = uniform(0, 1)
            tat = tat + a #keep track of the total amount of time alice and bob are measuring
            tbt = tbt + b
            if tat < tbt: #alice is measuring first
                if r < tp.p_i(a): #alice wins
                    r = uniform(0, 1)
                    if r < tp.p_i(a):
                        num_forks = num_forks + 1
            else: #bob is measuring first
                continue

    return





simulate_strats(fname)