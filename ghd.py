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


"""class Border(pygame.sprite.Sprite):
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
        self.mask = pygame.mask.from_surface(self.image)"""


class Board:
    def __init__(self):
        self.board = [['.'] * COUNT_W for _ in range(COUNT_H)]
        self.figures = []

    def draw(self):
        if self.figures:
            for figure in self.figures:
                image = figure.image
                for pos in figure.positions:
                    y, x = pos
                    screen.blit(image, (x * 30 + 10, y * 30 + 10))


class Figure(pygame.sprite.Sprite):
    def __init__(self, filename):  # сначала у потом х!
        super().__init__()
        self.image = load_image(filename)
        self.size = self.image.get_rect()
        self.scelet = random.choice(SCELETONS)      # относительно х

        self.width = self.scelet[0]
        self.height = self.scelet[1]

        self.x = random.randrange(-1 + self.width, COUNT_W - self.width + 1)
        self.y = 0
        self.positions = []     # относительно доски

        self.count_cubes = len(self.scelet) - 2

        self.can_move_lr = True

        for i in range(2, self.count_cubes + 2):  # мы всегда создаем на пустом месте
            delta_y, delta_x = self.scelet[i]
            BOARD.board[self.y + delta_y][self.x + delta_x] = '*'
            self.positions.append((self.y + delta_y, self.x + delta_x))  # координаты в списке

        BOARD.figures.append(self)

    def checking_down(self):
        can_move = True
        for i in range(self.count_cubes):
            y, x = self.positions[i]
            if y + 1 >= COUNT_H or BOARD.board[y + 1][x] != '.' and (y + 1, x) not in self.positions:
                can_move = False
                break
        return can_move

    def checking_left_right(self):
        can_move_l, can_move_r = True, True
        for i in range(self.count_cubes):
            y, x = self.positions[i]
            if x - 1 < 0 or BOARD.board[y][x - 1] != '.' and (y, x - 1) not in self.positions:  # проверяем что слева свободно...
                # ... и что мы не перемещаемся в себя
                can_move_l = False
            if x + 1 >= COUNT_W or BOARD.board[y][x + 1] != '.' and (y, x + 1) not in self.positions:
                can_move_r = False
            if not can_move_l and not can_move_r:
                break
        return can_move_l, can_move_r

    def update(self):
        if self.checking_down():
            self.y += 1
            for i in range(self.count_cubes):
                y, x = self.positions[i]
                BOARD.board[y][x] = '.'
            for i in range(self.count_cubes):
                delta_y, delta_x = self.scelet[i + 2]
                BOARD.board[self.y + delta_y][self.x + delta_x] = '*'
                self.positions[i] = (self.y + delta_y, self.x + delta_x)
        else:
            self.can_move_lr = False

    def moving(self, command):
        can_move_l, can_move_r = self.checking_left_right()
        if self.can_move_lr:
            if command == 'l' and can_move_l:
                self.x -= 1
                for i in range(self.count_cubes):
                    y, x = self.positions[i]
                    BOARD.board[y][x] = '.'
                for i in range(self.count_cubes):
                    delta_y, delta_x = self.scelet[i + 2]
                    BOARD.board[self.y + delta_y][self.x + delta_x] = '*'
                    self.positions[i] = (self.y + delta_y, self.x + delta_x)
            elif command == 'r' and can_move_r:
                self.x += 1
                for i in range(self.count_cubes):
                    y, x = self.positions[i]
                    BOARD.board[y][x] = '.'
                for i in range(self.count_cubes):
                    delta_y, delta_x = self.scelet[i + 2]
                    BOARD.board[self.y + delta_y][self.x + delta_x] = '*'
                    self.positions[i] = (self.y + delta_y, self.x + delta_x)


def cleaning(y):
    pass


if __name__ == '__main__':
    pygame.init()
    FPS = 15
    COUNT_W, COUNT_H = 25, 30
    one_sq = 30
    size = 20 + COUNT_W * one_sq, 20 + COUNT_H * one_sq
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    running = True

    SCELETONS = [[2, 3, (0, 0), (0, 0 - 1), (1, 0 - 1), (2, 0 - 1)],  # width, height, points
                 [3, 2, (0, 0), (1, 0), (1, 0 + 1), (1, 0 + 2)]]
    ALL_COLORS = ['one.png', 'two.png']

    BOARD = Board()
    active_figure = None

    while running:
        screen.fill(pygame.Color('white'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                active_figure = Figure(random.choice(ALL_COLORS))
            if event.type == pygame.KEYDOWN and active_figure is not None:
                if event.key == pygame.K_LEFT:
                    active_figure.moving('l')
                if event.key == pygame.K_RIGHT:
                    active_figure.moving('r')
        if active_figure is not None:
            active_figure.update()
        BOARD.draw()
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
