import pygame

class KeysController:
    def __init__(self):
        self.alpha = 0
        self.beta = 0
        self.gamma = 0
        self.speed = 0.02
        
    def get_keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            self.alpha = self.beta = self.gamma = 0
        if keys[pygame.K_a]:
            self.alpha += self.speed
        if keys[pygame.K_d]:
            self.alpha -= self.speed
        if keys[pygame.K_w]:
            self.beta += self.speed
        if keys[pygame.K_s]:
            self.beta -= self.speed
        if keys[pygame.K_q]:
            self.gamma+= self.speed
        if keys[pygame.K_e]:
            self.gamma-= self.speed
        return self.alpha, self.beta, self.gamma
    
if __name__ == "__main__":
    try:
        pygame.init()
        clock = pygame.time.Clock()
        key_state = KeysController()
        running = True
        while running:
            pygame.event.get()
            a,b,c = key_state.get_keys()
            print(a, b, c)
            clock.tick(60)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pygame.quit()