import pygame

from src.motion.RobotController import RobotController
from src.controller.PS4Controller import PS4Controller

""" class JoystickMessage:
    def __init__(self, axes, buttons):
        self.axes = axes
        self.buttons = buttons """
        
class Robot:
    def __init__(self):
        self.robot = RobotController()
        self.ps4 = PS4Controller()
    
    def iteration(self):
        robot.main()
        """ joystick_state = self.ps4.get_joystick_state()
        msg = JoystickMessage(joystick_state['axes'], joystick_state['buttons'])
        self.robot.joystick_command(msg)
        self.robot.change_controller()
        foot_locations = self.robot.run() """
    
if __name__ == "__main__":
    try:
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
        pygame.quit()