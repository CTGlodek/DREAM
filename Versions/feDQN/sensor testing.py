import pygame
from sensor import *
from target import *

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

target = Target((screen.get_width() / 2)+5, 1)

#target = Target(((screen.get_width() / 2)-5, 0, 0, 1))
target_pos_1 = pygame.Vector2(screen.get_width() / 2, screen.get_height())

t_1_dir = 1 # 1 for postive direction, -1 for negative


# Blit everything to the screen
#screen.blit(background, (0, 0))

sensor_test = Sensor(screen.get_width() / 2, screen.get_height() / 2, fov=90)
sensor_test_1 = Sensor(screen.get_width() / 4, screen.get_height() / 4, active=False) # set to inactive


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    pygame.draw.circle(screen, "red", player_pos, 30)
    #pygame.draw.circle(screen, "blue", target_pos, 30)
    #pygame.draw.circle(screen, "green", target_pos_1, 20)

    target.move()
    sensor_test.update_sensor_fov([target])
    target.draw_target(screen)
    sensor_test.draw_sensors(screen)
    sensor_test_1.draw_sensors(screen)

    distance = sensor_test.position.distance_to(target.position)
    #angle = sensor_test.position.angle_to(player_pos) % 360
    angle = player_pos.angle_to(sensor_test.position) % 360
    angle_1 = math.degrees(math.atan2(player_pos.y - sensor_test.position.y, player_pos.x - sensor_test.position.x)) % 360 # works
    angle_2 = sensor_test.angle

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:
        player_pos.x += 300 * dt

    if target_pos_1.y >= screen.get_height(): 
        t_1_dir = 1
    if target_pos_1.y <= 0: 
        t_1_dir = -1

    target_pos_1.y = target_pos_1.y - t_1_dir
    


    # Display some text
    font = pygame.font.Font(None, 36)
    text = font.render(str(distance), 1, (10, 10, 10)) # display the distance between each target
    textpos = text.get_rect()
    textpos.centerx = screen.get_rect().centerx
    screen.blit(text, textpos)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()