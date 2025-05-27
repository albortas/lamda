from math import pi, sin, cos
import pygame
import numpy as np
from src.kinematics.kinematics import forward_kinematics
from src.utils.transformations import display_rotate

"""Display colors """
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
YALE_BlUE =  (0,  53, 102)
BLUE_GREEN = (33, 158, 188)
OXFORD_BLUE = (2, 48, 71)
GREEN = (51, 204, 51)
ORANGE = (251, 133, 0)
GREY =  (225, 225, 225)
DARK_GREY=(100,100,100)
DARK_RED =(176,0,0)
SKY_BLUE = (142, 202, 230)
VIOLET =(207,175,255)
CYAN = (0,255,255)
MED_GREY = (170,170,170)

# Axes coordinates for animation
axes = np.array([[0, 0, 0],
                 [100, 0, 0],
                 [0, 100, 0],
                 [0, 0, 100]])


class Animation:
    """Clase para la animación de la simulación."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((600, 600))
        self.lineas_leg = np.array(range(40)).reshape(4,5,2)
    
    def draw_floor(self, center_map, theta):
        """Dibuja el suelo y la cuadrícula."""
        line = display_rotate(-center_map[0], -center_map[1], -center_map[2],
                              [theta[0], theta[1], 0, 0, 0, 0],
                              [500, 500, -500, -500],
                              [500, -500, -500, 500],
                              [0, 0, 0, 0])
        pygame.draw.polygon(self.screen, GREY, line, 0)

        for i in range(11):
            grid_line_x = display_rotate(-center_map[0], -center_map[1], -center_map[2],
                                         [theta[0], theta[1], 0, 0, 0, 0],
                                         [-500 + i * 100, -500 + i * 100],
                                         [-500, 500], [0, 0])
            pygame.draw.lines(self.screen, DARK_GREY, False, grid_line_x, 1)

            grid_line_y = display_rotate(-center_map[0], -center_map[1], -center_map[2],
                                         [theta[0], theta[1], 0, 0, 0, 0],
                                         [-500, 500],
                                         [-500 + i * 100, -500 + i * 100], [0, 0])
            pygame.draw.lines(self.screen, DARK_GREY, False, grid_line_y, 1)

    def draw_axes(self, center_map):
        """Dibuja los ejes X, Y, Z."""
        line = display_rotate(-center_map[0], -center_map[1], -center_map[2],
                              [0, 0, 0, 0, 0, 0], axes[:,0], axes[:, 1], axes[:,2])
        color_axes = ["RED", GREEN, "BLUE"]        
        for i, color in enumerate(color_axes):
            pygame.draw.line(self.screen, color, line[0], line[1+i], 2)

    def draw_radius_and_direction(self, center_map, theta, center, steering, walking_direction, walking_speed):
        """Dibuja el radio y la dirección."""
        center_display = True
        if steering < 2000:
            line_radius = display_rotate(-center_map[0], -center_map[1], -center_map[2],
                                         [0, 0, 0, 0, 0, 0],
                                         [center[0], center_map[0]], [center[1], center_map[1]], [0, 0])
        else:
            center_x1 = center_map[0] + (center[0] - center_map[0]) / steering * 2000
            center_y1 = center_map[1] + (center[1] - center_map[1]) / steering * 2000
            line_radius = display_rotate(-center_map[0], -center_map[1], -center_map[2],
                                         [0, 0, 0, 0, 0, 0],
                                         [center_x1, center_map[0]], [center_y1, center_map[1]], [0, 0])
            center_display = False
        
        xd = center_map[0] + walking_speed * cos(theta[2] + walking_direction - pi / 2)
        yd = center_map[1] + walking_speed * sin(theta[2] + walking_direction - pi / 2)
        line_direction = display_rotate(-center_map[0], -center_map[1], -center_map[2],
                                        [0, 0, 0, 0, 0, 0],
                                        [xd, center_map[0]], [yd, center_map[1]], [0, 0])
        
        

        #pygame.draw.lines(self.screen, CYAN, False, line_radius, 2)
        #if (center_display == True):
            #pygame.draw.circle(self.screen, BLACK,line_radius[0],5)
        pygame.draw.circle(self.screen, OXFORD_BLUE,line_radius[1],5)
        pygame.draw.lines(self.screen, BLUE_GREEN, False, line_direction, 2)
        
    

    def draw_legs(self, center_map, framecenter_comp, default_frame, foot_position, theta, angles, dim_legs):
        """Dibuja las patas del robot."""
        lista = list(range(4))
        
        lineb = display_rotate (framecenter_comp[0] - center_map[0],
                                framecenter_comp[1] - center_map[1],
                                framecenter_comp[2] - center_map[2],theta,
                                default_frame[0], default_frame[1], default_frame[2])
        
        legs = {
            "lf": {"x": default_frame[0,0], "y": default_frame[1,0], "angles": angles[:,0], "n_pos": 0},
            "rf": {"x": default_frame[0,1], "y": default_frame[1,1], "angles": angles[:,1], "n_pos": 1},
            "rr": {"x": default_frame[0,2], "y": default_frame[1,2], "angles": angles[:,2], "n_pos": 2},
            "lr": {"x": default_frame[0,3], "y": default_frame[1,3], "angles": angles[:,3], "n_pos": 3}
        }

        for i, (leg, data) in enumerate(legs.items()):
            fk = forward_kinematics(data["angles"], dim_legs, 1 if leg in ["lf", "lr"] else -1)
            x_leg = [data["x"], data["x"] + fk[0], data["x"] + fk[1], data["x"] + fk[2], data["x"] + foot_position[0,data["n_pos"]]]
            y_leg = [data["y"], data["y"] + fk[3], data["y"] + fk[4], data["y"] + fk[5], data["y"] + foot_position[1,data["n_pos"]]]
            z_leg = [0, fk[6], fk[7], fk[8], foot_position[2,data["n_pos"]]]
            
            line_leg = display_rotate(framecenter_comp[0] - center_map[0],
                                      framecenter_comp[1] - center_map[1],
                                      framecenter_comp[2] - center_map[2],
                                      theta, x_leg, y_leg, z_leg)
            lista[i] = line_leg            
            
            pygame.draw.lines(self.screen, ORANGE, False, line_leg, 4)
        
        pygame.draw.lines(self.screen, YALE_BlUE, True,lineb,10)
           
        self.lineas_leg = np.array(lista)
        
    def draw_area_sustentacion(self,center_map, CGabs, dCG, stance):
        linesus = []
        for i, valor in enumerate(stance):
            if valor:
                linesus.append(self.lineas_leg[i][4])
        
        lineCG = display_rotate(-center_map[0],-center_map[1],-center_map[2],
                                [0,0,0,0,0,0],
                                [CGabs[0],CGabs[0]],[CGabs[1], CGabs[1]],[0,CGabs[2]])
        
        linedCG = display_rotate(-center_map[0],-center_map[1],-center_map[2],
                                 [0,0,0,0,0,0],
                                 [CGabs[0],dCG[0]],[CGabs[1],dCG[1]],[0,0])
        
        pygame.draw.polygon(self.screen, SKY_BLUE,linesus,0)
        pygame.draw.lines(self.screen, BLACK,True,linesus,1)
        pygame.draw.lines(self.screen, BLACK,False, linedCG,1)
        pygame.draw.lines(self.screen, BLACK,False, lineCG,1)
        if (dCG[2] == True):
            pygame.draw.circle(self.screen, GREEN,lineCG[0],3)
        else:
            pygame.draw.circle(self.screen, "RED",lineCG[0],3)
        pygame.draw.circle(self.screen, DARK_GREY,lineCG[1],10)
            

    def animate(self, state, default_frame, legs):
        """Animación principal."""
        self.screen.fill(WHITE)
        # Dibujar elementos estáticos
        self.draw_floor(state.center_map, state.theta)
        self.draw_axes(state.center_map)
        # Dibujar el area de sustentacion
        self.draw_area_sustentacion(state.center_map, state.CGabs, state.dCG, state.stance)
        # Dibujar radio y dirección
        self.draw_radius_and_direction(state.center_map, state.theta, state.center, state.steering, state.walking_direction, state.walking_speed)
        # Dibujar patas
        self.draw_legs(state.center_map, state.framecenter_comp, default_frame, state.foot_position, state.theta, state.angles_foot, legs)

        pygame.display.flip()
