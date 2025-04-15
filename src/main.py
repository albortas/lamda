import pygame

from src.motion.RobotController import RobotController
from src.controller.PS4Controller import PS4Controller
from src.animation.Animacion import SpotAnime

class JoystickMessage:
    def __init__(self, axes, buttons):
        self.axes = axes
        self.buttons = buttons
        
class Robot:
    def __init__(self):
        self.body = {'Lb': 187.1, 'Wb': 78}
        self.legs = {'d': 10.73, 'L0': 58.09, 'L1': 108.31, 'L2':138}
        self.robot = RobotController(self.body, self.legs)
        self.ps4 = PS4Controller()
        self.anime = SpotAnime()
    
    def iteration(self):
        joystick_state = self.ps4.get_joystick_state()
        msg = JoystickMessage(joystick_state['axes'], joystick_state['buttons'])
        self.robot.joystick_command(msg)
        self.robot.run()
        self.anime.screen.fill("white")
        self.anime.draw_floor(self.robot.state.body_center, self.robot.state.theta)
        self.anime.draw_axes(self.robot.state.body_center)
        self.anime.draw_radius_and_direction(self.robot.state.body_center,
                                             self.robot.state.theta,
                                             self.robot.state.center,
                                             self.robot.state.steering,
                                             self.robot.state.walking_direction,
                                             self.robot.state.walking_speed)
        
        self.anime.draw_legs(self.robot.state.body_center,
                             self.robot.state.framecenter_comp,
                             self.robot.default_frame,
                             self.robot.state.foot_position,
                             self.robot.state.theta,
                             self.robot.state.angles_foot,
                             self.legs)
    
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
    pygame.quit()
    
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