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


class Figure(pygame.sprite.Sprite):
    def __init__(self, filename):  # 'tetris_sp.png'
        super().__init__()
        self.image = load_image(filename, (128, 128, 128, 255))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.height = self.rect.height + 20
        self.v_down = DIST
        self.v_right_left = self.rect.width // 3
        self.rect.x = random.choice([i for i in range(0, WIDTH - self.rect.width + 2, self.rect.width // 3)])
        self.rect.top = 30

    def checking(self):
        col_m = False  # пересечение с остальными фигурами
        col_l, col_r, col_g = False, False, False  # пересечение с верт и горизонт стенками
        left, right = VER_BORDERS.sprites()
        if pygame.sprite.collide_mask(self, left):
            col_l = True
        if pygame.sprite.collide_mask(self, right):
            col_r = True
        old_rect = self.rect
        new_rect = self.rect.move(0, self.v_down)
        self.rect = new_rect
        for sp in HOR_BORDERS.sprites():
            if pygame.sprite.collide_mask(self, sp):
                print(pygame.sprite.collide_mask(self, sp))
                col_g = True
                break
        for sp2 in ALL_FIGURES.sprites():
            # print(sp2.rect.y, self.rect.y, self.rect.y + self.v_down)
            if pygame.sprite.collide_mask(self, sp2) and self != sp2:
                col_m = True
                break
        if col_g or col_m:
            self.rect = old_rect
        return col_l, col_r, col_g, col_m

    def update(self):
        col_l, col_r, *another = self.checking()
        if any(another):
            # self.rect = self.rect.move(0, self.v_down * -1)
            self.v_down = 0
            ALL_FIGURES.add(self)
        else:
            self.rect = self.rect.move(0, self.v_down)

    def moving(self, comand):
        col_l, col_r, col_g, col_m = self.checking()
        if comand == 'l' and not col_l:
            self.rect = self.rect.move(-1 * self.v_right_left, 0)
        elif comand == 'r' and not col_r:
            self.rect = self.rect.move(self.v_right_left, 0)
        elif comand == 'd' and not any(another):
            self.rect = self.rect.move(0, self.v_down)
        if comand == 'u':
            self.rect = self.rect.move(0, -1 * DIST)


def make_design():
    Border(10, 10, WIDTH - 10, 10)  # верхняя
    Border(10, HEIGHT - 10, WIDTH - 10, HEIGHT - 10)  # нижняя
    Border(10, 10, 10, HEIGHT - 10)  # левая
    Border(WIDTH - 10, 10, WIDTH - 10, HEIGHT - 10)  # правая

    pygame.draw.line(screen, (255, 255, 0), (10, 10), (WIDTH - 10, 10))
    pygame.draw.line(screen, (255, 255, 0), (10, HEIGHT - 10), (WIDTH - 10, HEIGHT - 10))
    pygame.draw.line(screen, (255, 255, 0), (10, 10), (10, HEIGHT - 10))
    pygame.draw.line(screen, (255, 255, 0), (WIDTH - 10, 10), (WIDTH - 10, HEIGHT - 10))


pygame.init()
FPS = 20
one_sq = 30
size = WIDTH, HEIGHT = 20 * one_sq, 20 * one_sq
# print(WIDTH, HEIGHT)
DIST = 10
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
make_design()
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
