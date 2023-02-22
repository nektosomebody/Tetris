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


class Board:
    def __init__(self):
        self.board = [['.'] * COUNT_W for _ in range(COUNT_H)]

        self.board_index = [[None] * COUNT_W for _ in range(COUNT_H)]

        self.figures = []

    def draw(self):
        if self.figures:
            for figure in self.figures:
                image = figure.image
                for i in range(len(figure.positions)):
                    y, x = figure.positions[i]
                    if BOARD.board[y][x] == '*':
                        screen.blit(image, (x * 30 + BORDER_LEFT_RIGHT, y * 30 + BORDER_UP))

    def change_y(self, del_y):
        for j in range(len(self.figures)):
            y = self.figures[j].y
            if y < del_y:
                self.figures[j].y += 1
                self.figures[j].make_positions()
        return


class Figure(pygame.sprite.Sprite):
    def __init__(self, filename):  # сначала у потом х!
        super().__init__()
        self.image = load_image(filename)
        self.size = self.image.get_rect()
        self.scelet = random.choice(SCELETONS)      # относительно х
        # self.scelet = SCELETONS[2]

        self.width = self.scelet[0]
        self.height = self.scelet[1]

        self.x = random.randrange(-1 + self.width, COUNT_W - self.width + 1)
        self.y = 0
        self.positions = []     # относительно доски

        self.count_cubes = len(self.scelet) - 2

        self.can_move_lr = True
        self.make_positions()

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
            if x - 1 < 0 or BOARD.board[y][x - 1] != '.' and (y, x - 1) not in self.positions:
                # проверяем что слева свободно и что мы не перемещаемся в себя
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

    def make_positions(self):
        self.positions = []
        for i in range(2, self.count_cubes + 2):  # мы всегда создаем на пустом месте
            delta_y, delta_x = self.scelet[i]
            BOARD.board[self.y + delta_y][self.x + delta_x] = '*'

            BOARD.board_index[self.y + delta_y][self.x + delta_x] = GLOBAL_ORDER_LAST

            self.positions.append((self.y + delta_y, self.x + delta_x))  # координаты в списке


def check_on_line():
    one = ['*'] * COUNT_W
    y_to_clean = []
    for i in range(COUNT_H):
        if BOARD.board[i] == one:
            y_to_clean.append(i)
    return y_to_clean


