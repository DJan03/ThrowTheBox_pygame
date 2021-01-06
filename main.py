import pygame
from typing import List, Dict


WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 4

class ObjectManager:
    BLOCK_KEY = "block"
    BOX_KEY = "box"
    PLAYER_KEY = "player"
    ENEMY_KEY = "enemy"
    BULLET_KEY = "bullet"

    def __init__(self):
        self.sprite_group = pygame.sprite.Group()
        self.lib = {}

        for key in [ObjectManager.BLOCK_KEY,
                    ObjectManager.BOX_KEY,
                    ObjectManager.PLAYER_KEY,
                    ObjectManager.ENEMY_KEY,
                    ObjectManager.BULLET_KEY]:
            self.lib[key] = []

    def player_control(self, event):
        self.lib[ObjectManager.PLAYER_KEY][0].control(event)

    def draw(self, screen):
        self.sprite_group.draw(screen)

    def update(self):
        self.sprite_group.update(self)

    def remove(self, object, key):
        self.sprite_group.remove(object)
        self.lib[key].remove(object)

    def append(self, object, key):
        self.lib[key].append(object)

    def get(self, key):
        return self.lib[key]


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

    def update(self, objectManager: ObjectManager):
        if self.apply_velocity:
            self.rect.x += self.velocity_x

            block_hit_list = pygame.sprite.spritecollide(self, objectManager.get(ObjectManager.BLOCK_KEY), False)
            for block in block_hit_list:
                if self.velocity_x > 0:
                    self.rect.right = block.rect.left
                    self.velocity_x = -abs(self.velocity_x) // 2
                elif self.velocity_x < 0:
                    self.rect.left = block.rect.right
                    self.velocity_x = abs(self.velocity_x) // 2

            self.velocity_y += GRAVITY
            self.rect.y += self.velocity_y

            block_hit_list = pygame.sprite.spritecollide(self, objectManager.get(ObjectManager.BLOCK_KEY), False)
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
    def __init__(self, group: pygame.sprite.Group,
                 left=pygame.K_LEFT,
                 right=pygame.K_RIGHT,
                 up=pygame.K_UP, down=pygame.K_DOWN,
                 use=pygame.K_SPACE):
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

    def update(self, objectManager: ObjectManager):
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

        block_hit_list = pygame.sprite.spritecollide(self, objectManager.get(ObjectManager.BLOCK_KEY), False)
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

        block_hit_list = pygame.sprite.spritecollide(self, objectManager.get(ObjectManager.BLOCK_KEY), False)
        for block in block_hit_list:
            if self.velocity_y > 0:
                self.rect.bottom = block.rect.top
                self.ready_to_jump = True
            elif self.velocity_y < 0:
                self.rect.top = block.rect.bottom

            self.velocity_y = 0

        # boxes
        if self.holding_box is None and self.keys[self.USE]:
            box = pygame.sprite.spritecollideany(self, objectManager.get(ObjectManager.BOX_KEY))
            if box != None:
                self.holding_box = objectManager.get(ObjectManager.BOX_KEY).pop(objectManager.get(ObjectManager.BOX_KEY).index(box)) # TODO: fix this strange line
                self.holding_box.apply_velocity = False
        if self.holding_box != None and self.keys[self.USE]:
            self.holding_box.rect.x = self.rect.x
            self.holding_box.rect.y = self.rect.y

        if self.holding_box != None and self.keys[self.USE] == False:
            self.holding_box.set_velocity(self.velocity_x * 5, self.velocity_y * 3 - 20)
            self.holding_box.apply_velocity = True
            objectManager.get(ObjectManager.BOX_KEY).append(self.holding_box) # TODO: change strange line
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

    def update(self, objectManager: ObjectManager):
        box_hit = pygame.sprite.spritecollideany(self, objectManager.get(ObjectManager.BOX_KEY))
        if box_hit is not None:
            self.health -= 1
            objectManager.remove(box_hit, ObjectManager.BOX_KEY)

            if self.health <= 0:
                objectManager.remove(self, ObjectManager.ENEMY_KEY)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    objectManager = ObjectManager()

    objectManager.append(Player(objectManager.sprite_group), ObjectManager.PLAYER_KEY)

    objectManager.append(Block(objectManager.sprite_group, 0, 0, WIDTH, 50), ObjectManager.BLOCK_KEY)  # top
    objectManager.append(Block(objectManager.sprite_group, 0, 400, WIDTH, 50), ObjectManager.BLOCK_KEY)  # bot
    objectManager.append(Block(objectManager.sprite_group, 0, 0, 50, 450), ObjectManager.BLOCK_KEY)  # left
    objectManager.append(Block(objectManager.sprite_group, 750, 0, 50, 450), ObjectManager.BLOCK_KEY)  # right
    objectManager.append(Block(objectManager.sprite_group, 200, 200, 400, 50), ObjectManager.BLOCK_KEY)  # center

    objectManager.append(Box(objectManager.sprite_group, WIDTH // 2, HEIGHT // 2), ObjectManager.BOX_KEY)
    objectManager.append(Box(objectManager.sprite_group, WIDTH // 2, HEIGHT // 2), ObjectManager.BOX_KEY)

    objectManager.append(Enemy(objectManager.sprite_group, WIDTH // 2, 100), ObjectManager.ENEMY_KEY)

    clock = pygame.time.Clock()
    RUN = True

    while RUN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
            objectManager.player_control(event)

        screen.fill((50, 50, 50))

        objectManager.update()
        objectManager.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
    pygame.quit()
