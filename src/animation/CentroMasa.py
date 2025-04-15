import pygame
import numpy as np
import math
from pygame.locals import *

# Configuración inicial
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Visualización Compensación Centro de Masa - Robot Cuadrúpedo")
clock = pygame.time.Clock()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)

# Parámetros del robot
BODY_LENGTH = 200
BODY_WIDTH = 100
LEG_LENGTH = 80
FOOT_SIZE = 10
COM_RADIUS = 15

class Visualizador:
    def __init__(self):
        self.foot_positions = np.array([
            [ BODY_LENGTH/2,  BODY_WIDTH/2, 0],  # Pata delantera derecha
            [ BODY_LENGTH/2, -BODY_WIDTH/2, 0],  # Pata delantera izquierda
            [-BODY_LENGTH/2,  BODY_WIDTH/2, 0],  # Pata trasera derecha
            [-BODY_LENGTH/2, -BODY_WIDTH/2, 0]   # Pata trasera izquierda
        ])
        
        self.body_shift_y = 0
        self.contact_phases = [1, 1, 1, 1]  # Todas las patas en contacto inicialmente
        self.phase_time = 0
        self.phase_duration = 2.0  # segundos por fase
        
    def update(self, dt):
        self.phase_time += dt
        
        # Ciclo de marcha simplificado (alternar patas)
        if self.phase_time > self.phase_duration:
            self.phase_time = 0
            # Cambiar el patrón de contacto (ejemplo: levantar una pata a la vez)
            self.contact_phases = [1, 1, 1, 1]
            leg_to_lift = int((self.phase_time / self.phase_duration) % 4)
            self.contact_phases[leg_to_lift] = 0
            
            # Compensación corporal: mover el cuerpo hacia el lado opuesto
            if leg_to_lift == 0 or leg_to_lift == 2:  # Patas derechas
                self.body_shift_y = -30  # Compensar a la izquierda
            else:  # Patas izquierdas
                self.body_shift_y = 30   # Compensar a la derecha
        
        # Suavizar el regreso al centro cuando todas las patas están en contacto
        if sum(self.contact_phases) == 4:
            self.body_shift_y *= 0.9  # Amortiguación
            
        # Mover las patas en swing (ejemplo simplificado)
        for i in range(4):
            if self.contact_phases[i] == 0:  # Pata en swing
                swing_height = 50 * math.sin(math.pi * self.phase_time / self.phase_duration)
                self.foot_positions[i, 2] = swing_height
    
    def draw(self, screen):
        screen.fill(WHITE)
        
        # Calcular centro de masa visual (simplificado)
        total_weight = sum(self.contact_phases) + 0.1  # Evitar división por cero
        com_x = 0
        com_y = self.body_shift_y  # Incluir compensación corporal
        
        # Dibujar el polígono de apoyo (solo patas en contacto)
        support_polygon = []
        for i in range(4):
            if self.contact_phases[i] == 1:
                foot_x = WIDTH/2 + self.foot_positions[i, 0]
                foot_y = HEIGHT/2 + self.foot_positions[i, 1]
                support_polygon.append((foot_x, foot_y))
        
        if len(support_polygon) >= 3:
            pygame.draw.polygon(screen, (200, 255, 200), support_polygon)
            
        
        # Dibujar patas
        for i in range(4):
            foot_x = WIDTH/2 + self.foot_positions[i, 0]
            foot_y = HEIGHT/2 + self.foot_positions[i, 1] + self.body_shift_y
            
            # Conexión cuerpo-pata
            body_x = WIDTH/2 + (BODY_LENGTH/2 if i < 2 else -BODY_LENGTH/2)
            body_y = HEIGHT/2 + (BODY_WIDTH/2 if i % 2 == 0 else -BODY_WIDTH/2) + self.body_shift_y
            
            pygame.draw.line(screen, BLACK, (body_x, body_y), (foot_x, foot_y), 3)
            
            # Pie (rojo si está en swing)
            color = RED if self.contact_phases[i] == 0 else GREEN
            pygame.draw.circle(screen, color, (int(foot_x), int(foot_y)), FOOT_SIZE)
        
        # Dibujar cuerpo
        body_rect = pygame.Rect(
            WIDTH/2 - BODY_LENGTH/2,
            HEIGHT/2 - BODY_WIDTH/2 + self.body_shift_y,
            BODY_LENGTH,
            BODY_WIDTH
        )
        pygame.draw.rect(screen, BLUE, body_rect, 2)
        
        # Dibujar centro de masa
        com_screen_x = WIDTH/2
        com_screen_y = HEIGHT/2 + self.body_shift_y
        pygame.draw.circle(screen, RED, (int(com_screen_x), int(com_screen_y)), COM_RADIUS)
        
        # Dibujar línea vertical desde CoM al suelo
        pygame.draw.line(screen, BLACK, (com_screen_x, com_screen_y), (com_screen_x, HEIGHT), 1)
        
        # Mostrar información
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Compensación corporal: {self.body_shift_y:.1f} px", True, BLACK)
        screen.blit(text, (20, 20))
        
        text2 = font.render("Patas en contacto: " + " ".join(str(p) for p in self.contact_phases), True, BLACK)
        screen.blit(text2, (20, 50))

# Bucle principal
vis = Visualizador()
running = True
last_time = pygame.time.get_ticks()

while running:
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_time) / 1000.0  # Delta time en segundos
    last_time = current_time
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
    
    vis.update(dt)
    vis.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()