import pygame
from typing import List, Dict


WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 10


class Block(pygame.sprite.Sprite):
    color = (125, 125, 125)

    def __init__(self, group, x, y, w, h):
        super().__init__(group)
        self.image = pygame.Surface((w, h))
        self.image.fill(Block.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Player(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, image: pygame.Surface, keys: Dict[int, bool]):
        super().__init__(group)

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2

        self.velocity_x = 0
        self.velocity_y = 0

        self.keys = keys

        self.ready_to_jump = False

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


    def update(self, blocks):
        # change velocity
        input = [self.keys[key] for key in self.keys]

        if input[0] and input[1]:
            self.velocity_x = 0
        elif input[0]:
            self.velocity_x = -10
        elif input[1]:
            self.velocity_x = 10
        else:
            self.velocity_x = 0

        if input[2] and self.ready_to_jump:
            self.ready_to_jump = False
            self.velocity_y = -70

        # apply veloticy
        self.rect.x += self.velocity_x

        block_hit_list = pygame.sprite.spritecollide(self, blocks, False)
        for block in block_hit_list:
            if self.velocity_x > 0:
                self.rect.right = block.rect.left
            elif self.velocity_x < 0:
                self.rect.left = block.rect.right

        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        block_hit_list = pygame.sprite.spritecollide(self, blocks, False)
        for block in block_hit_list:
            if self.velocity_y > 0:
                self.rect.bottom = block.rect.top
                self.ready_to_jump = True
            elif self.velocity_y < 0:
                self.rect.top = block.rect.bottom

            self.velocity_y = 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    square = pygame.Surface((50, 50))
    square.fill((255, 255, 255))

    sprite_group = pygame.sprite.Group()

    player = Player(sprite_group, square, {pygame.K_LEFT: False, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_SPACE: False})

    blocks = []
    blocks.append(Block(sprite_group, 0, HEIGHT - 200, WIDTH, 200))
    blocks.append(Block(sprite_group, 0, 0, WIDTH, 100))
    blocks.append(Block(sprite_group, 300, 200, 200, 50))
    blocks.append(Block(sprite_group, 0, 0, 100, HEIGHT))
    blocks.append(Block(sprite_group, WIDTH - 100, 0, 100, HEIGHT))

    clock = pygame.time.Clock()
    RUN = True

    while RUN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
            player.control(event)

        screen.fill((50, 50, 50))

        sprite_group.update(blocks)
        sprite_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
    pygame.quit()