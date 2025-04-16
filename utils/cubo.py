import pygame
from math import cos, sin
import numpy as np

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
ROTATE_SPEED = 0.02 # Velocidad de rotación
escala = 100 # Escala de los puntos
beta_x = beta_y = beta_z = 0 # Ángulos de rotación
color_ejes = [(29, 94, 105),(35, 153, 142),(250, 52, 25),(243, 225, 182)]
color_cubo = (124, 188, 154)

pygame.init() # Inicializamos Pygame
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Ventana de 1280x720
clock = pygame.time.Clock() # Reloj para limitar los fps
running = True # Variable para controlar el bucle principal

# Matriz de proyección
Mp = np.array([[1,0,0],
              [0,1,0],
              [0,0,0]])

# Matrices de rotación
def matriz_rotacion_xyz(beta_x=0, beta_y=0, beta_z=0):
    Rx = np.array([ [1,0,0],
                    [0, cos(beta_x), -sin(beta_x)],
                    [0, sin(beta_x), cos(beta_x)]])

    Ry = np.array([ [cos(beta_y), 0, sin(beta_y)],
                    [0, 1, 0],
                    [-sin(beta_y), 0, cos(beta_y)]])

    Rz = np.array([ [cos(beta_z), -sin(beta_z), 0],
                    [sin(beta_z), cos(beta_z), 0],
                    [0, 0, 1]])
    return Rx, Ry, Rz

def dibujar_puntos(puntos,escala,color,coordenada_x,coordenada_y):
    p = [(0,0) for i in range(len(puntos))]
    i = 0
    for punto in puntos:
        rotacion_x = Rx @ punto.T # Rotamos los puntos en x
        rotacion_y = Ry @ rotacion_x # Rotamos los puntos en y
        rotacion_z = Rz @ rotacion_y # Rotamos los puntos en z
        puntos_2d = Mp @ rotacion_z # Multiplicamos la matriz de proyección por los puntos
        
        x = puntos_2d[0] * escala  + coordenada_x # Obtenemos la coordenada x
        y = puntos_2d[1] * escala  + coordenada_y # Obtenemos la coordenada y
        
        p[i] = (x, y) # Guardamos las coordenadas
        if len(puntos) == 8:            
            pygame.draw.circle(screen, color, (x,y), 5)
        else:
            pygame.draw.circle(screen, color[i], (x,y), 5)
        i += 1        
        
    return p

# Puntos de un cubo
cubo_puntos = np.array([[-1,1,1],
                   [1,1,1],
                   [1,-1,1],
                   [-1,-1,1],
                   [-1,1,-1],
                   [1,1,-1],
                   [1,-1,-1],
                   [-1,-1,-1]])
#print(len(cubo_puntos)) # Devuelve 8

# Puntos del plano 3D
puntos_origen = np.array([[0,0,0],
                      [1,0,0],
                      [0,1,0],
                      [0,0,1]])
                      

def conectar_todos_los_puntos(puntos):
    # Conectamos los puntos del cubo
    if len(puntos) == 8:
        conexiones = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
        colores = color_cubo
        for i, j in conexiones:
            pygame.draw.line(screen, colores , puntos[i], puntos[j], 3)
    else:
        conexiones = [(0,1),(0,2),(0,3)]
        colores = color_ejes
        for i, j in conexiones:
            pygame.draw.line(screen, colores[j], puntos[i], puntos[j], 3)


while running:   
    #Proyección de los cubo puntos al plano 2D
    screen.fill((0,0,0)) # Rellenamos la pantalla
    Rx, Ry, Rz = matriz_rotacion_xyz(beta_x, beta_y, beta_z)
    
    beta_x += 0.01
    beta_y += 0.01
    beta_z += 0.01
    
    p_cubo = dibujar_puntos(cubo_puntos,escala,color_cubo,SCREEN_WIDTH/2,SCREEN_HEIGHT/2)
    p_coordenadas = dibujar_puntos(puntos_origen,20,color_ejes,SCREEN_WIDTH/2,SCREEN_HEIGHT/2)    
    
    
    conectar_todos_los_puntos(p_coordenadas)
    conectar_todos_los_puntos(p_cubo)
    
    for event in pygame.event.get(): # Obtenemos los eventos
        if event.type == pygame.QUIT:# Si se cierra la ventana
            running = False
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            beta_x = beta_y = beta_z = 0
        if keys[pygame.K_a]:
            beta_x += ROTATE_SPEED
        if keys[pygame.K_d]:
            beta_x -= ROTATE_SPEED
        if keys[pygame.K_w]:
            beta_y += ROTATE_SPEED
        if keys[pygame.K_s]:
            beta_y -= ROTATE_SPEED
        if keys[pygame.K_q]:
            beta_z += ROTATE_SPEED
        if keys[pygame.K_e]:
            beta_z -= ROTATE_SPEED                                

    #screen.fill(("black")) # Rellenamos la pantalla
    
    pygame.display.flip() # Actualizamos la pantalla
    clock.tick(60) # Limitamos a 60 fps
pygame.quit() # Salimos de Pygame