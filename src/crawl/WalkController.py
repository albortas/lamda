import numpy as np

from src.motion.GaitController import GaitController
from src.motion.UpdateMovement import UpdateMovement

class WalkGaitController(GaitController):       
    def __init__(self, stance_time, swing_time, time_step, default_stance):
        contact_phases = np.array([ [0, 1, 1, 1, 1, 1, 1, 1],  # 0: Balanceo Pierna
                                    [1, 1, 1, 1, 0, 1, 1, 1],  # 1: Movimiento de postura adelante
                                    [1, 1, 0, 1, 1, 1, 1, 1],
                                    [1, 1, 1, 1, 1, 1, 0, 1]])
        super().__init__(stance_time, swing_time, time_step, contact_phases)
        self.default_stance = default_stance
        self.updateMovement = UpdateMovement(default_stance)
        
    def updateStateCommand(self, msg, state, command):
        command.velocity = [msg.axes[1], msg.axes[0]]
        command.yaw_rate = msg.axes[3]
        command.yaw_inv = msg.axes[2]
        
    def step(self, ticks):
        pass
    
    def run(self, state, command):
        # Actualizar tiempo
        state.t += 0.01
        self.updateMovement.update_movement(state, command)
        
        
        
    
    
    
   
class WalkSwingController:
    def __init__(self):
        pass
    
    def touchdown_location(self):
        pass
    
    def swing_height(self):
        pass
    
    def next_foot_location(self):
        pass
    
class WalkStanceController:
    def __init__(self):
        pass
    
    def position_delta(self):
        pass
    
    def next_foot_location(self):
        pass
    
