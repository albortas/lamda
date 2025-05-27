import pygame

from src.motion.RobotController import RobotController
from src.controller.PS4Controller import PS4Controller
from src.animation.Animation import Animation

class JoystickMessage:
    def __init__(self, axes, buttons):
        self.axes = axes
        self.buttons = buttons
        
class Robot:
    def __init__(self):
        self.body = {'Lb': 223.5, 'Wb': 78}
        self.legs = {'d': 10.73, 'L0': 58.09, 'L1': 108.31, 'L2':138}
        self.robot = RobotController(self.body, self.legs)
        self.ps4 = PS4Controller()
        self.anime = Animation()
    
    def iteration(self):
        joystick_state = self.ps4.get_joystick_state()
        msg = JoystickMessage(joystick_state['axes'], joystick_state['buttons'])
        self.robot.joystick_command(msg)
        self.robot.run()
        self.anime.animate(self.robot.state, self.robot.default_frame, self.legs)
    
if __name__ == "__main__":  
    pygame.init()
    clock = pygame.time.Clock()
    robot = Robot()
    runnig = True
    while runnig:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runnig = False            
        robot.iteration()
        pygame.display.flip()
        clock.tick(60)
        
    """ try:
        pygame.init()
        clock = pygame.time.Clock()
        robot = Robot()
        runnig = True
        while runnig:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    runnig = False            
            robot.iteration()
            pygame.display.flip()
            clock.tick(60)
    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario.")
    except Exception as e:
        print(f"Programa detenido error: {e}, {type(e)}")
    finally:
        pygame.quit() """