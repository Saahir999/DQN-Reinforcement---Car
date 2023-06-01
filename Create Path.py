import pygame
import random

pygame.init()
clock = pygame.time.Clock()
SCREEN = pygame.display.set_mode((1244, 1016))
SCREEN.fill((2, 105, 31))
pygame.display.flip()
is_Pressed = False
rnam = random.randint(0, 100000)
size = 40

def draw_circle(center):
    pygame.draw.circle(SCREEN, (105, 105, 105), center, size)
    pygame.display.flip()


while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

        if event.type == pygame.MOUSEWHEEL:
            size += event.y
            print(size)

        if event.type == pygame.MOUSEBUTTONDOWN:
            is_Pressed = True

        if event.type == pygame.MOUSEBUTTONUP:
            is_Pressed = False

        if event.type == pygame.MOUSEMOTION:

            if is_Pressed:
                x, y = pygame.mouse.get_pos()
                draw_circle((x, y))

        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_s]:
            pygame.image.save(SCREEN, "track" + str(rnam) + ".png")
        if user_input[pygame.K_r]:
            SCREEN.fill((2, 105, 31))
            pygame.display.flip()
