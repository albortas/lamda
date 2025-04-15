import numpy as np
from math import pi, sin, cos

from src.utils.transformations import xyz_rotation_matrix, new_coordinates, new_coordinates_vec, rotz


# Constantes
SEQ = [0, .5, .25, .75]
STEPL = 0.125
TSTEP = 0.01
V_AMP = 40


class CrawlController:
    def __init__(self, x_offset, default_height, CG, default_stance, default_frame):
        self.default_frame = default_frame
        self.default_stance = default_stance
        self.stance = [True,True,True,True]
        self.CG = CG
        self.x_offset = x_offset
        self.b_height = default_height
        self.framecorner = np.zeros(3)
        
    def calcule_body_center(self, state):
        # Calculando body_center
        xc, yc = self.steering_center(state)
        dtheta = self.dtheta(state)
        state.theta[2] += dtheta
        
        Ms = rotz(state.theta[2])
        s = new_coordinates(Ms,xc,yc,0,
                            state.body_center[0], state.body_center[1], state.body_center[2])
        dMs = rotz(dtheta)
        state.body_center = new_coordinates(dMs,
                                            state.body_center[0] - s[0],
                                            state.body_center[1] - s[1], 0,
                                            s[0], s[1], 0)
        
    def calcule_framecenter_comp(self, state):
        """Calculo de Compensacion"""
        kcomp = self.compensation_theta(state)[0]
        comp = self.calculate_compensation(state)
        
        Ms_comp = rotz(state.theta[2])
        compt = new_coordinates(Ms_comp,
                                (comp[0] - self.CG[0]) * kcomp + self.x_offset,
                                (comp[1] - self.CG[1]) * kcomp, 0)
        
        state.framecenter_comp = [state.body_center[0] + compt[0],
                                  state.body_center[1] + compt[1],
                                  self.b_height]
        

    def start_walk_stop (self, state):
        
        self.calcule_body_center(state)
        self.calcule_framecenter_comp(state)
        # Actulizando stance
        self.stance = self.update_stance(state)
        
        # Calculo de framecorner
        Msi_comp = rotz(-state.theta[2])
        Ms_updated = xyz_rotation_matrix(state.theta[3], state.theta[4], state.theta[5] + state.theta[2])
        Msi_updated = xyz_rotation_matrix(-state.theta[3], -state.theta[4], -state.theta[5] - state.theta[2], True)
        self.framecorner = new_coordinates_vec(Ms_updated,
                                               self.default_frame[0], self.default_frame[1], self.default_frame[2],
                                               state.framecenter_comp[0], state.framecenter_comp[1], state.framecenter_comp[2])
        xc, yc = self.steering_center(state)
        alpha = self.alpha(state)
        alphav = self.alphav(state)
        radii, an = self.radii_angles(state)
        mangle = self.mangle(state)
        comp = self.calculate_compensation(state)
        kcomp, v_amp_t = self.compensation_theta(state)
        
        xleg = np.zeros(4)
        yleg = np.zeros(4)
        zleg = np.zeros(4)
        xabs = np.zeros(4)
        yabs = np.zeros(4)
        zabs = np.zeros(4)
        xint = np.zeros(4)
        yint = np.zeros(4)
        zint = np.zeros(4)
         
        for i in range (0,4):              
            if self.stance[i] == False:
                #relative position calculation (used for inverse kinematics)
                alphah = an[i]+mangle*alpha[i]*state.cw
                xleg_target = xc + radii[i]*cos(alphah) -(comp[0]- self.CG[0])*kcomp - self.x_offset - self.default_frame[0,i]
                yleg_target = yc + radii[i]*sin(alphah) -(comp[1]- self.CG[1])*kcomp - self.default_frame[1,i]
                
                leg_current = new_coordinates(Msi_comp,
                                              state.foot_abs[0,i]- self.framecorner[0,i],
                                              state.foot_abs[1,i]- self.framecorner[1,i],
                                              - self.framecorner[2,i])
                #interpolate between current position and targe
                if ((SEQ[i] + STEPL - state.t1)> TSTEP):
                    xint[i] = leg_current[0]+(xleg_target - leg_current[0])*(TSTEP)/(SEQ[i]+STEPL-state.t1)
                    yint[i] = leg_current[1]+(yleg_target - leg_current[1])*(TSTEP)/(SEQ[i]+STEPL-state.t1)
                else:
                    xint[i] = xleg_target 
                    yint[i] = yleg_target   
                zint[i] = leg_current[2] + v_amp_t*(1+sin(alphav[i]))/2                 
                #print (leg_current[2],zint[i],leg_current[2]-zint[i])
                Msi_body = xyz_rotation_matrix (-state.theta[3],-state.theta[4],-state.theta[5],True) 
                legs = new_coordinates(Msi_body,xint[i],yint[i],zint[i])
                xleg[i]= legs[0]
                yleg[i]= legs[1]
                zleg[i]= legs[2]
                
                #absolute foot position 
                #Msb_updated = Spot.xyz_rotation_matrix (self,0,0,theta_spot_updated[2]+theta_spot_updated[5],False)
                foot_abs = new_coordinates(Ms_updated,xleg[i],yleg[i],zleg[i],self.framecorner[0,i],self.framecorner[1,i],self.framecorner[2,i])
                

                xabs[i] = foot_abs[0]
                yabs[i] = foot_abs[1]
                zabs[i] = foot_abs[2]
                        
            else:
                xabs[i] = state.foot_abs[0, i]
                yabs[i] = state.foot_abs[1, i]
                zabs[i] = 0
                
                #relative foot position of foot on the ground/floor for inverse kinematics
                leg = new_coordinates(Msi_updated,xabs[i]- self.framecorner[0,i],yabs[i]- self.framecorner[1,i],zabs[i]- self.framecorner[2,i])
                xleg[i] = leg[0]
                yleg[i] = leg[1]
                zleg[i] = leg[2]
                
        state.foot_position = np.array([xleg, yleg, zleg])
        state.foot_abs = np.array([xabs, yabs, zabs])
               
    
    def steering_center(self, state):
        """Coordenadas del centro de dirección en el marco puntual"""
        xc = state.steering * cos(state.walking_direction)
        yc = state.steering * sin(state.walking_direction)
        return xc, yc
    
    def radii_angles(self, state):
        """Calcula la direccion del radio y angulo"""
        xc, yc = self.steering_center(state)
        radii = np.sqrt((xc - self.foot_position[0])**2 + (yc - self.foot_position[1])**2)
        an = np.atan2(self.foot_position[1] - yc, self.foot_position[0] - xc)
        return radii, an
    
    def mangle(self, state):
        """Ángulo de movimiento"""
        radii, an = self.radii_angles(state)
        maxr = max(radii)
        return state.walking_speed/maxr
    
    def dtheta(self, state):
        """Cálculo del ángulo de rotación y traslación"""
        mangle = self.mangle(state)
        if (state.step_phase =='start')|(state.step_phase == 'stop'):           
            dtheta = mangle/(1-STEPL)*TSTEP/2*state.cw
        else:
            dtheta = mangle/(1-STEPL)*TSTEP*state.cw
        return dtheta
    
    
    def update_stance(self, state):
        for i in range(4):
            if state.t1 <= SEQ[i]:
                self.stance[i] = True #Leg is on the ground (absolute position value unchanged)
            else:
                if state.t1 <= SEQ[i] + STEPL:
                    self.stance[i] = False #leg is lifted (absolute position value changes)
                else:
                    self.stance[i] = True #Leg is on the ground (absolute position value unchanged)
        return self.stance
    
    
    def alpha(self, state):
        alpha = np.zeros(4)
        for i in range(4):
            if (state.t1<(SEQ[i] + STEPL)):
                t2 = SEQ[i] + STEPL
                if (state.step_phase == 'start'):
                    #End position alpha 
                    alpha[i] = -SEQ[i]/(1-STEPL)/2 + (t2- SEQ[i])/STEPL/(1-STEPL)* SEQ[i]  
                if (state.step_phase == 'stop'):                          
                    alpha[i] = -1/2 + SEQ[i]/(1-STEPL)/2 + (t2- SEQ[i])/STEPL*(1- SEQ[i]/(1-STEPL)) 
                if (state.step_phase == 'walk'):                                                 
                    alpha[i] = -1/2  + ((t2- SEQ[i])/STEPL)
        return alpha
        
        
    def alphav(self, state):
        alphav = np.zeros(4)
        for i in range (4):
            if (state.t1<(SEQ[i] + STEPL)):
                alphav[i] = -pi/2 + 2*pi/STEPL*(state.t1 - SEQ[i])
            return alphav
    
    def compensation_theta(self, state):
        """Cálculo de compensación con theta"""
        kcomp = 1
        v_amp_t = V_AMP
        ts = 0.25
        if (state.step_phase == 'start'):
            if (state.t1< ts):
                kcomp = state.t1/ts
                v_amp_t = 0
        elif (state.step_phase == 'stop'):  
            if (state.t1 > (1-ts)):
                kcomp = (1-state.t1)/ts
                v_amp_t = 0
        return kcomp, v_amp_t
    
    def calculate_compensation(self, state):
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
            x_abs_area[i] = ((state.foot_abs[0][idx[0]] + state.foot_abs[0][idx[1]])*weight+ state.foot_abs[0][t_idx])/(2*weight+1) 
            y_abs_area[i] = ((state.foot_abs[1][idx[0]] + state.foot_abs[1][idx[1]])*weight+ state.foot_abs[1][t_idx])/(2*weight+1) 
        
        if sum(self.stance) == 4:
            istart, iend = 0, 0
            tstart = int(state.t1 / 0.25) * 0.25
            tend = tstart + 0.25
            if tend == 1:
                tend = 0
            for i in range(4):
                if tstart == SEQ[i]:
                    istart = i
                if tend == SEQ[i]:
                    iend = i
            if state.t1 > (SEQ[istart] + STEPL):
                x_abs_comp = x_abs_area[istart] + (x_abs_area[iend] - x_abs_area[istart]) * (state.t1 - tstart - STEPL) / (0.25 - STEPL)
                y_abs_comp = y_abs_area[istart] + (y_abs_area[iend] - y_abs_area[istart]) * (state.t1 - tstart - STEPL) / (0.25 - STEPL)
            else:
                x_abs_comp = x_abs_area[istart]
                y_abs_comp = y_abs_area[istart]
        else:
            for i in range(4):
                if not self.stance[i]:
                    x_abs_comp = x_abs_area[i]
                    y_abs_comp = y_abs_area[i]
                    
        Msi_comp = rotz(-state.theta[2])
        comp = new_coordinates(Msi_comp,
                                x_abs_comp - state.body_center[0],
                                y_abs_comp - state.body_center[1], 0)
        return comp
    
    @property
    def foot_position(self):
        """Posición nominal del pie"""
        return self.default_stance[0], self.default_stance[1]
    