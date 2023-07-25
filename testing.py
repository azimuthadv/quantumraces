import numpy as np
import lemkehowson as lh
import sys
from decimal import *

N = float(2**256) # number of possible hashes
D = float(1e30)
GIPS = 167906
intvl = 15

getcontext().prec = 100

def p_i(t):
    theta = float(np.arcsin(1 / (np.sqrt(D))))
    return Decimal((np.sin(2*((t * intvl * GIPS) + 0.5) * theta))**2)

alice_strats = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]
bob_strats = [[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3], [3, 1], [3, 2], [3, 3]]

print('A1:')
for i in range(len(alice_strats)):
    as1, as2 = alice_strats[i]
    bs1, bs2 = bob_strats[i]

    if as1 < bs1:
        print('CASE ONE')
    elif bs1 <= as1 < bs1 + bs2:
        print('CASE TWO')
    elif as1 >= bs1 + bs2:
        print('CASE THREE')
    else:
        print('NO CASE')

print('A2:')
for i in range(len(alice_strats)):
    as1, as2 = alice_strats[i]
    bs1, bs2 = bob_strats[i]

    if as1 + as2 < bs1:
        print('CASE ONE')
    elif bs1 <= as1 + as2 < bs1 + bs2:
        print('CASE TWO')
    elif as1 + as2 >= bs1 + bs2:
        print('CASE THREE')
    else:
        print('NO CASE')