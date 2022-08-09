import numpy as np
import random

class Player:
    def __init__(self, max_t):
        self.max_t = max_t

    def measure(self, k, n, m):
        theta = np.arcsin(1 / (np.sqrt(2**n / m)))
        p = (np.sin(2 * (k + 0.5) * theta))**2
        r = random.uniform(0, 1)
        return [p > r, p]

    def make_measure(self, t, n, m, GIPS, early = False):
        if not early:
            if t == self.max_t or t % self.max_t  == 0:
                return(self.measure(self.max_t * GIPS, n, m))
        else:
            return(self.measure(t * GIPS, n, m))

    def get_max_t(self):
        return self.max_t

    def __repr__(self):
        return str(self.max_t)

    def __str__(self):
        return 'test'
