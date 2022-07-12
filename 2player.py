import numpy as np

# ===== CONSTANTS =====
N = float(2**256) # number of possible hashes
M = float(2**256 / 1e2) #number of solutions
#K = int(np.ceil(np.pi / 4 * np.sqrt(N) - 3/2)) # number of strategies (number of times to measure)
K = 2
GIPS = 224 # number of grover iterations per second that the quantum computers are capable of
num_plays = 2 # number of times each player can run Grover's algorithm
# =====================

#Calculates the probability of Grover's algorithm finding the marked item after time t.
def p_i(t):
    theta = float(np.arcsin(1 / (np.sqrt(N / M))))
    return (np.sin(2*((t * GIPS) + 0.5) * theta))**2

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
    A = [np.empty((dim, dim), dtype=float) for i in range(num_plays + 1)]

    #populate each array
    for play in range(1, num_plays + 1):
        for col in range(dim):
            for row in range(dim):
                A[play][col][row] = get_element(S, col, row, play, dim)
                A[0][col][row] += A[play][col][row]

    return A[0]


def get_element(S, col, row, play, dim):
    cart = S[col * dim + row]
    strat_length = len(cart) // 2
    alice_strat = cart[strat_length:]
    bob_strat = cart[:strat_length]
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
    if x < arr2[0]:
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

print(alice_payoff())
