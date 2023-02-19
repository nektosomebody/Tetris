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


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__()
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Board:
    def __init__(self):
        self.board = [['.'] * COUNT_W for _ in range(COUNT_H)]

        self.board_index = [[None] * COUNT_W for _ in range(COUNT_H)]

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
        self.scelet = SCELETONS[2]

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

            BOARD.board_index[self.y + delta_y][self.x + delta_x] = GLOBAL_ORDER_LAST

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
        global GLOBAL_ORDER_LAST
        if self.checking_down():
            self.y += 1
            for i in range(self.count_cubes):
                y, x = self.positions[i]
                BOARD.board[y][x] = '.'

                BOARD.board_index[y][x] = None

            for i in range(self.count_cubes):
                delta_y, delta_x = self.scelet[i + 2]
                BOARD.board[self.y + delta_y][self.x + delta_x] = '*'

                BOARD.board_index[self.y + delta_y][self.x + delta_x] = GLOBAL_ORDER_LAST

                self.positions[i] = (self.y + delta_y, self.x + delta_x)
        else:
            GLOBAL_ORDER_LAST += 1
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


def check_on_line():
    one = ['*'] * COUNT_W
    y_to_clean = []
    for i in range(COUNT_H):
        if BOARD.board[i] == one:
            y_to_clean.append(i)
    return y_to_clean


def cleaning(clean_y):
    global BOARD
    list_of_image_in_line = []  # список линий где нужно удалить квадраты
    for y in clean_y:
        one_line = []
        for index in BOARD.board_index[y]:
            image = BOARD.figures[index].image
            image = make_small(image)
            one_line.append(image)  # линия в виде списка с картинками
        list_of_image_in_line.append(one_line)

    for i in range(len(clean_y)):
        y = clean_y[i]
        one_l = list_of_image_in_line[i]
        for x in range(3):
            pygame.draw.rect(screen, pygame.color.Color('white'), (10, 10 + 30 * y, 30 * COUNT_W, 30))
            for j in range(COUNT_W):
                img = one_l[j][x]
                img_rect = pygame.Rect(15 + j * 30, 15 + y * 30, 30, 30)
                screen.blit(img, img_rect)
                pygame.display.update()
                clock.tick(FPS)
        del BOARD.board[y]
        BOARD.board.insert(0, ['.'] * COUNT_W)
        screen.fill((255, 255, 255))
        BOARD.draw()
        pygame.display.flip()
        clock.tick(FPS)


def make_small(image):
    new_img = None
    ret_lst = []
    width, height = 30, 30
    for i in range(3):
        new_img = pygame.transform.scale(image, (width - 10, height - 10))
        ret_lst.append(new_img)
        width -= 10
        height -= 10
    return ret_lst


if __name__ == '__main__':
    pygame.init()
    FPS = 10
    COUNT_W, COUNT_H = 24, 30
    one_sq = 30
    size = 20 + COUNT_W * one_sq, 20 + COUNT_H * one_sq
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    running = True

    GLOBAL_ORDER_LAST = 0

    SCELETONS = [[2, 3, (0, 0), (0, 0 - 1), (1, 0 - 1), (2, 0 - 1)],  # width, height, points, (delta_y, delta_x) ...
                 [3, 2, (0, 0), (1, 0), (1, 0 + 1), (1, 0 + 2)],
                 [4, 1, (0, 0), (0, 1), (0, 2), (0, 3)],
                 [2, 2, (0, 0), (0, 1), (1, 0), (1, 1)]]
    ALL_COLORS = ['red.png', 'yellow.png', 'green.png']

    ANIMATED_SPRITES = [AnimatedSprite(load_image("cut_sheet_green.png", (0, 255, 255)), 3, 1, 50, 50),
                        AnimatedSprite(load_image("cut_sheet_red.png", (0, 255, 255)), 3, 1, 50, 50),
                        AnimatedSprite(load_image("cut_sheet_yellow.png", (0, 255, 255)), 3, 1, 50, 50)]

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
        if active_figure is not None and active_figure.can_move_lr is False:
            active_figure = None
        BOARD.draw()
        clean_y = check_on_line()
        if clean_y:
            cleaning(clean_y)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
