import os
import pygame

size = width, height = 500, 500
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
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


class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((SIDE_H, SIDE_H))
        pygame.draw.rect(self.image, pygame.Color("blue"), (0, 0, 20, 20))
        self.coords = (x, y)
        self.rect = pygame.Rect(*self.coords, SIDE_H, SIDE_H)
        self.v = DIST

    def update(self):
        if pygame.sprite.spritecollideany(self, all_sprites):
            self.v = 0
        self.rect = self.rect.move(0, self.v)

    def moving(self, v):
        self.rect.move(v, 0)


class GreyRect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(GreyRect, self).__init__()
        self.image = pygame.Surface(SIZE_R)
        pygame.draw.rect(self.image, pygame.Color("grey"), (0, 0, *SIZE_R))
        self.rect = pygame.Rect(x, y, *SIZE_R)
        self.coords = (x, y)


# группа, содержащая все спрайты
all_sprites = pygame.sprite.Group()
greyrect_group = pygame.sprite.Group()
DIST = 10
SIDE_H = 20
SIZE_R = (50, 10)
show = False
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                if not show:
                    show = True
                    hero = Hero(*event.pos)
                    hero.add(all_sprites)
                # hero.rect = pygame.Rect(*event.pos, *SIZE_R)
                else:
                    hero.coords = event.pos
                # hero.coords = event.pos
            if event.button == 1:
                grey_rect = GreyRect(*event.pos)
                grey_rect.add(all_sprites)
                grey_rect.add(greyrect_group)
        if event.type == pygame.KEYDOWN:
            if show:
                if event.key == pygame.K_LEFT:
                    hero.coords = (hero.coords[0] - 10, hero.coords[1])
                elif event.key == pygame.K_RIGHT:
                    hero.coords = (hero.coords[0] + 10, hero.coords[1])

    if show:
        if pygame.sprite.spritecollideany(hero, greyrect_group):
            DIST = 0
        else:
            DIST = 10
        hero.coords = (hero.coords[0], hero.coords[1] + DIST)
    screen.fill(pygame.Color("black"))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.update()
    clock.tick(30)

pygame.quit()
