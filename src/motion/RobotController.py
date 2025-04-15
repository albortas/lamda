import numpy as np

from src.motion.StateCommand import State, Command
from src.motion.WalkController import WalkGaitController

class RobotController:
    def __init__(self, body, legs):
        self.body = body
        self.legs = legs
        self.frame_x = self.body['Lb'] * 0.5
        self.frame_y = self.body['Wb'] * 0.5
        self.delta_x = self.frame_x
        self.delta_y = self.frame_y + self.legs['L0']
        self.default_height = 200
        self.x_offset = 0
        self.x_shift_from = -5
        self.x_shift_back = -5
        self.walkGaitController = WalkGaitController(self.x_offset, self.default_height, self.legs, self.default_stance, self.default_frame)
        self.currentController = self.walkGaitController
        self.state = State(self.default_stance, self.default_position, self.default_framecenter_comp)
        self.command = Command()
    
    def joystick_command(self, msg):
        if msg.buttons[0] == 0 and msg.buttons[1] == 0 and self.command.lock:
            self.command.lock = False
        
        # Inicia la caminata
        if msg.buttons[0] == 1 and not self.command.walking and self.command.free:
            print("Modo Crawl On")
            self.command.walking = True
            self.command.lock = True
            self.command.stop = False
            self.command.free = False
            self.state.t = 0
            self.command.tstart = 1
            self.command.tstop = 1000
            self.command.trec = int(self.state.t)
        
        # Finaliza la camminata
        if msg.buttons[0] == 1 and self.command.walking and not self.command.stop and not self.command.lock:
            print("Modo Crawl Off")
            self.command.stop = True
            self.command.lock = True
            if abs(self.state.t - int(self.state.t)) <= 0.01:
                self.command.tstop = int(self.state.t)
            else:
                self.command.tstop = int(self.state.t) + 1
                
            if self.state.t == 0:
                self.command.tstop = 1
            
        
        self.currentController.updateStateCommand(msg, self.state, self.command)
            
    def run(self):
        return self.currentController.run(self.state, self.command)
    
    @property
    def default_stance(self):
        #LF, RF, RR, LR
        return np.array([[self.delta_x + self.x_shift_from, self.delta_x + self.x_shift_from, -self.delta_x + self.x_shift_back, -self.delta_x + self.x_shift_back],
                         [self.delta_y, -self.delta_y, -self.delta_y, self.delta_y],
                         [0, 0, 0, 0]])
    @property
    def default_frame(self):
        #LF, RF, RR, LR
        return np.array([[self.frame_x,  self.frame_x, -self.frame_x, -self.frame_x],
                         [self.frame_y, -self.frame_y, -self.frame_y,  self.frame_y],
                         [           0,             0,             0,             0]])
        
    @property
    def default_position(self):
        return np.array([[      -self.x_offset,       -self.x_offset,       -self.x_offset,      -self.x_offset],
                         [     self.legs['L0'],      -self.legs['L0'],      -self.legs['L0'],     self.legs['L0']],
                         [-self.default_height, -self.default_height, -self.default_height, -self.default_height]])
        
    @property
    def default_framecenter_comp(self):
        return np.array([self.x_offset, 0, self.default_height])