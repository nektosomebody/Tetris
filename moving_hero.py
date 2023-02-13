import os

import pygame


def load_image(name, color_key=None):
    fullname = os.path.join('./data', name)
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


def main():
    size = 300, 300
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Герой двигается!')

    # группа, содержащая все спрайты
    all_sprites = pygame.sprite.Group()

    # изображение должно лежать в папке data
    hero_image = load_image("creature.png")
    hero = pygame.sprite.Sprite(all_sprites)
    hero.image = hero_image
    hero.rect = hero.image.get_rect()

    # шаг перемещения
    dist = 20

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Проверяем нажатые кнопки
            key = pygame.key.get_pressed()
            if key[pygame.K_DOWN]:
                hero.rect.top += dist
            elif key[pygame.K_UP]:
                hero.rect.top -= dist
            if key[pygame.K_RIGHT]:
                hero.rect.left += dist
            elif key[pygame.K_LEFT]:
                hero.rect.left -= dist
        screen.fill(pygame.Color("white"))
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
