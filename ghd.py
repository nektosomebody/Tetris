import os
import pygame
import sys
import random


def load_image(name, color_key=None):
    fullname = os.path.join(r'data\TETRIS', name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__()
        if x1 == x2:  # вертикальная стенка
            self.add(VER_BORDERS)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(HOR_BORDERS)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
        self.mask = pygame.mask.from_surface(self.image)


class Figure(pygame.sprite.Sprite):
    def __init__(self, filename):  # 'tetris_sp.png'
        super().__init__()
        self.image = load_image(filename, (128, 128, 128, 255))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.v_down = DIST
        self.v_right_left = self.rect.width // 3
        self.rect.x = random.choice([i for i in range(10, WIDTH - self.rect.width - 20 + 1, self.rect.width // 3)])
        self.rect.top = 30

    def update(self):
        col_down_border, col_down_sprite = self.check_down()
        if col_down_border or col_down_sprite:
            self.v_down = 0
            ALL_FIGURES.add(self)
        else:
            self.rect = self.rect.move(0, self.v_down)

    def moving(self, comand):
        col_left_border, col_right_border, col_left_sprite, col_right_sprite = self.check_left_right()
        col_down_border, col_down_sprite = self.check_down()
        if comand == 'l' and not col_left_border and not col_left_sprite:
            self.rect = self.rect.move(-1 * self.v_right_left, 0)
        elif comand == 'r' and not col_right_border and not col_right_sprite:
            self.rect = self.rect.move(self.v_right_left, 0)
        elif comand == 'd' and not col_down_border and not col_down_sprite:
            self.rect = self.rect.move(0, self.v_down)

    def check_down(self):
        col_down_border, col_down_sprite = False, False     # пересечение с горизонт границей и нижними спрайтами

        old_rect = self.rect.copy()

        moving_self_down = self
        moving_self_down.rect = moving_self_down.rect.move(0, moving_self_down.v_down - 1)

        if pygame.sprite.collide_mask(moving_self_down, DOWN_BORDER):
            col_down_border = True

        for sp in ALL_FIGURES.sprites():
            if pygame.sprite.collide_mask(moving_self_down, sp):
                col_down_sprite = True
                break

        self.rect = old_rect.copy()
        return col_down_border, col_down_sprite

    def check_left_right(self):
        left, right = VER_BORDERS.sprites()
        col_left_border, col_right_border = False, False
        col_left_sprite, col_right_sprite = False, False

        old_rect = self.rect.copy()

        moving_self_left = self
        moving_self_left.rect = moving_self_left.rect.move(-1 * self.v_right_left + 4, 0)    # сдвинулись влево
        if pygame.sprite.collide_mask(moving_self_left, left):
            col_left_border = True
        for sp in ALL_FIGURES.sprites():
            if pygame.sprite.collide_mask(moving_self_left, sp):
                col_left_sprite = True
        self.rect = old_rect.copy()

        moving_self_right = self
        moving_self_right.rect = moving_self_right.rect.move(self.v_right_left - 3, 0)   # сдвинулись вправо
        if pygame.sprite.collide_mask(moving_self_right, right):
            col_right_border = True
        for sp in ALL_FIGURES.sprites():
            if pygame.sprite.collide_mask(moving_self_right, sp):
                col_right_sprite = True
        self.rect = old_rect.copy()

        return col_left_border, col_right_border, col_left_sprite, col_right_sprite


pygame.init()
FPS = 20
one_sq = 30
size = WIDTH, HEIGHT = 35 * one_sq, 30 * one_sq
DIST = 30
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
running = True

ALL_SPRITES = pygame.sprite.Group()
ALL_FIGURES = pygame.sprite.Group()
BORDERS = pygame.sprite.Group()
VER_BORDERS = pygame.sprite.Group()
HOR_BORDERS = pygame.sprite.Group()

# start_screen()
sp = None

TOP_BORDER = Border(10, 10, WIDTH - 10, 10)  # верхняя
print(TOP_BORDER.rect.x, TOP_BORDER.rect.y)
DOWN_BORDER = Border(10, HEIGHT - 10, WIDTH - 10, HEIGHT - 10)  # нижняя
print(DOWN_BORDER.rect.x, DOWN_BORDER.rect.y)
LEFT_BORDER = Border(10, 10, 10, HEIGHT - 10)  # левая
print(LEFT_BORDER.rect.x, LEFT_BORDER.rect.y)
RIGHT_BORDER = Border(WIDTH - 10, 10, WIDTH - 10, HEIGHT - 10)  # правая
print(RIGHT_BORDER.rect.x, RIGHT_BORDER.rect.y)

while running:
    screen.fill((255, 255, 255))

    pygame.draw.line(screen, (0, 0, 0), (10, 10), (WIDTH - 10, 10))
    pygame.draw.line(screen, (0, 0, 0), (10, HEIGHT - 10), (WIDTH - 10, HEIGHT - 10))
    pygame.draw.line(screen, (0, 0, 0), (10, 10), (10, HEIGHT - 10))
    pygame.draw.line(screen, (0, 0, 0), (WIDTH - 10, 10), (WIDTH - 10, HEIGHT - 10))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            sp = Figure('tetris_sp2.png')
            ALL_SPRITES.add(sp)
        if event.type == pygame.KEYDOWN and sp is not None:
            if event.key == pygame.K_LEFT:
                sp.moving('l')
            if event.key == pygame.K_RIGHT:
                sp.moving('r')
            if event.key == pygame.K_DOWN:
                sp.moving('d')
            if event.key == pygame.K_UP:
                sp.moving('u')
    ALL_SPRITES.update()
    ALL_SPRITES.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
