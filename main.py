import pygame
from typing import List, Dict


WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 4


class Block(pygame.sprite.Sprite):
    color = (125, 125, 125)

    def __init__(self, group, x, y, w, h):
        super().__init__(group)
        self.image = pygame.Surface((w, h))
        self.image.fill(Block.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Box(pygame.sprite.Sprite):
    def __init__(self, group, x, y, apply_velocity=True, velocity_x=0, velocity_y=0):
        super().__init__(group)

        self.image = pygame.transform.scale(pygame.image.load("box.png"), (25, 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

        self.apply_velocity = apply_velocity

    def update(self, blocks, *args):
        if self.apply_velocity:
            self.rect.x += self.velocity_x

            block_hit_list = pygame.sprite.spritecollide(self, blocks, False)
            for block in block_hit_list:
                if self.velocity_x > 0:
                    self.rect.right = block.rect.left
                    self.velocity_x = -abs(self.velocity_x) // 2
                elif self.velocity_x < 0:
                    self.rect.left = block.rect.right
                    self.velocity_x = abs(self.velocity_x) // 2

            self.velocity_y += GRAVITY
            self.rect.y += self.velocity_y

            block_hit_list = pygame.sprite.spritecollide(self, blocks, False)
            for block in block_hit_list:
                if self.velocity_y > 0:
                    self.rect.bottom = block.rect.top
                    self.velocity_x = self.velocity_x // 2
                    self.velocity_y = -abs(self.velocity_x) // 2
                elif self.velocity_y < 0:
                    self.rect.top = block.rect.bottom
                    self.velocity_x = self.velocity_x // 2
                    self.velocity_y = self.velocity_x // 2

            if abs(self.velocity_x) <= 2:
                self.velocity_x = 0

    def set_velocity(self, x, y):
        self.velocity_x = x
        self.velocity_y = y


class Player(pygame.sprite.Sprite):
    def __init__(self, group: pygame.sprite.Group, left, right, up, down, use):
        super().__init__(group)

        self.image = pygame.transform.scale(pygame.image.load("hero.png"), (40, 40))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH // 2
        self.rect.y = HEIGHT // 2

        self.velocity_x = 0
        self.velocity_y = 0

        self.velocity_a = 1
        self.velocity_max = 10

        self.impulse_x = 0

        self.LEFT = left
        self.RIGHT = right
        self.UP = up
        self.DOWN = down
        self.USE = use
        self.keys = {}

        for i in [self.LEFT, self.RIGHT, self.UP, self.DOWN, self.USE]:
            self.keys[i] = False

        self.ready_to_jump = False

        self.holding_box = None

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

    def update(self, blocks, boxes: List[Box], *args):
        # change velocity
        if self.keys[self.LEFT] and self.keys[self.RIGHT]:
            self.velocity_x = 0
        elif self.keys[self.LEFT]:
            self.velocity_x -= self.velocity_a
            if self.velocity_x < -self.velocity_max:
                self.velocity_x = -self.velocity_max
        elif self.keys[self.RIGHT]:
            self.velocity_x += self.velocity_a
            if self.velocity_x > self.velocity_max:
                self.velocity_x = self.velocity_max
        else:
            self.velocity_x = 0

        if self.keys[self.UP] and self.ready_to_jump:
            self.keys[self.UP] = False
            self.ready_to_jump = False
            self.velocity_y = -40

        if self.impulse_x != 0:
            if self.impulse_x > 0:
                self.impulse_x -= 1
            else:
                self.impulse_x += 1


        # apply velocity
        self.rect.x += self.velocity_x + self.impulse_x

        block_hit_list = pygame.sprite.spritecollide(self, blocks, False)
        for block in block_hit_list:
            if self.velocity_x > 0:
                self.rect.right = block.rect.left
                self.impulse_x = 0

                if self.keys[self.RIGHT]:
                    self.velocity_y = GRAVITY // 4

                    if self.keys[self.UP]:
                        self.keys[self.RIGHT] = False
                        self.keys[self.UP] = False
                        self.impulse_x = -20
                        self.velocity_y = -30
            elif self.velocity_x < 0:
                self.rect.left = block.rect.right
                self.impulse_x = 0

                if self.keys[self.LEFT]:
                    self.velocity_y = GRAVITY // 4

                    if self.keys[self.UP]:
                        self.keys[self.LEFT] = False
                        self.keys[self.UP] = False
                        self.impulse_x = 20
                        self.velocity_y = -30

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

        # boxes
        if self.holding_box is None and self.keys[self.USE]:
            box = pygame.sprite.spritecollideany(self, boxes)
            if box != None:
                self.holding_box = boxes.pop(boxes.index(box))
                self.holding_box.apply_velocity = False
        if self.holding_box != None and self.keys[self.USE]:
            self.holding_box.rect.x = self.rect.x
            self.holding_box.rect.y = self.rect.y

        if self.holding_box != None and self.keys[self.USE] == False:
            self.holding_box.set_velocity(self.velocity_x * 5, self.velocity_y * 3 - 20)
            self.holding_box.apply_velocity = True
            boxes.append(self.holding_box)
            self.holding_box = None

        if self.rect.x < 0 or self.rect.x > WIDTH or self.rect.y < 0 or self.rect.y > HEIGHT:
            self.rect.x = WIDTH // 2
            self.rect.y = HEIGHT // 2

        print(self.rect.x, self.rect.y)


class Enemy(pygame.sprite.Sprite):
    color = (30, 30, 30)

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = pygame.Surface((40, 40))
        self.image.fill(Block.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.health = 2

    def update(self, blocks, boxes, enemies):
        box_hit = pygame.sprite.spritecollideany(self, boxes)
        if box_hit is not None:
            self.health -= 1
            boxes.remove(box_hit)
            self.groups()[0].remove(box_hit)

            if self.health <= 0:
                enemies.remove(self)
                self.groups()[0].remove(self)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    sprite_group = pygame.sprite.Group()

    player = Player(sprite_group, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_SPACE)

    boxes = []
    boxes.append(Box(sprite_group, WIDTH // 2, HEIGHT // 2))
    boxes.append(Box(sprite_group, WIDTH // 2, HEIGHT // 2))

    blocks = []
    blocks.append(Block(sprite_group, 0, 0, WIDTH, 50))             #top
    blocks.append(Block(sprite_group, 0, 400, WIDTH, 50))           # bot
    blocks.append(Block(sprite_group, 0, 0, 50, 450))               #left
    blocks.append(Block(sprite_group, 750, 0, 50, 450))             #right
    blocks.append(Block(sprite_group, 200, 200, 400, 50)) #center

    enemies = []
    enemies.append(Enemy(sprite_group, WIDTH // 2, 100))

    clock = pygame.time.Clock()
    RUN = True

    while RUN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
            player.control(event)

        screen.fill((50, 50, 50))

        sprite_group.update(blocks, boxes, enemies)
        sprite_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
    pygame.quit()