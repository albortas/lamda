import numpy as np
from math import pi
from src.utils.transformations import xyz_rotation_matrix, new_coordinates, rotz
SEQ = [0, .5, .25, .75]
STEPL = .125
V_AMP = 40



def stance_controller(state, t1):
    alpha = np.zeros(4)
    alphav = np.zeros(4)
    stance = [True, True, True, True]
    for i in range (0,4):
        alphav[i] =0 
        if (t1<=SEQ[i]):
                stance[i] = True #Leg is on the ground (absolute position value unchanged)
        else:        
            if (t1<(SEQ[i]+STEPL)):
                    
                stance[i] = False #leg is lifted (absolute position value changes)
                alphav[i] = -pi/2+2*pi/STEPL*(t1-SEQ[i])
                t2 = SEQ[i]+STEPL
                if (state.step_phase == 'start'):
                    #End position alpha 
                    alpha[i] = -SEQ[i]/(1-STEPL)/2 + (t2-SEQ[i])/STEPL/(1-STEPL)*SEQ[i]  
                if (state.step_phase == 'stop'):                          
                    alpha[i] = -1/2 + SEQ[i]/(1-STEPL)/2 + (t2-SEQ[i])/STEPL*(1-SEQ[i]/(1-SEQ)) 
                if (state.step_phase == 'walk'):                                                 
                    alpha[i] = -1/2  + ((t2-SEQ[i])/STEPL) 
            else:         
                stance[i] = True #Leg is on the ground (absolute position value unchanged)
        state.stance = stance
        return alpha, alphav
                
def compensacion_theta(state,t1):
    kcomp = 1
    v_amp_t = V_AMP
    ts = 0.25
    if (state.step_phase == 'start'):
        if (t1< ts):
            kcomp = t1/ts
            v_amp_t = 0
    elif (state.step_phase == 'stop'):  
        if (t1 > (1-ts)):
            kcomp = (1- t1)/ts
            v_amp_t = 0
    return v_amp_t, kcomp

def calculate_compensation(state, t1):
    """Calcula la compensación para el centro de gravedad."""
    weight = 1.2
    
    x_abs_area = np.zeros(4)
    y_abs_area = np.zeros(4)
    
    secuencia = [
                ([1, 3], 2),
                ([0, 2], 3),
                ([1, 3], 0),
                ([0, 2], 1)
    ]
    
    for i, (idx, t_idx) in enumerate(secuencia):
        x_abs_area[i] = ((state.foot_stance[0][idx[0]] + state.foot_stance[0][idx[1]])*weight+ state.foot_stance[0][t_idx])/(2*weight+1) 
        y_abs_area[i] = ((state.foot_stance[1][idx[0]] + state.foot_stance[1][idx[1]])*weight+ state.foot_stance[1][t_idx])/(2*weight+1) 
    
    if sum(state.stance) == 4:
        istart, iend = 0, 0
        tstart = int(t1 / 0.25) * 0.25
        tend = tstart + 0.25
        if tend == 1:
            tend = 0
        for i in range(4):
            if tstart == SEQ[i]:
                istart = i
            if tend == SEQ[i]:
                iend = i
        if t1 > (SEQ[istart] + STEPL):
            x_abs_comp = x_abs_area[istart] + (x_abs_area[iend] - x_abs_area[istart]) * (t1 - tstart - STEPL) / (0.25 - STEPL)
            y_abs_comp = y_abs_area[istart] + (y_abs_area[iend] - y_abs_area[istart]) * (t1 - tstart - STEPL) / (0.25 - STEPL)
        else:
            x_abs_comp = x_abs_area[istart]
            y_abs_comp = y_abs_area[istart]
    else:
        for i in range(4):
            if not state.stance[i]:
                x_abs_comp = x_abs_area[i]
                y_abs_comp = y_abs_area[i]
                
    Msi_comp = rotz(-state.theta[2])
    comp = new_coordinates(Msi_comp,
                            x_abs_comp - state.foot_center[0],
                            y_abs_comp - state.foot_center[1], 0,)
    return comp
    