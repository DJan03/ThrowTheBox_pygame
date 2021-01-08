import pygame
from typing import List, Dict
from math import sqrt
from random import shuffle, random, sample
from copy import deepcopy


WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 4

WINDOW_IS_OPEN = True

FROZE_DURATION = 200
FROZE_BOXES_CHANCE = 0.2
SPEED_UP_POWER = 12
MISS_CHANCE = 0.1
HEALTH_UP_POWER = 4
HEART_BOX_CHANCE = 0.75
MORE_BOXES_MODIFY = 3


class ObjectManager:
    BLOCK_KEY = "block"
    BOX_KEY = "box"
    PLAYER_KEY = "player"
    ENEMY_KEY = "enemy"
    BULLET_KEY = "bullet"
    HEART_KEY = "heart"

    def __init__(self):
        self.sprite_group = pygame.sprite.Group()
        self.lib = {}

        for key in [ObjectManager.BLOCK_KEY,
                    ObjectManager.BOX_KEY,
                    ObjectManager.PLAYER_KEY,
                    ObjectManager.ENEMY_KEY,
                    ObjectManager.BULLET_KEY,
                    ObjectManager.HEART_KEY]:
            self.lib[key] = []

    def player_control(self, event):
        self.lib[ObjectManager.PLAYER_KEY][0].control(event)

    def draw(self, screen):
        self.sprite_group.draw(screen)

    def update(self):
        self.sprite_group.update(self)

    def remove(self, object, key):
        try:
            self.sprite_group.remove(object)
            self.lib[key].remove(object)
        except ValueError:
            pass

    def append(self, object, key):
        self.lib[key].append(object)

    def get(self, key):
        return self.lib[key]

    def player(self):
        return self.lib[ObjectManager.PLAYER_KEY][0]

    def clear(self):
        self.player().clear_movement()
        for i in [ObjectManager.BOX_KEY, ObjectManager.ENEMY_KEY, ObjectManager.BULLET_KEY, ObjectManager.HEART_KEY]:
            a = self.lib[i].copy()
            for j in a:
                self.remove(j, i)


