import pygame

def main():
    pygame.init()

    white = 255, 255, 255
    black = 0, 0, 0

    screen = pygame.display.set_mode((1000, 400))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Pygame")

    font = pygame.font.Font('freesansbold.ttf', 32)
    screen.fill(white)
    buf = ''

    while True:
        clock.tick(1000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                screen.fill(white)
                buf += event.unicode
                key_pressed = font.render(buf, True, black)
                screen.blit(key_pressed, (100, 160))
                # print(f'keydown {event.unicode}')

        pygame.display.update()

if __name__ == '__main__':
    main()