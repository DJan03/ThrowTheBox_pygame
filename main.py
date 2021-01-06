import pygame
from typing import List, Dict
from math import sqrt
from random import shuffle
from copy import deepcopy


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
    color = (170, 170, 170)

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
        self.rect.center = self.rect.w // 2, self.rect.h // 2
        self.rect.centerx = x
        self.rect.centery = y


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
                 up=pygame.K_UP,
                 down=pygame.K_DOWN,
                 jump=pygame.K_c,
                 hold=pygame.K_x):
        super().__init__(group)

        self.image = pygame.transform.scale(pygame.image.load("hero.png"), (40, 40))

        self.rect = self.image.get_rect()
        self.rect.center = 20, 20
        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT // 2

        self.velocity_x = 0
        self.velocity_y = 0

        self.velocity_a = 1
        self.velocity_max = 10

        self.impulse_x = 0

        self.LEFT = left
        self.RIGHT = right
        self.UP = up
        self.DOWN = down
        self.JUMP = jump
        self.HOLD = hold
        self.keys = {}

        for i in [self.LEFT, self.RIGHT, self.UP, self.DOWN, self.JUMP, self.HOLD]:
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

        if self.keys[self.JUMP] and self.ready_to_jump:
            self.keys[self.JUMP] = False
            self.ready_to_jump = False
            self.velocity_y = -40

        if self.impulse_x != 0:
            if self.impulse_x > 0:
                self.impulse_x -= 1
            else:
                self.impulse_x += 1

        # apply velocity
        self.rect.centerx += self.velocity_x + self.impulse_x

        block_hit_list = pygame.sprite.spritecollide(self, objectManager.get(ObjectManager.BLOCK_KEY), False)
        for block in block_hit_list:
            if self.velocity_x > 0:
                self.rect.right = block.rect.left
                self.impulse_x = 0

                if self.keys[self.RIGHT]:
                    self.velocity_y = GRAVITY // 4

                    if self.keys[self.JUMP]:
                        self.keys[self.RIGHT] = False
                        self.keys[self.JUMP] = False
                        self.impulse_x = -20
                        self.velocity_y = -30
            elif self.velocity_x < 0:
                self.rect.left = block.rect.right
                self.impulse_x = 0

                if self.keys[self.LEFT]:
                    self.velocity_y = GRAVITY // 4

                    if self.keys[self.JUMP]:
                        self.keys[self.LEFT] = False
                        self.keys[self.JUMP] = False
                        self.impulse_x = 20
                        self.velocity_y = -30

        self.velocity_y += GRAVITY
        self.rect.centery += self.velocity_y

        block_hit_list = pygame.sprite.spritecollide(self, objectManager.get(ObjectManager.BLOCK_KEY), False)
        for block in block_hit_list:
            if self.velocity_y > 0:
                self.rect.bottom = block.rect.top
                self.ready_to_jump = True
            elif self.velocity_y < 0:
                self.rect.top = block.rect.bottom

            self.velocity_y = 0

        # boxes
        if self.holding_box is None and self.keys[self.HOLD]:
            box = pygame.sprite.spritecollideany(self, objectManager.get(ObjectManager.BOX_KEY))
            if box != None:
                self.holding_box = objectManager.get(ObjectManager.BOX_KEY).pop(objectManager.get(ObjectManager.BOX_KEY).index(box)) # TODO: fix this strange line
                self.holding_box.apply_velocity = False
        if self.holding_box != None and self.keys[self.HOLD]:
            self.holding_box.rect.centerx = self.rect.centerx
            self.holding_box.rect.centery = self.rect.centery

        if self.holding_box != None and self.keys[self.HOLD] == False:
            v_x = 0
            v_y = 0

            if self.keys[self.UP]:
                v_y -= 1
            if self.keys[self.DOWN]:
                v_y += 1
            if self.keys[self.LEFT]:
                v_x -= 1
            if self.keys[self.RIGHT]:
                v_x += 1

            self.holding_box.set_velocity(v_x * 20, v_y * 20 - 20)
            self.holding_box.apply_velocity = True
            objectManager.get(ObjectManager.BOX_KEY).append(self.holding_box) # TODO: change strange line
            self.holding_box = None

        if self.rect.centerx < 0 or self.rect.centerx > WIDTH or self.rect.centery < 0 or self.rect.centery > HEIGHT:
            self.rect.centerx = WIDTH // 2
            self.rect.centery = HEIGHT // 2


