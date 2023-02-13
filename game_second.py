import pygame
from PIL import Image, ImageFilter, ImageEnhance


def blit_pil_image(screen, img, position):
    pygame_image = pygame.image.fromstring(img.tobytes(), img.size, "RGB")
    screen.blit(pygame_image, position)


def images_demo():
    img = Image.open(r"C:\Users\sns-h\PycharmProjects\pythonProject1\PyGame\flover.jpg")
    box_size = 400
    img.thumbnail((box_size, box_size))
    blit_pil_image(screen, img, (width // 2 - img.width // 2, 20 + box_size // 2 - img.height // 2))

    small_images = [img for _ in range(6)]
    for i in range(len(small_images)):
        small_images[i].thumbnail((150, 150))

    r, g, b = small_images[0].split()
    small_images[0] = Image.merge("RGB", (r.point(lambda x: x // 2), g, b))
    small_images[1] = Image.merge("RGB", (r, g.point(lambda x: x // 2), b))
    small_images[2] = Image.merge("RGB", (r, g, b.point(lambda x: x // 2)))

    small_images[3] = small_images[3].filter(ImageFilter.BLUR)
    small_images[4] = small_images[4].filter(ImageFilter.SHARPEN)

    enhancer = ImageEnhance.Contrast(small_images[5])
    small_images[5] = enhancer.enhance(1.7)    # from 0 to 2

    for i in range(len(small_images)):
        blit_pil_image(screen, small_images[i], (20 + 160 * i, box_size + 40))


pygame.init()
pygame.display.set_caption('Кирпичи')
size = width, height = 1000, 600
screen = pygame.display.set_mode(size)

images_demo()
pygame.display.flip()
while pygame.event.wait().type != pygame.QUIT:
    pass
pygame.quit()