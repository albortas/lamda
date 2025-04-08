from math import pi, sin, cos
import pygame
import numpy as np
from src.kinematics.kinematics import FK
from src.utils.transformations import display_rotate
from src.motion.Spot import Spot

"""Display colors """
BLACK = (0,   0,   0)
WHITE = (255, 255, 255)
BLUE =  (24,  84, 231)
GREEN = (51, 204, 51)
RED =   (255,   0,   0)
GREY =  (225, 225, 225)
DARK_GREY=(100,100,100)
DARK_RED =(176,0,0)
VIOLET =(207,175,255)
CYAN = (0,255,255)
DARK_CYAN =(0,127,127)
MED_GREY = (170,170,170)

# Axes coordinates for animation
axes = np.array([[0, 0, 0],
                 [100, 0, 0],
                 [0, 100, 0],
                 [0, 0, 100]])


class SpotAnime:
    
    def __init__(self):
        self.screen = pygame.display.set_mode((600, 600))
        self.lineas_leg = np.array(range(40)).reshape(4,5,2)
        self.torso = Spot()
    
    def draw_floor(self, pos):
        """Dibuja el suelo y la cuadrícula."""
        line = display_rotate(-pos[2][0], -pos[3][0], -pos[4][0],
                              [pos[1][0], pos[1][1], 0, 0, 0, 0],
                              [500, 500, -500, -500],
                              [500, -500, -500, 500],
                              [0, 0, 0, 0])
        pygame.draw.polygon(self.screen, GREY, line, 0)

        for i in range(11):
            grid_line_x = display_rotate(-pos[2][0], -pos[3][0], -pos[4][0],
                                         [pos[1][0], pos[1][1], 0, 0, 0, 0],
                                         [-500 + i * 100, -500 + i * 100],
                                         [-500, 500], [0, 0])
            pygame.draw.lines(self.screen, DARK_GREY, False, grid_line_x, 1)

            grid_line_y = display_rotate(-pos[2][0], -pos[3][0], -pos[4][0],
                                         [pos[1][0], pos[1][1], 0, 0, 0, 0],
                                         [-500, 500],
                                         [-500 + i * 100, -500 + i * 100], [0, 0])
            pygame.draw.lines(self.screen, DARK_GREY, False, grid_line_y, 1)

    def draw_axes(self, pos):
        """Dibuja los ejes X, Y, Z."""
        line = display_rotate(-pos[2][0], -pos[3][0], -pos[4][0], [0, 0, 0, 0, 0, 0], axes[:,0], axes[:, 1], axes[:,2])
        color_axes = ["RED", GREEN, BLUE]        
        for i, color in enumerate(color_axes):
            pygame.draw.line(self.screen, color, line[0], line[1+i], 2)

    def draw_radius_and_direction(self, pos, center_x, center_y, steering, walking_speed, walking_direction):
        """Dibuja el radio y la dirección."""
        center_display = True
        if steering < 2000:
            line_radius = display_rotate(-pos[2][0], -pos[3][0], -pos[4][0],
                                         [0, 0, 0, 0, 0, 0],
                                         [center_x, pos[2][0]], [center_y, pos[3][0]], [0, 0])
        else:
            center_x1 = pos[2][0] + (center_x - pos[2][0]) / steering * 2000
            center_y1 = pos[3][0] + (center_y - pos[3][0]) / steering * 2000
            line_radius = display_rotate(-pos[2][0], -pos[3][0], -pos[4][0],
                                         [0, 0, 0, 0, 0, 0],
                                         [center_x1, pos[2][0]], [center_y1, pos[3][0]], [0, 0])
            center_display = False
        
        xd = pos[2][0] + walking_speed * cos(pos[1][2] + walking_direction - pi / 2)
        yd = pos[3][0] + walking_speed * sin(pos[1][2] + walking_direction - pi / 2)
        line_direction = display_rotate(-pos[2][0], -pos[3][0], -pos[4][0],
                                        [0, 0, 0, 0, 0, 0],
                                        [xd, pos[2][0]], [yd, pos[3][0]], [0, 0])
        
        

        pygame.draw.lines(self.screen, CYAN, False, line_radius, 2)
        if (center_display == True):
            pygame.draw.circle(self.screen, BLACK,line_radius[0],5)
        pygame.draw.circle(self.screen, DARK_CYAN,line_radius[1],5)
        pygame.draw.lines(self.screen, GREEN, False, line_direction, 2)
        
    

    def draw_legs(self, pos, theta_spot, angles):
        """Dibuja las patas del robot."""
        lista = list(range(4))
        
        lineb = display_rotate (pos[2][1] - pos[2][0], pos[3][1] - pos[3][0], pos[4][1] - pos[4][0],theta_spot,
                                [self.torso.xlf,self.torso.xrf,self.torso.xrr, self.torso.xlr, self.torso.xlf],
                                [self.torso.ylf,self.torso.yrf,self.torso.yrr,self.torso.ylr,self.torso.ylf],
                                [self.torso.zlf,self.torso.zrf,self.torso.zrr,self.torso.zlr,self.torso.zlf])
        
        legs = {
            "lf": {"x": self.torso.xlf, "y": self.torso.ylf, "angles": angles[0], "n_pos": 0},
            "rf": {"x": self.torso.xrf, "y": self.torso.yrf, "angles": angles[1], "n_pos": 1},
            "rr": {"x": self.torso.xrr, "y": self.torso.yrr, "angles": angles[2], "n_pos": 2},
            "lr": {"x": self.torso.xlr, "y": self.torso.ylr, "angles": angles[3], "n_pos": 3}
        }

        for i, (leg, data) in enumerate(legs.items()):
            fk = FK(data["angles"], 1 if leg in ["lf", "lr"] else -1)
            x_leg = [data["x"], data["x"] + fk[0], data["x"] + fk[1], data["x"] + fk[2], data["x"] + pos[0][0,data["n_pos"]]]
            y_leg = [data["y"], data["y"] + fk[3], data["y"] + fk[4], data["y"] + fk[5], data["y"] + pos[0][1,data["n_pos"]]]
            z_leg = [0, fk[6], fk[7], fk[8], pos[0][2,data["n_pos"]]]
            
            line_leg = display_rotate(pos[2][1] - pos[2][0], pos[3][1] - pos[3][0], pos[4][1] - pos[4][0],
                                      theta_spot, x_leg, y_leg, z_leg)
            lista[i] = line_leg            
            
            pygame.draw.lines(self.screen, RED, False, line_leg, 4)
        
        pygame.draw.lines(self.screen, BLUE,False,lineb,10)
           
        self.lineas_leg = np.array(lista)
        
    def draw_area_sustentacion(self, stance, pos):
        linesus = []
        for i, valor in enumerate(stance):
            if valor:
                linesus.append(self.lineas_leg[i][4])
        
        lineCG = display_rotate(-pos[2][0],-pos[3][0],-pos[4][0],[0,0,0,0,0,0],[pos[2][7],pos[2][7]],[pos[3][7],pos[3][7]],[0,pos[4][7]])
        linedCG = display_rotate(-pos[2][0],-pos[3][0],-pos[4][0],[0,0,0,0,0,0], [pos[2][7],pos[2][8]],[pos[3][7],pos[3][8]],[0,0])
        
        pygame.draw.polygon(self.screen, VIOLET,linesus,0)
        pygame.draw.lines(self.screen, BLACK,True,linesus,1)
        pygame.draw.lines(self.screen, BLACK,False, linedCG,1)
        pygame.draw.lines(self.screen, BLACK,False, lineCG,1)
        if (pos[4][8] == True):
            pygame.draw.circle(self.screen, GREEN,lineCG[0],3)
        else:
            pygame.draw.circle(self.screen, RED,lineCG[0],3)
        pygame.draw.circle(self.screen, DARK_GREY,lineCG[1],10)
            

    def animate(self, pos, angle, center_x, center_y, thetalf, thetarf, thetarr, thetalr, walking_speed, walking_direction, steering, stance):
        """Animación principal."""
        self.screen.fill(WHITE)

        # Dibujar elementos estáticos
        self.draw_floor(pos)
        self.draw_axes(pos)

        self.draw_area_sustentacion(stance, pos)
        # Dibujar radio y dirección
        # Dibujar patas
        self.draw_radius_and_direction(pos, center_x, center_y, steering, walking_speed, walking_direction)
        angles = [thetalf, thetarf, thetarr, thetalr]
        self.draw_legs(pos, pos[1], angles)

        pygame.display.flip()