class Bullet(pygame.sprite.Sprite):
    def __init__(self, group, x, y, velocity_x, velocity_y):
        super().__init__(group)

        self.image = pygame.transform.scale(pygame.image.load("bullet.png"), (20, 20))

        self.rect = self.image.get_rect()
        self.rect.center = 10, 10
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def update(self, objectManager: ObjectManager):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        block_hit = pygame.sprite.spritecollideany(self, objectManager.get(ObjectManager.BLOCK_KEY))
        if block_hit is not None:
            objectManager.remove(self, ObjectManager.BULLET_KEY)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, group, x, y, shoot_cooldown=50):
        super().__init__(group)
        self.image = pygame.transform.scale(pygame.image.load("enemy.png"), (40, 40))

        self.rect = self.image.get_rect()
        self.rect.center = 20, 20
        self.rect.centerx = x
        self.rect.centery = y

        self.health = 2
        
        self.time_to_shoot = shoot_cooldown
        self.shoot_cooldown = shoot_cooldown

    def update(self, objectManager: ObjectManager):
        box_hit = pygame.sprite.spritecollideany(self, objectManager.get(ObjectManager.BOX_KEY))
        if box_hit is not None:
            self.health -= 1
            objectManager.remove(box_hit, ObjectManager.BOX_KEY)

            if self.health <= 0:
                objectManager.remove(self, ObjectManager.ENEMY_KEY)
        
        # shoot
        if self.time_to_shoot <= 0:
            self.time_to_shoot = self.shoot_cooldown
            self.shoot(objectManager)
        else:
            self.time_to_shoot -= 1
    
    def shoot(self, objectManager: ObjectManager):
        delta_x = objectManager.get(ObjectManager.PLAYER_KEY)[0].rect.centerx - self.rect.centerx
        delta_y = objectManager.get(ObjectManager.PLAYER_KEY)[0].rect.centery - self.rect.centery

        k = sqrt(delta_x ** 2 + delta_y ** 2)

        speed = 5

        v_x = (delta_x * speed) // k
        v_y = (delta_y * speed) // k

        objectManager.append(Bullet(objectManager.sprite_group, self.rect.centerx, self.rect.centery, v_x, v_y), ObjectManager.BULLET_KEY)


class SpawnManager:
    def __init__(self):
        self.points_for_enemy = [(125, 125), (275, 125), (400, 125), (525, 125), (675, 125),
                                 (125, 325), (275, 325), (400, 325), (525, 325), (675, 325)]
        self.points_for_box = [(275, 125), (400, 125), (525, 125), (125, 325), (275, 325), (400, 325), (525, 325), (675, 325)]

    def get_points_for_enemies(self, count):
        points = deepcopy(self.points_for_enemy)
        shuffle(points)
        return points[:count]

    def get_points_for_box(self, count):
        points = deepcopy(self.points_for_box)
        shuffle(points)
        return points[:count]

    def generate_new_level(self, objectManager):
        enemies_count = 1
        for x, y in self.get_points_for_enemies(enemies_count):
            objectManager.append(Enemy(objectManager.sprite_group, x, y), ObjectManager.ENEMY_KEY)

        for x, y in self.get_points_for_box(enemies_count * 2):
            objectManager.append(Box(objectManager.sprite_group, x, y), ObjectManager.BOX_KEY)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    spawnManager = SpawnManager()

    objectManager = ObjectManager()

    objectManager.append(Player(objectManager.sprite_group), ObjectManager.PLAYER_KEY)

    objectManager.append(Block(objectManager.sprite_group, 0, 0, WIDTH, 50), ObjectManager.BLOCK_KEY)  # top
    objectManager.append(Block(objectManager.sprite_group, 0, 400, WIDTH, 50), ObjectManager.BLOCK_KEY)  # bot
    objectManager.append(Block(objectManager.sprite_group, 0, 0, 50, 450), ObjectManager.BLOCK_KEY)  # left
    objectManager.append(Block(objectManager.sprite_group, 750, 0, 50, 450), ObjectManager.BLOCK_KEY)  # right
    objectManager.append(Block(objectManager.sprite_group, 200, 200, 400, 50), ObjectManager.BLOCK_KEY)  # center

    spawnManager.generate_new_level(objectManager)

    clock = pygame.time.Clock()
    RUN = True

    while RUN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
            objectManager.player_control(event)

        screen.fill((70, 70, 70))

        objectManager.update()
        objectManager.draw(screen)

        if objectManager.get(ObjectManager.ENEMY_KEY) == []:
            spawnManager.generate_new_level(objectManager)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
    pygame.quit()
