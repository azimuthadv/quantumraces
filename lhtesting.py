#testing that the lemkehowson algorithm is working appropriately

import numpy as np
import lemkehowson as lh

# non degenerate case
print("NON DEGENERATE CASE")
A = np.array([[3, 3], [2, 5], [0, 6]])
B = np.array([[3, 2], [2, 6], [3, 1]])
for label, output in [
    (0, (np.array([1, 0, 0]), np.array([1, 0]))),
    (1, (np.array([0, 1 / 3, 2 / 3]), np.array([1 / 3, 2 / 3]))),
    (2, (np.array([1, 0, 0]), np.array([1, 0]))),
    (3, (np.array([1, 0, 0]), np.array([1, 0]))),
    (4, (np.array([0, 1 / 3, 2 / 3]), np.array([1 / 3, 2 / 3]))),
]:
    tableaus, basic_vars = lh.create_tableau(A, B)
    Crange = basic_vars
    for eq, expected_eq in zip(lh.Lemke_Howson(tableaus, basic_vars, Crange, init_pivot=label), output):
        print(all(np.isclose(eq, expected_eq)))

# degenerate case
print("DEGENERATE CASE")

A = np.array([[1, 3, 3], [3, 1, 3], [1, 3, 3]])
B = np.array([[3, 3, 1], [1, 1, 3], [3, 1, 3]])

for label in range(3):
    tableaus, basic_vars = lh.create_tableau(A, B)
    Crange = basic_vars
    print(tableaus)
    print(Crange)
    for eq, expected_eq in zip(
        lh.Lemke_Howson(tableaus, basic_vars, Crange, init_pivot = label),
        (np.array([0.5, 0.5, 0]), np.array([0, 0, 1])),
    ):
        print(all(np.isclose(eq, expected_eq)))



'''
A = np.array([[-1, -1, -1], [0, 0, 0], [-1, -1, -10000]])
B = np.array([[-1, -1, -1], [0, 0, 0], [-1, -1, -10000]])

for label in range(3):
    tableaus, basic_vars = lh.create_tableau(A, B)
    Crange = basic_vars
    for eq, expected_eq in zip(
        lh.Lemke_Howson(tableaus, basic_vars, Crange, init_pivot = label), 
        (np.array([0, 1, 0]), np.array([1, 0, 0])), 
    ):
        print(all(np.isclose(eq, expected_eq)))
'''