class Block(pygame.sprite.Sprite):
    color = (170, 170, 170)

    def __init__(self, group, x, y, w, h):
        super().__init__(group)
        self.image = pygame.Surface((w, h))
        self.image.fill(Block.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Heart(pygame.sprite.Sprite):
    image = pygame.transform.scale(pygame.image.load("data/heart.png"), (20, 20))
    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Heart.image.copy()

        self.rect = self.image.get_rect()
        self.rect.center = 10, 10
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity_y = 0

    def update(self, objectManager: ObjectManager):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        block_hit_list = pygame.sprite.spritecollide(self, objectManager.get(ObjectManager.BLOCK_KEY), False)
        for block in block_hit_list:
            if self.velocity_y > 0:
                self.rect.bottom = block.rect.top
                self.velocity_y = 0
            elif self.velocity_y < 0:
                self.rect.top = block.rect.bottom
                self.velocity_y = 0


class Box(pygame.sprite.Sprite):
    image = pygame.transform.scale(pygame.image.load("data/box.png"), (25, 20))
    image_frozen = pygame.transform.scale(pygame.image.load("data/box_frozen.png"), (25, 20))
    image_heart = pygame.transform.scale(pygame.image.load("data/box_heart.png"), (25, 20))

    def __init__(self, group, x, y, velocity_x=0, velocity_y=0, is_frozen=False, apply_velocity=True, apply_gravity=True, is_heart_box=False, is_bullet_box=False):
        super().__init__(group)

        self.image = Box.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = self.rect.w // 2, self.rect.h // 2
        self.rect.centerx = x
        self.rect.centery = y

        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

        self.apply_velocity = apply_velocity

        self.is_frozen_box = is_frozen
        self.apply_gravity = apply_gravity
        self.is_heart_box = is_heart_box
        self.is_bullet_box = is_bullet_box

        if self.is_frozen_box:
            self.image = Box.image_frozen.copy()
        if self.is_heart_box:
            self.image = Box.image_heart.copy()
        if self.is_bullet_box:
            self.image = pygame.transform.scale(Box.image.copy(), (12, 10))
            self.rect = self.image.get_rect()
            self.rect.center = self.rect.w // 2, self.rect.h // 2
            self.rect.centerx = x
            self.rect.centery = y

    def update(self, objectManager: ObjectManager):
        if self.apply_velocity:
            self.rect.x += self.velocity_x

            get_hit = False

            block_hit_list = pygame.sprite.spritecollide(self, objectManager.get(ObjectManager.BLOCK_KEY), False)
            for block in block_hit_list:
                if self.velocity_x > 0:
                    self.rect.right = block.rect.left
                    self.velocity_x = -abs(self.velocity_x) // 2
                elif self.velocity_x < 0:
                    self.rect.left = block.rect.right
                    self.velocity_x = abs(self.velocity_x) // 2

                self.apply_gravity = True
                get_hit = True

            if self.apply_gravity:
                if self.is_bullet_box:
                    pass
                else:
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
                    get_hit = True

                self.apply_gravity = True

            if abs(self.velocity_x) <= 2:
                self.velocity_x = 0

            if self.velocity_x == 0 and self.velocity_y == 0:
                self.apply_gravity = True

            if get_hit:
                if self.is_heart_box:
                    objectManager.append(Heart(objectManager.sprite_group, self.rect.centerx, self.rect.centery), ObjectManager.HEART_KEY)
                    objectManager.remove(self, ObjectManager.BOX_KEY)

            if self.is_bullet_box and (get_hit or (self.velocity_x == 0 and self.velocity_y == 0)):
                objectManager.remove(self, ObjectManager.BOX_KEY)

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

        self.image = pygame.transform.scale(pygame.image.load("data/hero.png"), (40, 40))

        self.rect = self.image.get_rect()
        self.rect.center = 20, 20
        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT // 2

        self.velocity_x = 0
        self.velocity_y = 0

        self.velocity_a = 1
        self.velocity_max = 8

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

        self.health = 3
        self.max_health = 3

        self.FROZEN_BOXES = "frozenbox"
        self.NOGRAV_THROW = "nogravthrow"
        self.SPEED_UP = "speedup"
        self.MISS = "miss"
        self.HEALTH_UP = "healthup"
        self.HEART_BOXES = "heartboxes"
        self.TURTLE = "turtle"
        self.CHOICE_UP = "choiceup"
        self.MORE_BOXES = "boreboxes"
        self.HIT_BOXES = "hitboxes"

        self.ability_lib = {
            self.FROZEN_BOXES: False,
            self.NOGRAV_THROW: False,
            self.SPEED_UP: False,
            self.MISS: False,
            self.HEALTH_UP: False,
            self.HEART_BOXES: False,
            self.TURTLE: False,
            self.CHOICE_UP: False,
            self.MORE_BOXES: False,
            self.HIT_BOXES: False
        }

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
            if self.velocity_x > 0:
                self.velocity_x = 0
            self.velocity_x -= self.velocity_a
            if self.velocity_x < -self.velocity_max:
                self.velocity_x = -self.velocity_max
        elif self.keys[self.RIGHT]:
            if self.velocity_x < 0:
                self.velocity_x = 0
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
            if box != None and box.is_bullet_box == False:
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

            if self.ability_lib[self.NOGRAV_THROW]:
                if v_y == 0:
                    self.holding_box.rect.y -= 30 # TODO: it can be super easy for player

                self.holding_box.set_velocity(v_x * 20, v_y * 20)
                self.holding_box.apply_gravity = False
            else:
                self.holding_box.set_velocity(v_x * 20, v_y * 20 - 20)
                self.holding_box.apply_gravity = True

            self.holding_box.apply_velocity = True
            objectManager.get(ObjectManager.BOX_KEY).append(self.holding_box) # TODO: change strange line
            self.holding_box = None

        # hearts
        heart_hit = pygame.sprite.spritecollideany(self, objectManager.get(ObjectManager.HEART_KEY))
        if heart_hit is not None:
            if self.health < self.max_health:
                self.health += 1
                objectManager.remove(heart_hit, ObjectManager.HEART_KEY)

        # bug
        if self.rect.centerx < 0 or self.rect.centerx > WIDTH or self.rect.centery < 0 or self.rect.centery > HEIGHT:
            self.rect.centerx = WIDTH // 2
            self.rect.centery = HEIGHT // 2

    def add_ability(self, key):
        self.ability_lib[key] = True

        if self.ability_lib[self.SPEED_UP]:
            self.velocity_max = SPEED_UP_POWER

        if self.ability_lib[self.HEALTH_UP]:
            self.health += HEALTH_UP_POWER - self.max_health
            self.max_health = HEALTH_UP_POWER

    def lose_health(self, objectManager):
        if self.ability_lib[self.TURTLE] and self.velocity_x == 0 and self.velocity_y == 0:
            pass
        elif self.ability_lib[self.MISS] and random() <= MISS_CHANCE:
            pass
        else:
            self.health -= 1

            if self.ability_lib[self.HIT_BOXES]:
                for x, y in [(-20, -20), (-20, 0), (-20, 20), (0, -20), (0, 20), (20, -20), (20, 0), (20, 20)]:
                    objectManager.append(Box(objectManager.sprite_group, self.rect.centerx, self.rect.centery,
                                             velocity_x=x, velocity_y=y, is_bullet_box=True), ObjectManager.BOX_KEY)

    def is_live(self):
        return self.health > 0

    def clear_movement(self):
        for key in self.keys:
            self.keys[key] = False
        self.velocity_x = 0
        self.velocity_y = GRAVITY
        self.impulse_x = 0


class Bullet(pygame.sprite.Sprite):
    def __init__(self, group, x, y, velocity_x, velocity_y):
        super().__init__(group)

        self.image = pygame.transform.scale(pygame.image.load("data/bullet.png"), (20, 20))

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

        player_hit = pygame.sprite.spritecollideany(self, objectManager.get(ObjectManager.PLAYER_KEY))
        if player_hit is not None:
            objectManager.player().lose_health(objectManager)
            objectManager.remove(self, objectManager.BULLET_KEY)


class Enemy(pygame.sprite.Sprite):
    image = pygame.transform.scale(pygame.image.load("data/enemy.png"), (40, 40))
    image_frozen = pygame.transform.scale(pygame.image.load("data/enemy_frozen.png"), (40, 40))
    def __init__(self, group, x, y, shoot_cooldown=100):
        super().__init__(group)
        self.image = Enemy.image.copy()

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
            list_of_boxes = objectManager.get(ObjectManager.BOX_KEY)
            box = list_of_boxes[list_of_boxes.index(box_hit)]
            if box.is_heart_box:
                return

            self.health -= 1

            if box.is_frozen_box:
                self.time_to_shoot = FROZE_DURATION

            objectManager.remove(box_hit, ObjectManager.BOX_KEY)

            if self.health <= 0:
                objectManager.remove(self, ObjectManager.ENEMY_KEY)
        
        # shoot
        if self.time_to_shoot <= 0:
            self.time_to_shoot = self.shoot_cooldown
            self.shoot(objectManager)
        else:
            if self.time_to_shoot > self.shoot_cooldown:
                self.image = Enemy.image_frozen.copy()
            else:
                self.image = Enemy.image.copy()

            self.time_to_shoot -= 1
    
    def shoot(self, objectManager: ObjectManager):
        delta_x = objectManager.player().rect.centerx - self.rect.centerx
        delta_y = objectManager.player().rect.centery - self.rect.centery

        k = sqrt(delta_x ** 2 + delta_y ** 2)

        speed = 5

        v_x = (delta_x * speed) // k
        v_y = (delta_y * speed) // k

        objectManager.append(Bullet(objectManager.sprite_group, self.rect.centerx, self.rect.centery, v_x, v_y), ObjectManager.BULLET_KEY)


class SpawnManager:
    def __init__(self):
        self.points_for_enemy = [(125, 125), (275, 125), (400, 125), (525, 125), (675, 125),
                                 (125, 325), (275, 325), (400, 325), (525, 325), (675, 325)]
        self.points_for_box = [(275, 175), (350, 175), (400, 175), (450, 175), (525, 175),
                               (125, 375), (200, 375), (275, 375), (350, 375), (400, 375),
                               (450, 375), (525, 375), (600, 375), (675, 375)]

        self.level = 0
        self.enemy_count_in_level = [0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5]

    def get_points_for_enemies(self, count):
        points = deepcopy(self.points_for_enemy)
        shuffle(points)
        return points[:count]

    def get_points_for_box(self, count):
        points = deepcopy(self.points_for_box)
        shuffle(points)
        return points[:count]

    def generate_new_level(self, objectManager, player: Player):
        if 0 <= self.level < len(self.enemy_count_in_level) - 1:
            self.level += 1
        else:
            self.level = -1

        enemies_count = self.enemy_count_in_level[self.level]

        for x, y in self.get_points_for_enemies(enemies_count):
            objectManager.append(Enemy(objectManager.sprite_group, x, y), ObjectManager.ENEMY_KEY)

        points = []
        count_modify = 2

        if player.ability_lib[player.MORE_BOXES]:
            count_modify = MORE_BOXES_MODIFY

        if player.ability_lib[player.HEART_BOXES] and random() <= HEART_BOX_CHANCE:
            poitns = self.get_points_for_box(enemies_count * count_modify + 1)

            x, y = poitns.pop(0)
            objectManager.append(Box(objectManager.sprite_group, x, y, is_heart_box=True), ObjectManager.BOX_KEY)
        else:
            poitns = self.get_points_for_box(enemies_count * count_modify)

        for x, y in poitns:
            if player.ability_lib[player.FROZEN_BOXES]:
                if random() <= FROZE_BOXES_CHANCE:
                    objectManager.append(Box(objectManager.sprite_group, x, y, is_frozen=True), ObjectManager.BOX_KEY)
                else:
                    objectManager.append(Box(objectManager.sprite_group, x, y), ObjectManager.BOX_KEY)
            else:
                objectManager.append(Box(objectManager.sprite_group, x, y), ObjectManager.BOX_KEY)


class UI:
    bg_color = (39, 39, 39)

    def __init__(self):
        self.background = pygame.Surface((WIDTH, 150))
        self.background.fill(UI.bg_color)

        self.player_health = 3
        self.max_player_health = 3

        self.heart_full_img = pygame.transform.scale(pygame.image.load("data/heart_full.png"), (45, 35))
        self.heart_empty_img = pygame.transform.scale(pygame.image.load("data/heart_empty.png"), (45, 35))

        self.heart_full_rect = self.heart_full_img.get_rect()
        self.heart_empty_rect = self.heart_empty_img.get_rect()

        self.heart_full_rect.center = 22, 16
        self.heart_empty_rect.center = 22, 16

        self.cards = []

    def set_cards(self, cards: List[pygame.Surface]):
        self.cards = cards.copy()

    def update(self, player: Player):
        self.player_health = player.health
        self.max_player_health = player.max_health

    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0, HEIGHT - 150, WIDTH, 150))

        for i in range(self.max_player_health):
            if i < self.player_health:
                screen.blit(self.heart_full_img, (WIDTH // 2 + i * 60 - 30 * self.max_player_health, HEIGHT - 140, 45, 35))
            else:
                screen.blit(self.heart_empty_img, (WIDTH // 2 + i * 60 - 30 * self.max_player_health, HEIGHT - 140, 45, 35))

        for i, img in enumerate(self.cards):
            screen.blit(img, (WIDTH // 2 + 10 + i * 80 - 40 * len(self.cards), 500))


class ChoiceManager:
    img_choice_up = pygame.image.load("data/card_choice_up.png")
    img_frozen_box = pygame.image.load("data/card_frozen_box.png")
    img_health_up = pygame.image.load("data/card_health_up.png")
    img_heart_boxes = pygame.image.load("data/card_heart_boxes.png")
    img_hit_boxes = pygame.image.load("data/card_hit_boxes.png")
    img_miss = pygame.image.load("data/card_miss.png")
    img_more_boxes = pygame.image.load("data/card_more_boxes.png")
    img_nograv_throw = pygame.image.load("data/card_nograv_throw.png")
    img_speed_up = pygame.image.load("data/card_speed_up.png")
    img_turtle = pygame.image.load("data/card_turtle.png")

    def __init__(self, player: Player):
        self.img_lib = {
            player.CHOICE_UP: ChoiceManager.img_choice_up,
            player.FROZEN_BOXES: ChoiceManager.img_frozen_box,
            player.HEALTH_UP: ChoiceManager.img_health_up,
            player.HEART_BOXES: ChoiceManager.img_heart_boxes,
            player.HIT_BOXES: ChoiceManager.img_hit_boxes,
            player.MISS: ChoiceManager.img_miss,
            player.MORE_BOXES: ChoiceManager.img_more_boxes,
            player.NOGRAV_THROW: ChoiceManager.img_nograv_throw,
            player.SPEED_UP: ChoiceManager.img_speed_up,
            player.TURTLE: ChoiceManager.img_turtle
        }

        self.get_abilities = []
        self.other_abilities = []

        for key in player.ability_lib.keys():
            if player.ability_lib[key]:
                self.get_abilities.append(key)
            else:
                self.other_abilities.append(key)

    def visualise_choice(self, screen, objectManager: ObjectManager, ui: UI):
        global WINDOW_IS_OPEN
        RUN = True
        clock = pygame.time.Clock()

        # create background picture
        background = pygame.Surface((WIDTH, HEIGHT))
        background.fill((70, 70, 70))
        objectManager.draw(background)
        ui.draw(background)

        dark_screen = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dark_screen.fill(pygame.Color(0, 0, 0, 50))
        background.blit(dark_screen, (0, 0))

        count = 2

        if objectManager.player().CHOICE_UP in self.get_abilities:
            count = 3

        if len(self.other_abilities) >= count:
            cards = sample(self.other_abilities, count)

            group = pygame.sprite.Group()

            sprites = [pygame.sprite.Sprite(group) for _ in range(count)]

            for i in range(count):
                sprites[i].image = pygame.transform.scale(self.img_lib[cards[i]], (70 * 2, 90 * 2))
                sprites[i].rect = sprites[i].image.get_rect()
                sprites[i].rect.x = WIDTH // 2 + i * 160 - 80 * count
                sprites[i].rect.y = 200

            while RUN and WINDOW_IS_OPEN:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        RUN = False
                        WINDOW_IS_OPEN = False
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            x, y = event.pos

                            collide_id = -1

                            for i in range(count):
                                if sprites[i].rect.collidepoint(x, y):
                                    collide_id = i
                                    break

                            if collide_id != -1:
                                self.other_abilities.remove(cards[collide_id])
                                objectManager.player().add_ability(cards[collide_id])
                                self.get_abilities.append(cards[collide_id])
                                RUN = False

                screen.fill((0, 0, 0))

                screen.blit(background, (0, 0))

                group.draw(screen)

                pygame.display.flip()
                clock.tick(FPS)

    def get_images(self):
        return [self.img_lib[i] for i in self.get_abilities]


def main():
    global WINDOW_IS_OPEN
    spawnManager = SpawnManager()

    objectManager = ObjectManager()

    objectManager.append(Player(objectManager.sprite_group), ObjectManager.PLAYER_KEY)

    objectManager.append(Block(objectManager.sprite_group, 0, 0, WIDTH, 50), ObjectManager.BLOCK_KEY)  # top
    objectManager.append(Block(objectManager.sprite_group, 0, 400, WIDTH, 50), ObjectManager.BLOCK_KEY)  # bot
    objectManager.append(Block(objectManager.sprite_group, 0, 0, 50, 450), ObjectManager.BLOCK_KEY)  # left
    objectManager.append(Block(objectManager.sprite_group, 750, 0, 50, 450), ObjectManager.BLOCK_KEY)  # right
    objectManager.append(Block(objectManager.sprite_group, 200, 200, 400, 50), ObjectManager.BLOCK_KEY)  # center

    spawnManager.generate_new_level(objectManager, objectManager.player())

    ui = UI()

    choiceManager = ChoiceManager(objectManager.player())

    clock = pygame.time.Clock()
    RUN = True

    while RUN and WINDOW_IS_OPEN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False
                WINDOW_IS_OPEN = False
            objectManager.player_control(event)

        screen.fill((70, 70, 70))

        objectManager.update()
        objectManager.draw(screen)

        ui.update(objectManager.player())
        ui.draw(screen)

        if objectManager.get(ObjectManager.ENEMY_KEY) == []:
            objectManager.clear()

            choiceManager.visualise_choice(screen, objectManager, ui)

            ui.set_cards(choiceManager.get_images())
            spawnManager.generate_new_level(objectManager, objectManager.player())

        if not(objectManager.player().is_live()):
            RUN = False

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    while WINDOW_IS_OPEN:
        main()

    pygame.quit()
