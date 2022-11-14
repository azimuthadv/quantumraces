import numpy as np
from decimal import *
getcontext().prec = 100


# lexicographic ratio test from https://github.com/shizejin/theory16HW
def approx_equal(x, y, epsilon):
    if Decimal(y) -epsilon < Decimal(x) < Decimal(y) +epsilon:
        return True
    return False


def min_set(v):
    
    idx = []
    small = np.inf
    epsilon = Decimal(10e-60)
    #60 for D = 10e30
    
    for i in range(len(v)):
        if v[i] < 0:
            #print('case one')
            continue
        if approx_equal(v[i], small, epsilon):
            #print('case two')
            idx.append(i)
        elif v[i] < small:
            #print('case three')
            small = v[i]
            idx = [i]
    
    return idx


def lexico_ratio(tableau, pivot, Crange): 
    #get the pivot column of the tableau. Create a new list that stores whether or not the elements of that column are <= 0.
    ind_nonpositive = tableau[:, pivot] <= 0
    #get the columns of the basic variables and store them into C
    C = tableau[:, Crange]
    with np.errstate(divide='ignore'): #ignore divide by 0
        #divide the last column by the pivot column, store into C0
        C0 = tableau[:, -1] / tableau[:, pivot]
        #if one of the pivot column elements were non positive, set that same element in C0 to inf
        C0[ind_nonpositive] = np.inf
        #find the minimum element index of C0. Since each element cooresponds to a row, we find the minimum row for this column.
        row_min = min_set(C0)
    #if there is only one minimum row, return it. 
    if len(row_min) == 1:
        return row_min[0]

    #solve tie by choosing a random element arbitrarily. 
    #return random.choice(row_min)

    
    #If there are multiple minimum rows, start looping through the total number of labels present in the other tableau
    #tie breaking rule
    #loop through the min rows that are at a tie, compare each element from left to right, pick smallest
    #think of this as ordering alphabetically, when both words start with same letter. 
    for i in range(C.shape[1]):
        with np.errstate(divide = 'ignore'):
            #Ci is the ith column of C, divided by the pivot column of tableau, at row min indices
            Ci = (C[:, i] / tableau[:, pivot])[row_min]
        #if one of the pivot column elements were non positive, set that same element in C0 to inf
        
        for i in range(len(Ci)):
            elem = ind_nonpositive[i]
            if elem:
                Ci[i] = np.inf
       
        
        row_min = min_set(Ci)
        if len(row_min) == 1:
            return row_min[0]
    
    print("lexico minimum ratio is not found!")

def pivoting(tableau, basic_vars, pivot, Crange):
    
    row_min = lexico_ratio(tableau, pivot, Crange)
    with np.errstate(divide = 'ignore'):
        tableau[row_min, :] /= tableau[row_min, pivot]
    for i in range(tableau.shape[0]):
        if i != row_min:
            if row_min is None:
                print("NO ROW MIN")
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