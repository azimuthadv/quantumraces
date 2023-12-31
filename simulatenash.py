from random import randrange, choices, uniform
import twoplayer as tp
from itertools import chain
import numpy as np
import matplotlib.pyplot as plt

D = tp.D


fname = 'output.txt'
num_simulations = 10000000

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
                alice_strat.append([float(x) for x in data[1:-1]])
                alice_prob.append(float(data[-1]))
            elif data[0] == 'Bob':
                bob_strat.append([float(x) for x in data[1:-1]])
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
    num_forks = 0
    num_blocks = 0
    for sim in range(num_simulations):
        idx = randrange(len(strats))
        strat_to_play = strats[idx]
        alice_strat = list(chain(*choices(strat_to_play[0], weights = strat_to_play[2])))
        bob_strat = list(chain(*choices(strat_to_play[1], weights = strat_to_play[3])))
        strat_length = len(alice_strat)
        tat, tbt = [], []

        for i in range(strat_length):
            a = alice_strat[i]
            b = bob_strat[i]
            r = uniform(0, 1)
            tat.append(sum(alice_strat[:i+1])) #keep track of the total amount of time alice and bob are measuring
            tbt.append(sum(bob_strat[:i+1]))

            if tat[i] < tbt[i]: #alice is measuring first
                if r <= tp.p_i(a): #alice has a successful measurement
                    num_blocks = num_blocks + 1
                    r = uniform(0, 1)
                    if i == 0:
                        if r <= tp.p_i(a): #bob measures at alice's time
                            num_forks = num_forks + 1
                    else:
                        if r <= tp.p_i(np.abs(tat[i] - tbt[i-1])):
                            num_forks = num_forks + 1
                else: #alice does not have a succesful measurement
                    if r <= tp.p_i(b):
                        num_blocks = num_blocks + 1
                        r = uniform(0, 1)
                        if i != strat_length:
                            if r <= tp.p_i(np.abs(tbt[i] - tat[i])):
                                num_forks = num_forks + 1

            elif tat[i] > tbt[i]: #bob is measuring first
                if r <= tp.p_i(b): #bob has a successful measurement
                    num_blocks = num_blocks + 1
                    r = uniform(0, 1)
                    if i == 0:
                        if r <= tp.p_i(b):
                            num_forks = num_forks + 1
                    else:
                        if r <= tp.p_i(np.abs(tbt[i] - tat[i-1])):
                            num_forks = num_forks + 1
                else: #bob's measurement fails
                    if r <= tp.p_i(a):
                        num_blocks = num_blocks + 1
                        r = uniform(0, 1)
                        if i != strat_length:
                            if r <= tp.p_i(np.abs(tat[i] - tbt[i])):
                                num_forks = num_forks + 1
            else: #alice and bob are measuring at the same time
                if r <= tp.p_i(a):
                    r = uniform(0, 1)
                    if r <= tp.p_i(b):
                        num_forks = num_forks + 1
                    

    if num_blocks == 0:
        return 0
    else:
        return num_forks / num_blocks


def plot_fork_rate():
    original_D = tp.D
    max_Ks = [np.floor(np.pi/4 * np.sqrt(original_D/x)) for x in range(1, 10)]
    print(max_Ks)
    fork_rate = []
    for i in range(len(max_Ks)):
        print(max_Ks[i])
        tp.main(max_K = max_Ks[i])
        fork_rate.append(simulate_strats(fname))

    print(fork_rate)

    plt.figure()
    plt.plot([1/x for x in range(1, 10)], fork_rate)
    plt.xlabel('Maximum Fraction of Search Space')
    plt.ylabel('Fork Rate')
    plt.title('Forking Rate when Mining Optimally')
    plt.grid(True)
    plt.show()
    plt.savefig('result.png')


#plot_fork_rate()
print(simulate_strats(fname))