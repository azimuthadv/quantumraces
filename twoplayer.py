import numpy as np
import lemkehowson as lh
import sys
import random

# ===== CONSTANTS =====
N = float(2**256) # number of possible hashes
M = float(2**256 / 1e30) #number of solutions
D = float(1e10)
#K = int(np.ceil(np.pi / 4 * np.sqrt(N) - 3/2)) # number of strategies (number of times to measure)
GIPS = 224 # number of grover iterations per second that the quantum computers are capable of
num_plays = 2 # number of times each player can run Grover's algorithm
intvl = 15
K = 600 // intvl
mat_dim = K**num_plays #dimension of payoff matrix

# =====================

original_stdout = sys.stdout

#Calculates the probability of Grover's algorithm finding the marked item after time t.
def p_i(t):
    theta = float(np.arcsin(1 / (np.sqrt(D))))
    return (np.sin(2*((t * intvl * GIPS) + 0.5) * theta))**2

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

def alice_payoff():
    # first get all of the permutations from the cartesian product to index the matrix
    set_K = np.arange(1, K + 1)
    arrs = (set_K for i in range(2*num_plays))
    S = cartesian(arrs)

    #dimension of the payoff matrix
    dim = int(len(set_K)**num_plays)
    #initialize the payoff matrices. There will be a separate one for each play. A[0] will be the total
    A = [np.zeros((dim, dim), dtype=float) for i in range(num_plays + 1)]
    
    #populate each array
    for play in range(1, num_plays + 1):
        for col in range(dim):
            for row in range(dim):
                element = get_element(S, col, row, play, dim)
                A[play][col][row] = element
                A[0][col][row] = A[0][col][row] + A[play][col][row]

    return A[0]


def get_element(S, col, row, play, dim):
    cart = S[col * dim + row]
    strat_length = len(cart) // 2
    alice_strat = cart[:strat_length]
    bob_strat = cart[strat_length:]
    #print('Alice Strat: {}, Bob Strat: {}'.format(alice_strat, bob_strat))
    assert play <= strat_length, 'Only {} plays are allowed in this game, got {}'.format(strat_length, play)
    
    #first calculate the prefactor for the matrix
    prefactor = p_i(alice_strat[play-1])
    if play > 1:
        c = play - 2
        while c >= 0:
            prefactor *= (1 - p_i(alice_strat[c]))
            c -= 1
        
    #return this prefactor multiplied by the element case
    return prefactor * interval(alice_strat, bob_strat, p_i, play)


#gets the correct interval based on the strategies. The payoff matrix is split into intervals. 
#For example, with num_plays = 2, Alice's payoff matrix is (excluding prefactor)
# 1 if a0 < b0
# (1 - p_i(b0)) if b0 <= a0 < b0 + b1
# (1 - p_i(b0))(1-p_i(b1)) if a0 >= b0 + b1
def interval(arr1, arr2, p, play):  
    x = sum(arr1[:play])
    if x > K:
        return 0
    elif x < arr2[0]:
        return p_func(p, [])

    for i in range(len(arr2) - 1):
        if sum(arr2[:i+1]) <= x < sum(arr2[:i+2]):
            return p_func(p, arr2[0:i+1])

    return p_func(p, arr2)


#returns the correct element based on the interval function above
def p_func(p, arr):
    prod = 1

    for i in arr:
        prod *= (1 - p(i))

    return prod


# get the elements of the payoff matrix from col and row, without constructing everything
def get_cartesian_element(col, row):
    set_K = np.arange(1, K + 1)
    cart_prod = cartesian((set_K for x in range(num_plays)))
    return np.append(cart_prod[row], cart_prod[col])

def get_alice_payoff_element(col, row):
    cart = get_cartesian_element(col, row)
    strat_length = len(cart) // 2
    alice_strat = cart[:strat_length]
    bob_strat = cart[strat_length:]
    #print('Alice Strat: {}, Bob Strat: {}'.format(alice_strat, bob_strat))


    elem = 0
    for play in range(1, num_plays + 1):
        prefactor = p_i(alice_strat[play-1])
        if play > 1:
            c = play - 2
            while c >= 0:
                prefactor *= (1 - p_i(alice_strat[c]))
                c -= 1

        elem += prefactor * interval(alice_strat, bob_strat, p_i, play)

    return elem

def get_row(row):
    return [get_alice_payoff_element(x, row) for x in range(mat_dim)]

def get_col(col):
    return [get_alice_payoff_element(col, x) for x in range(mat_dim)]

def print_results(res, player):
    for i, value in enumerate(res):
        if abs(value) != 0.0:
            set_K = np.arange(1, K + 1)
            cart_prod = cartesian((set_K for x in range(num_plays)))
            strat = [intvl * x for x in cart_prod[i]]
            print('{} plays strategy {} with probability {}'.format(player, strat, value))


A = alice_payoff()
B = A.T

# for testing purpos
num_eq = 10

print('made game')
with open('output.txt' , 'w') as f:
    tableaus, basic_vars = lh.create_tableau(A, B)
    Crange = basic_vars
    sys.stdout = f

    for i in range(num_eq):
        eq = lh.Lemke_Howson(tableaus, basic_vars, Crange, init_pivot = random.randint(0, mat_dim))
        print('EQUILIBRIUM {}'.format(i))
        print_results(np.round(eq[0], 10), 'Alice')
        print_results(np.round(eq[1], 10), 'Bob')