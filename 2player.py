import numpy as np
import matplotlib.pyplot as plt
import itertools

# ===== CONSTANTS =====

N = float(2**256) # number of possible hashes
M = float(2**256 / 1e2) #number of solutions
#K = int(np.ceil(np.pi / 4 * np.sqrt(N) - 3/2)) # number of strategies (number of times to measure)
K = 2
GIPS = 224 # number of grover iterations per second that the quantum computers are capable of


num_plays = 2 # number of times each player can run Grover's algorithm


# =====================


#np.set_printoptions(formatter={'float': lambda x: "{0:0.30f}".format(x)})

def p_i(t):
    theta = float(np.arcsin(1 / (np.sqrt(N / M))))
    return (np.sin(2*((t * GIPS) + 0.5) * theta))**2


# 2 player symmetric case from Troy's paper
def alice_payoff_matrix_troy():
    A = np.empty((K, K))
    for j in range(K):
        for i in range(K):
            if(i < j):
                A[j][i] = p_i(i)
            elif(i == j):
                A[j][i] = p_i(i) * (1 - p_i(j)) + 0.5 * p_i(i) * p_i(j)
            elif(i > j):
                A[j][i] = p_i(i) * (1 - p_i(j))
    return A

def bob_payoff_matrix_troy(A):
    return A.transpose()

# With restarts


#function to get create a matrix of the Cartesian products of inputted arrays
def cartesian(arrays, out = None):
    arrays = [np.asarray(x) for x in arrays]
    dtype = arrays[0].dtype

    cn = np.prod([x.size for x in arrays])
    if out is None:
        out = np.zeros([cn, len(arrays)], dtype = dtype)

    cm = int(cn / arrays[0].size)
    out[:,0] = np.repeat(arrays[0], cm)

    if arrays[1:]:
        cartesian(arrays[1:], out = out[0:cm, 1:])
        for j in range(1, arrays[0].size):
            out[j*cm:(j+1)*cm, 1:] = out[0:cm, 1:]

    return out

#Function: alice_payoff_r: Constructs Alice's payoff matrix with p restarts and [K] possible times

def alice_payoff_r(last_time: int, p: int):
    set_K = np.arange(1, last_time + 1)
    arrs = (set_K for i in range(2**p))
    S = cartesian(arrs)

    
    dim = int(len(set_K)**p)
    # A[0] = total Alice matrix, rest of A's are the payoff matrix for each play
    A = [np.empty((dim, dim), dtype = float) for x in range(p + 1)] 

    for x in range(1, p + 1):
        c = 0 # counter
        for i in range(dim):
            for j  in range(dim):
                A[x][i][j] = get_payoff_element(S, i, j, x, dim)
                A[0] += A[x][i][j]
                c += 1

    return A[0]

# get the [i][j] entry of the payoff matrix for Alice. S is the matrix of Cartesian permutations
def get_payoff_element(S, row, col, play, dim):
    cart = S[row * dim + col]
    strat_length = len(cart) // 2
    alice_strat = cart[strat_length:]
    bob_strat = cart[:strat_length]

    #print('Alice Strat: {}, Bob Strat: {}'.format(alice_strat, bob_strat))

    assert play <= strat_length, 'Only {} plays are allowed in this game, got {}'.format(strat_length, play)


    prefactor = p_i(alice_strat[play - 1])
    c = play - 2
    while(c >= 0):
        prefactor *= (1 - p_i(alice_strat[c]))
        c -= 1

    #create the intervals from Alice's and Bob's strategies:

    #assign matrix elements from these intervals

    return prefactor * intervals(alice_strat, bob_strat, p_i, play)

    # number of cases in matrix is total number of plays + 1

    #return prefactor * element


def intervals(arr1, arr2, p, play):
    x = sum(arr1[:play + 1])

    if x < arr2[0]:
        return p_func(p, [])

    for i in range(len(arr2) - 1):
        #print('{}, {}'.format(sum(arr2[:i+1]), sum(arr2[:i+2])))
        if sum(arr2[0:i+i]) <= x < sum(arr2[0:i+2]):
            return p_func(p, arr2[0:i+1])


    return p_func(p, arr2)

def p_func(p, arr):
    prod = 1

    for i in arr:
        prod *= (1 - p(i))

    return prod


print(alice_payoff_r(K, num_plays))


'''
set_K = np.arange(1, K + 1)
arrs = (set_K for i in range(2**num_plays))
S = cartesian(arrs)

dim = int(len(set_K)**num_plays)

get_payoff_element(S, 0, 3, play = 3)




#print(alice_payoff_r(K, num_plays))
'''
