import pygame


def show_text(font, fontname, position):
    font_color = (50, 50, 50)
    text = font.render(f"Hello, pygame! ({fontname})", 1, font_color)
    screen.blit(text, position)


def fonts_demo():
    screen.fill((200, 200, 200))
    font_size = 24
    font = pygame.font.Font(None, font_size)
    show_text(font, 'default', (40, 40))

    print(pygame.font.get_fonts())
    font_names = ["Arial", "Georgia", "Comicsansms", "Candara"]
    for i in range(len(font_names)):
        font = pygame.font.SysFont(font_names[i], font_size)
        show_text(font, font_names[i], (40, 80 + 60 * i))
        font = pygame.font.SysFont(font_names[i], font_size, bold=True)   # жирный
        show_text(font, font_names[i] + ' bold', (340, 80 + 60 * i))
        font = pygame.font.SysFont(font_names[i], font_size, italic=True)   # курсив
        show_text(font, font_names[i] + ' italic', (740, 80 + 60 * i))
    font = pygame.font.Font(r"C:\Users\sns-h\PycharmProjects\pythonProject1\unicephalon.ttf", font_size)
    show_text(font, 'unicephalon', (40, 320))


"unicephalon"
pygame.init()
size = width, height = 1100, 500
screen = pygame.display.set_mode(size)

fonts_demo()

pygame.display.flip()
while pygame.event.wait().type != pygame.QUIT:
    pass
pygame.quit()
