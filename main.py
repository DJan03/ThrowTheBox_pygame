import pygame
from typing import List, Dict


WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 10


class GameObject(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, apply_gravity: bool, lose_velocity: bool, image: pygame.Surface):
        super().__init__(group)
        self.apply_gravity = apply_gravity
        self.lose_velocity = lose_velocity

        self.image = image
        self.rect = self.image.get_rect()

        self.velocity_x = 0
        self.velocity_y = 0

    def update(self):
        # TODO: create new method for every section
        if self.apply_gravity:
            self.velocity_y += GRAVITY
        if self.lose_velocity:
            pass

        self.rect = self.rect.move(self.velocity_x, self.velocity_y)

        # TODO: need to change that. Add simple borders at bot
        if self.rect.y > HEIGHT - 50:
            self.rect.y = HEIGHT - 50


    def set_velocity(self, x: int, y: int):
        self.velocity_x = x
        self.velocity_y = y


class Player(GameObject):
    def __init__(self, group: pygame.sprite.Group, image: pygame.Surface, keys: Dict[int, bool]):
        super().__init__(group, True, True, image)

        self.speed = 10
        self.keys = keys # TODO: need to rework

    def control(self, event):
        if event.type == pygame.KEYDOWN:
            for key in self.keys:
                if event.key == key:
                    self.keys[key] = True
                    break
        if event.type == pygame.KEYUP:
            for key in self.keys:
                if event.key == key:
                    self.keys[key] = False
                    break

    def move(self):
        input = [self.keys[key] for key in self.keys]

        if input[0] and input[1]:
            self.velocity_x = 0
        elif input[0]:
            self.velocity_x = -10
        elif input[1]:
            self.velocity_x = 10
        else:
            self.velocity_x = 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    square = pygame.Surface((50, 50))
    square.fill((255, 255, 255))

    sprite_group = pygame.sprite.Group()

    player = Player(sprite_group, square, {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_SPACE: False})

    clock = pygame.time.Clock()
    RUN = True

    while RUN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
            player.control(event)

        screen.fill((50, 50, 50))

        sprite_group.update()
        sprite_group.draw(screen)
        player.move()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
    pygame.quit()