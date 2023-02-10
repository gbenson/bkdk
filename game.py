import pygame

pygame.init()

reference = pygame.image.load("reference.png")

screen = pygame.display.set_mode(reference.get_size())

reference.convert()  # Speed up Surface.blit
reference.set_alpha(64)  # 25% opaque

clock = pygame.time.Clock()

while True:
    # Process player inputs.
    for event in pygame.event.get():
        if (event.type == pygame.KEYUP
            and event.key in (pygame.K_ESCAPE,
                              pygame.K_q)):
            event = pygame.event.Event(pygame.QUIT)
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

    # Do logical updates here.
    # ...

    # Render the graphics.
    screen.fill("purple")  # Fill the display with a solid color
    pygame.Surface.blit(screen, reference, (0, 0))

    pygame.display.flip()  # Refresh on-screen display
    clock.tick(60)         # wait until next frame (at 60 FPS)
