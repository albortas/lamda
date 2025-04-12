import numpy as np
from math import pi, sin, cos, sqrt, atan2

from src.utils.transformations import rotz, new_coordinates

# Constantes
tstep = 0.01
stepl = 0.125

STEERING_THRESHOLD = 2000
MIN_STEERING = 0.001
GAP_THRESHOLD = 0.01
DEADZONE = 0.2
COEF = 1.2
H_AMP = 100

class UpdateMovement:
    def __init__(self, default_stance):
        self.default_stance = default_stance
        self.module = 0
        self.steering = 200
        self.walking_direction = 0
        self.walking_speed = 0
        self.cw = 1
        self.step_phase = ""
        
    def update_joystick(self, state, command):
        # Determinar si hay movimiento
        if (abs(command.velocity[0]) > DEADZONE or abs(command.velocity[1]) > DEADZONE or command.stop):
            self.active_joystick(state, command)
        if (abs(command.velocity[0]) < DEADZONE and abs(command.velocity[1]) < DEADZONE and not command.stop):
            self.deactive_joystick(state, command)
        self.update_phase(state, command)
    
    def update_movement(self, state, command):
        #if command.walking:
        self.update_joystick(state, command)
        state.steering = self.steering
        state.walking_direction = self.walking_direction
        state.walking_speed = self.walking_speed
        state.foot_center = self.nominal_abs_foot(state)
        state.center = self.center(state)
    
    def active_joystick(self, state, command):
        command.trec = int(state.t) + 1
        # Guardar valores antiguos
        old_values = {
            'module': self.module,
            'walking_direction': state.walking_direction,
            'steering': state.steering,
            'x': self.module * cos(state.walking_direction),
            'y': self.module * sin(state.walking_direction)
        }
        
        # Actualizar módulo y dirección
        self.module = sqrt(command.velocity[0]**2 + command.velocity[1]**2)
        self.walking_direction = (atan2(-command.velocity[1], -command.velocity[0]) % (2*pi) + pi/2) % (2*pi)
        
        # Calcular nuevas coordenadas
        x_new = self.module * cos(self.walking_direction)
        y_new = self.module * sin(self.walking_direction)
        
        # Actualizar dirección (steering)
        if abs(command.yaw_rate) < DEADZONE:
            self.cw = 1
            self.steering = 1e6 if self.steering >= STEERING_THRESHOLD else min(1e6, self.steering * COEF)
        else:
            self.steering = STEERING_THRESHOLD - (abs(command.yaw_rate) - DEADZONE) * STEERING_THRESHOLD / 0.8 + MIN_STEERING
            self.steering = self.apply_steering_limits(self.steering, old_values['steering'], COEF, MIN_STEERING)
            self.cw = -np.sign(command.yaw_rate)
        
        # Limitar cambio brusco de dirección
        gap = sqrt((x_new - old_values['x'])**2 + (y_new - old_values['y'])**2)
        if gap > GAP_THRESHOLD:
            x_new = old_values['x'] + (x_new - old_values['x']) / gap * GAP_THRESHOLD
            y_new = old_values['y'] + (y_new - old_values['y']) / gap * GAP_THRESHOLD
            self.module = sqrt(x_new**2 + y_new**2)
            self.walking_direction = atan2(y_new, x_new)
        
        # Calcular velocidad de caminata
        min_h_amp = H_AMP * (self.steering / (2e6) + 0.5)
        xa = 1 + cos(self.walking_direction - pi/2)
        self.walking_speed = min(1, self.module) * min(H_AMP, min_h_amp) * (0.125 * xa**2 + 0.125 * xa + 0.25)
        
        
    def apply_steering_limits(self, new_steering, old_steering, coef, min_steering):
        ratio = new_steering / old_steering
        if ratio > coef:
            new_steering = old_steering * coef
        elif 1/ratio > coef:
            new_steering = old_steering / coef
            if new_steering < min_steering:
                new_steering = min_steering
        return new_steering
            
    def deactive_joystick(self, state, command):
        # Movimiento inactivo - desacelerar
        self.module = max(0, self.module - 0.01)
        self.walking_speed = self.module * H_AMP * ((1 + cos(self.walking_direction - pi/2)) / 2 * 0.75 + 0.25)
        self.steering = 1e6 if self.steering >= STEERING_THRESHOLD else min(1e6, self.steering * COEF)
        self.cw = 1
        if state.t > command.trec:
            state.t = command.trec
            
    def update_phase(self, state, command):
        # Paso de fase
        if state.t < command.tstart:
            self.step_phase = "start"
        else:
            if state.t < command.tstop:
                self.step_phase = "walk"
            else:
                self.step_phase = "stop"
                
        # Actualiza estados
        if state.t > command.tstop + 1 - 0.01:
            command.stop = False
            command.walking = False
            command.free = True
            
    @property
    def coor_circle(self):
        xc = self.steering * np.cos(self.walking_direction)
        yc = self.steering * np.sin(self.walking_direction)
        return xc, yc
    @property
    def foot_position(self):
        return self.default_stance[0], self.default_stance[1]
    
    @property
    def nominal_radius_angle(self):
        radii = np.sqrt((self.coor_circle[0]-self.foot_position[0])**2 + (self.coor_circle[1]-self.foot_position[1])**2)
        an = np.atan2(self.foot_position[1] - self.coor_circle[1], self.foot_position[0] - self.coor_circle[0])
        return radii, an
    
    @property
    def mangle(self):
        maxr = max(self.nominal_radius_angle[0])
        return self.walking_speed/maxr
    
    @property
    def dtheta(self):
        if (self.step_phase =='start')|(self.step_phase == 'stop'):           
            dtheta = self.mangle/(1-stepl)*tstep/2* self.cw
        else:
            dtheta = self.mangle/(1-stepl)*tstep* self.cw
        return dtheta
    
    def nominal_abs_foot(self, state):
        """ Posición absoluta del centro nominal del pie """
        xc, yc = self.coor_circle
        Ms = rotz(state.theta[2])
        s = new_coordinates(Ms,xc,yc,0, state.foot_center[0], state.foot_center[1], state.foot_center[2])
        dMs = rotz(self.dtheta)
        foot_center = new_coordinates(dMs, state.foot_center[0] - s[0], state.foot_center[1] - s[1], 0,
                                      s[0], s[1], 0)
        state.theta[2] += self.dtheta
        return foot_center
    
    def center(self, state):
        xc, yc = self.coor_circle
        center_x = state.foot_center[0]+(xc*cos(state.theta[2])-yc*sin(state.theta[2])) #absolute center x position
        center_y = state.foot_center[1]+(xc*sin(state.theta[2])+yc*cos(state.theta[2])) #absolute center y position
        center = np.array([center_x, center_y])
        return center
        
        
            
        
        
        
            
            
            
        
    