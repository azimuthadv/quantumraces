import numpy as np
import lemkehowson as lh
import sys
from decimal import *


# ===== CONSTANTS =====
N = float(2**256) # number of possible hashes
D = float(1e10) #network difficulty
num_plays = 2 # number of times each player can run Grover's algorithm

K = 20 #number of pure strategies
#max_K = 20148780 #maximum possible number of iterations per round
max_K = np.floor(np.pi / 4 * np.sqrt(D)) / 5
intvl = max_K // K #shorten the strategy space by checking intervalss
gamma = Decimal(0.50) # the probability that alice wins in a fork
mat_dim = (K+1)**num_plays #dimension of payoff matrix

getcontext().prec = 10

# =====================

original_stdout = sys.stdout

#Calculates the probability of Grover's algorithm finding the marked item after time t.


def p_i(t):
    theta = float(np.arcsin(1 / (np.sqrt(D))))
    return Decimal((np.sin(2*((t * intvl) + 0.5) * theta))**2)

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

def get_payoff(bob = False):
    # first get all of the permutations from the cartesian product to index the matrix
    set_K = np.arange(0, K + 1)
    arrs = (set_K for i in range(num_plays))
    S = cartesian(arrs)

    #dimension of the payoff matrix
    dim = int(len(set_K)**num_plays)
    #initialize the payoff matrices. There will be a separate one for each play. A[0] will be the total
    A = [np.zeros((mat_dim, mat_dim), dtype=Decimal) for i in range(num_plays + 1)]
    
    #populate each array
    for play in range(1, num_plays + 1):
        for col in range(mat_dim):
            for row in range(mat_dim):
                element = get_element(S, col, row, play, mat_dim, bob)
                A[play][col][row] = element
                A[0][col][row] = A[0][col][row] + A[play][col][row]

    return A[0]


def get_element(S, col, row, play, dim, bob = False):
    row_strats, col_strats = S, S
    cart = [*row_strats[col], *col_strats[row]]
    strat_length = len(cart) // 2
    alice_strat = cart[:strat_length]
    bob_strat = cart[strat_length:]
    #print('Alice Strat: {}, Bob Strat: {}'.format(alice_strat, bob_strat))
    assert play <= strat_length, 'Only {} plays are allowed in this game, got {}'.format(strat_length, play)
    
    #first calculate the prefactor for the matrix

    if not bob:
        prefactor = p_i(alice_strat[play-1])
        if play > 1:
            c = play - 2
            while c >= 0:
                prefactor *= Decimal((1 - p_i(alice_strat[c])))
                c -= 1
    else:
        prefactor = p_i(bob_strat[play-1])
        if play > 1:
            c = play - 2
            while c >= 0:
                prefactor *= (1 - p_i(bob_strat[c]))
                c -= 1

    element = Decimal(prefactor * interval(alice_strat, bob_strat, p_i, play, prefactor, bob))
        
    #return this prefactor multiplied by the element case
    return element



#gets the correct interval based on the strategies. The payoff matrix is split into intervals. 
#For example, with num_plays = 2, Alice's payoff matrix is (excluding prefactor)
# 1 if a0 < b0
# (1 - p_i(b0)) if b0 <= a0 < b0 + b1
# (1 - p_i(b0))(1-p_i(b1)) if a0 >= b0 + b1
def interval(arr1, arr2, p, play, prefactor, bob = False):
    if not bob:  
        x = sum(arr1[:play])
        if x > K:
            return 0
        elif x < arr2[0]:
            return p_func(p, []) + gamma/prefactor * (p_i(arr1[play-1])**2)

        for i in range(len(arr2) - 1):
            if sum(arr2[:i+1]) < x < sum(arr2[:i+2]):
                return p_func(p, arr2[0:i+1]) + gamma/prefactor *  (p_i(x - sum(arr2[:i+1])))**2
            elif x == sum(arr2[:i+1]):
                return p_func(p, arr2[0:i+2]) + gamma/prefactor * p_i(arr1[play-1]) * p_i(arr2[i])

        return p_func(p, arr2) 
    else:
        x = sum(arr2[:play])
        if x > K:
            return 0
        elif x < arr1[0]:
            return p_func(p, []) + (1 - gamma/prefactor) * (p_i(arr2[play-1])**2)

        for i in range(len(arr1) - 1):
            if sum(arr1[:i+1]) < x < sum(arr1[:i+2]):
                return p_func(p, arr1[0:i+1]) + (1 - gamma)/prefactor *  (p_i(x - sum(arr1[:i+1])))**2
            elif x == sum(arr1[:i+1]):
                return p_func(p, arr1[0:i+2]) + (1 - gamma)/prefactor * p_i(arr2[play-1]) * p_i(arr1[i])

        return p_func(p, arr1) 


#returns the correct element based on the interval function above
def p_func(p, arr):
    prod = 1

    for i in arr:
        prod *= Decimal((1 - p(i)))

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
            print('{} {} {}'.format(player, strat, value))



def get_eq(A, B):
    tableaus, basic_vars = lh.create_tableau(A, B)
    Crange = basic_vars
    nash_eqs = []
    with open('output.txt', 'w') as f:
        sys.stdout = f

        for i in range(mat_dim):
            eq = lh.Lemke_Howson(tableaus, basic_vars, Crange, init_pivot=i)

            if len(nash_eqs) == 3:
                break

            if not (
                any((np.allclose(eq[0], item[0]) and np.allclose(eq[1], item[1]) for item in nash_eqs))
            ):
                nash_eqs.append(eq)
                print_results(np.round(eq[0], 20), 'Alice')
                print_results(np.round(eq[1], 20), 'Bob')
                print('-----')

    return 

def main():
    A = get_payoff()
    B = get_payoff(bob = True)
    print('payoff matrix made')
    get_eq(A, B)
    sys.stdout = original_stdout

if __name__ == "__main__":
    main()  