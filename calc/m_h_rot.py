import numpy as np
import sympy as sp

def HRotx(alpha):
    return np.array([[1, 0, 0, 0],
                     [0, sp.cos(alpha), -sp.sin(alpha), 0],
                     [0, sp.sin(alpha), sp.cos(alpha), 0],
                     [0, 0, 0, 1]])

def HRoty(phi):
    return np.array([[sp.cos(phi), 0, sp.sin(phi), 0],
                     [0, 1, 0, 0],
                     [-sp.sin(phi), 0, sp.cos(phi), 0],
                     [0, 0, 0, 1]])

def HRotz(psi):
    return np.array([[sp.cos(psi), -sp.sin(psi), 0, 0],
                     [sp.sin(psi), sp.cos(psi), 0, 0],
                     [0, 0, 1, 0],
                     [0, 0, 0, 1]])
    
def HTrans(x, y, z):
    return np.array([[1, 0, 0, x],
                     [0, 1, 0, y],
                     [0, 0, 1, z],
                     [0, 0, 0, 1]])
    
def MatrixA(rot, trans):
    return rot @ trans

if __name__ == "__main__":
    d = sp.Symbol('d')
    L0 = sp.Symbol('L0')
    L1 = sp.Symbol('L1')
    q1 = sp.Symbol('q1')
    q2 = sp.Symbol('q2')
    q3 = sp.Symbol('q3')
    A0_1 = MatrixA(HRotx(q1), HTrans(0, 0, -d))
    A1_2 = HTrans(0, L0, 0)
    A2_3 = MatrixA(HRoty(q2), HTrans(0, 0, -L1))
    A0_2 = A0_1 @ A1_2
    A0_3 = A0_2 @ A2_3
    print(A0_3)