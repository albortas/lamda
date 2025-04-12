import numpy as np

from src.motion.StateCommand import State, Command
from src.crawl.WalkController import WalkGaitController

class RobotController:
    def __init__(self, body, track):
        self.body = body
        self.track = track
        self.delta_x = self.body[0] * 0.5
        self.delta_y = self.body[1] * 0.5 + self.track
        self.x_shift_from = -10
        self.x_shift_back = -10
        self.walkGaitController = WalkGaitController(0.15, 0.10, 0.01, self.default_stance)
        self.currentController = self.walkGaitController
        self.state = State()
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
        