import numpy as np
import sympy as sp

def rotx(alpha):
    return np.array([[1, 0, 0],
                     [0, sp.cos(alpha), -sp.sin(alpha)],
                     [0, sp.sin(alpha), sp.cos(alpha)]])
    
def roty(beta):
    return np.array([[sp.cos(beta), 0, sp.sin(beta)],
                     [0, 1, 0],
                     [-sp.sin(beta), 0, sp.cos(beta)]])
    
def rotz(gamma):
    return np.array([[sp.cos(gamma), -sp.sin(gamma), 0],
                     [sp.sin(gamma), sp.cos(gamma), 0],
                     [0, 0, 1]])
    
def rotxyz(alpha, beta, gamma):
    return rotz(gamma) @ roty(beta) @ rotx(alpha)

def rotzyx(gamma, beta, alpha):
    return rotx(alpha) @ roty(beta) @ rotz(gamma)


    