def cleaning(clean_y):
    global BOARD
    global TOTAL_SCORE
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
        del BOARD.board_index[y]
        BOARD.board.insert(0, ['.'] * COUNT_W)
        BOARD.board_index.insert(0, [None] * COUNT_W)
        BOARD.change_y(y)
        TOTAL_SCORE += COUNT_OF_POINTS * COUNT_W
        screen.fill((255, 255, 255))
        design()
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


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    screen.fill(pygame.Color('white'))
    text_coord = 50
    font_main = pygame.font.Font("unicephalon.ttf", 100)
    s_r = font_main.render("TETRIS", 1, pygame.Color('black'))
    in_r = s_r.get_rect()
    in_r.x = (WIDTH - in_r.width) // 2
    in_r.top = text_coord
    screen.blit(s_r, in_r)
    font = pygame.font.Font(None, 140)

    button_start = font.render('START', True, pygame.Color('white'))
    button_start_rect = button_start.get_rect()
    width_but, height_but = button_start_rect.width + 20, button_start_rect.height + 20
    pygame.draw.rect(screen, (255, 255, 87), ((WIDTH - width_but) // 2, (HEIGHT - height_but) // 3 * 2,
                                              width_but, height_but))
    button_start_rect.x = (WIDTH - width_but) // 2 + 10
    button_start_rect.top = (HEIGHT - height_but) // 3 * 2 + 10
    screen.blit(button_start, button_start_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if button_start_rect.x <= x <= (button_start_rect.x + button_start_rect.width) and\
                        button_start_rect.y <= y <= (button_start_rect.y + button_start_rect.height):
                    return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def game_over():
    screen.fill(pygame.color.Color('white'))

    font = pygame.font.Font(None, 100)  # score
    score = font.render(f"TOTAL SCORE {TOTAL_SCORE}", 1, pygame.color.Color('black'))
    score_rect = score.get_rect()
    screen.blit(score,
                ((BORDER_LEFT_RIGHT * 2 + COUNT_W * one_sq - score_rect.width) // 2, (BORDER_DOWN + BORDER_UP + COUNT_H * one_sq - score_rect.height) // 3))

    font = pygame.font.Font(None, 70)
    go_back = font.render('GO BACK', True, pygame.Color('black'))
    go_back_rect = go_back.get_rect()
    dist_x = (COUNT_W * one_sq + BORDER_LEFT_RIGHT * 2 - go_back_rect.width * 2) // 3
    dist_y = ((COUNT_H * one_sq + BORDER_DOWN + BORDER_UP) - (score_rect.y + score_rect.height) - go_back_rect.height) // 2
    go_back_rect.x = dist_x
    go_back_rect.y = (score_rect.y + score_rect.height) + dist_y
    screen.blit(go_back, (go_back_rect.x, go_back_rect.y))

    # button 1
    but_rect = pygame.rect.Rect(go_back_rect.x - 3, go_back_rect.y - 3, go_back_rect.width + 5, go_back_rect.height + 5)
    pygame.draw.rect(screen, pygame.color.Color('orange'), but_rect, border_radius=5, width=4)

    restart = font.render('RESTART', True, pygame.Color('black'))
    restart_rect = restart.get_rect()
    restart_rect.x = dist_x * 2 + go_back_rect.width
    restart_rect.y = go_back_rect.y
    screen.blit(restart, (restart_rect.x, restart_rect.y))

    # button 2
    but_rect.x = restart_rect.x - 5
    pygame.draw.rect(screen, pygame.color.Color('orange'), but_rect, border_radius=5, width=4)

    running = True
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if go_back_rect.x <= x <= (go_back_rect.x + go_back_rect.width) and \
                        go_back_rect.y <= y <= (go_back_rect.y + go_back_rect.height):
                    return
                if restart_rect.x <= x <= (restart_rect.x + restart_rect.width) and \
                        restart_rect.y <= y <= (restart_rect.y + restart_rect.height):
                    return
        pygame.display.flip()
        clock.tick(FPS)


def design():
    pygame.draw.rect(screen, (115, 210, 70), (0, BORDER_UP + COUNT_H * one_sq,
                                              COUNT_W * one_sq + BORDER_LEFT_RIGHT * 2, BORDER_DOWN))

    pygame.draw.rect(screen, (0, 0, 0), (0, 0, COUNT_W * one_sq + BORDER_LEFT_RIGHT * 2, BORDER_UP))      # top
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, BORDER_LEFT_RIGHT, one_sq * COUNT_H + BORDER_UP))      # left
    pygame.draw.rect(screen, (0, 0, 0), (BORDER_LEFT_RIGHT + COUNT_W * one_sq, 0, BORDER_LEFT_RIGHT,
                                         BORDER_UP + one_sq * COUNT_H))       # right

    pygame.draw.rect(screen, (255, 0, 0), (BORDER_LEFT_RIGHT, BORDER_UP + one_sq * 3, COUNT_W * one_sq, 1))   # red line

    font = pygame.font.Font(None, 24)   # score
    score = font.render(f"YOUR SCORE {TOTAL_SCORE}", 1, pygame.color.Color('black'))
    score_rect = score.get_rect()
    screen.blit(score, ((COUNT_W * one_sq - score_rect.width) // 2, COUNT_H * one_sq + (BORDER_DOWN - score_rect.height) // 2))


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption('TETRIS')

    FPS = 10
    COUNT_W, COUNT_H = 20, 25
    BORDER_DOWN = 50
    BORDER_UP = 10
    BORDER_LEFT_RIGHT = 10
    one_sq = 30
    TOTAL_SCORE = 0
    COUNT_OF_POINTS = 5

    size = WIDTH, HEIGHT = BORDER_LEFT_RIGHT * 2 + COUNT_W * one_sq, 10 + BORDER_DOWN + COUNT_H * one_sq
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    running = True

    GLOBAL_ORDER_LAST = 0

    SCELETONS = [[2, 3, (0, 0), (0, 0 - 1), (1, 0 - 1), (2, 0 - 1)],  # width, height, points, (delta_y, delta_x) ...
                 [3, 2, (0, 0), (1, 0), (1, 0 + 1), (1, 0 + 2)],
                 [4, 1, (0, 0), (0, 1), (0, 2), (0, 3)],
                 [2, 2, (0, 0), (0, 1), (1, 0), (1, 1)],
                 [3, 2, (0, 0), (1, -1), (1, 0), (1, 1)],
                 [3, 2, (0, 0), (0, 1), (0, 2), (1, 1)],
                 [1, 4, (0, 0), (1, 0), (2, 0), (3, 0)],
                 [2, 1, (0, 0), (0, 1)]]
    ALL_COLORS = ['red.png', 'yellow.png', 'green.png', 'blue.png', 'pink.png']

    BOARD = Board()
    active_figure = None
    MAKE_NEW_FIGURE = pygame.USEREVENT + 1
    pygame.time.set_timer(MAKE_NEW_FIGURE, FPS)

    start_screen()
    while running:
        screen.fill(pygame.Color('white'))
        design()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            if event.type == MAKE_NEW_FIGURE and active_figure is None:
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
        if clean_y and not active_figure.checking_down():
            cleaning(clean_y)
        if '*' in BOARD.board[2] and active_figure is None:
            running = False
        clock.tick(FPS)
        pygame.display.flip()
    game_over()
    pygame.quit()
