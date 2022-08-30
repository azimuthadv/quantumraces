# lexicographic pivoting degenerate games from https://github.com/shizejin/theory16HW

import numpy as np

def approx_equal(x, y, epsilon):
    if y-epsilon < x < y+epsilon:
        return True
    return False

def min_set(v):
    
    idx = []
    small = np.inf
    epsilon = 10e-15
    
    for i in range(len(v)):
        if v[i] < 0:
            continue
        if approx_equal(v[i], small, epsilon):
            idx.append(i)
        elif v[i] < small:
            small = v[i]
            idx = [i]
    
    return idx

def lexico_ratio(tableau, pivot, Crange):  
    ind_nonpositive = tableau[:, pivot] <= 0
    #print('ind_nonpositive: {}'.format(ind_nonpositive))
    C = tableau[:, Crange]
    with np.errstate(divide='ignore'):
        C0 = tableau[:, -1] / tableau[:, pivot]
        C0[ind_nonpositive] = np.inf
        row_min = min_set(C0)
    if len(row_min) == 1:
        return row_min[0] 
    
    for i in range(C.shape[1]):
        Ci = (C[:, i] / tableau[:, pivot])[row_min]
        #print('Ci {}'.format(Ci))
        Ci[ind_nonpositive] = np.inf
        row_min = min_set(Ci)
        if len(row_min) == 1:
            return row_min[0]
    
    print("lexico minimum ratio is not found!")

def pivoting(tableau, basic_vars, pivot, Crange):
    
    row_min = lexico_ratio(tableau, pivot, Crange)
    tableau[row_min, :] /= tableau[row_min, pivot]
    for i in range(tableau.shape[0]):
        if i != row_min:
            tableau[i, :] -= tableau[i, pivot] * tableau[row_min, :]
    basic_vars[row_min], pivot = pivot, basic_vars[row_min]
    return pivot

def create_tableau(A, B):
    B_T = B.T
    m, n = A.shape
    tableaus = []
    for i in range(2):
        tableaus.append(np.empty((A.shape[1-i], m+n+1)))
        tableaus[i][:, :m] = [B_T, np.identity(m)][i]
        tableaus[i][:, m:m+n] = [np.identity(n), A][i]
        tableaus[i][:, -1] = 1
    basic_vars_list = [np.arange(m, m+n), np.arange(m)]
    return tableaus, basic_vars_list

def Lemke_Howson(tableaus, basic_vars_list, Crange, init_pivot, return_tableau = False):
    
    m, n = tableaus[1].shape[0], tableaus[0].shape[0]
    pivot = init_pivot
    init_player = int((basic_vars_list[0]==init_pivot).any())
    players = [init_player, 1 - init_player]
    
    while True:
        for i in players:
            pivot = pivoting(tableaus[i], basic_vars_list[i], pivot, Crange[i])
            if pivot == init_pivot:
                break
        else:
            continue
        break
        
    #summarize the found NE
    normalized = np.empty(m+n)
    out = np.zeros(m+n)
    for i, (start, num) in enumerate(zip([0, m], [m, n])):
        ind = basic_vars_list[i] < start + num if i == 0 else start <= basic_vars_list[i]
        out[basic_vars_list[i][ind]] = tableaus[i][ind, -1]
        s = out[start:start+num].sum()
        if s != 0:
            for j in range(start,start+num):
                normalized[j] = out[j] / s
        else:
            normalized[start:start+num] = np.zeros(num)
    actions = normalized[:m], normalized[m:]

    if return_tableau:
        return actions, tableaus, basic_vars_list
    
    return actions


