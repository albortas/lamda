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
    x_hg = sp.Symbol('x_HCG')
    y_hg = sp.Symbol('y_HCG')
    z_hg = sp.Symbol('z_HCG')
    x_tg = sp.Symbol('x_TCG')
    y_tg = sp.Symbol('y_TCG')
    z_tg = sp.Symbol('z_TCG')
    x_fg = sp.Symbol('x_FCG')
    y_fg = sp.Symbol('y_FCG')
    z_fg = sp.Symbol('z_FCG')
    d = sp.Symbol('d')
    L0 = sp.Symbol('L_0')
    L1 = sp.Symbol('L_1')
    #q1 = sp.Symbol('theta[0]')
    #q2 = sp.Symbol('theta[1]')
    #q3 = sp.Symbol('theta[2]')
    q1 = sp.Symbol('%theta_1')
    q2 = sp.Symbol('%theta_2')
    q3 = sp.Symbol('%theta_3')
    A0_1 = MatrixA(HRotx(q1), HTrans(0, 0, -d))
    A1_2 = HTrans(0,L0,0)
    A0_2 = A0_1 @ A1_2
    A1 = MatrixA(HRotx(q1), HTrans(x_hg, y_hg, z_hg))
    A2 = MatrixA(HRoty(q2), HTrans(x_tg, y_tg, z_tg))
    T_2  = A0_2 @ A2
    A2_3 = MatrixA(HRoty(q2), HTrans(0, 0, -L1))
    A0_3 = A0_2 @ A2_3
    A3 = MatrixA(HRoty(-q3), HTrans(x_fg, y_fg, z_fg))
    T3 = A0_3 @ A3
    T3 = sp.simplify(T3[0,3])
    print(T3)
   