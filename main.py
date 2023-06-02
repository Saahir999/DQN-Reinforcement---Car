import numpy as np
import pygame
import os
import math
import sys
from AI import DeepQLearn as Dqn
from matplotlib import pyplot

# TODO: implement jerk to give variable accel with opposing jerk similar to velocity for better simulation (?)
# TODO: implement greater goals like a destination and checkpoint rewards
# TODO: feed self.angle , give penalty for turning, pass differential change in radar,
#  lower degree of rotation per decision, make rewards cumulative, make some radars more important by rewarding based on their inputs

MANUAL = False
show_radar = True
show_hitbox = False
READY = False

SCREEN_WIDTH = 1244
SCREEN_HEIGHT = 1016
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
NORMAL = os.path.join("Images", "car.png")
BROKEN = os.path.join("Images", "broken_car.png")
TRACK = pygame.image.load(os.path.join("Images", "track.png"))

Agent = Dqn(6, 3, 0.8)
action2rotation = [0, -20, 20]
# Straight Left Right

last_reward = 0
scores = []
count = 100000
drop_count = 0
lap_count = 0
action = 0

x, y = 0, 0
collision_point_left: list[int]
collision_point_left_rear: list[int]
collision_point_right: list[int]
collision_point_right_rear: list[int]

start_x = 0
start_y = 0
end_x = 0
end_y = 0

dist = 0
last_dist = 0


# -(210,247)------------(915,240)
# -                              -
# -                              -
# -                              -(1011, 700)
# -(209, 793)-------(620,800)------


class Car(pygame.sprite.Sprite):
    def __init__(self):

        global collision_point_left
        global collision_point_left_rear
        global collision_point_right
        global collision_point_right_rear

        super().__init__()

        self.accel = pygame.math.Vector2(0, 0)
        self.original_image = pygame.image.load(NORMAL)
        self.broken_image = pygame.image.load(BROKEN)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(490, 820))
        self.origin = self.rect
        self.vel_vector = pygame.math.Vector2(0, 0)
        self.angle = 0
        self.rotation_vel = 5
        self.direction = 0
        self.alive = True
        self.radars = []
        self.friction = pygame.math.Vector2(0, 0)
        self.drive_state = True

        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * 40),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * 40)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * 40),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * 40)]

        collision_point_left_rear = [int(self.rect.center[0] - math.cos(math.radians(self.angle - 18)) * 40),
                                     int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * 40)]
        collision_point_right_rear = [int(self.rect.center[0] - math.cos(math.radians(self.angle - 18)) * 40),
                                      int(self.rect.center[1] + math.sin(math.radians(self.angle - 18)) * 40)]

        Agent.load("3sftmax6inppart2_brain.pth")

    def update(self):

        global last_reward
        global scores
        global car
        global count
        global lap_count
        global dist, last_dist
        global action

        self.radars.clear()
        self.drive()
        self.rotate(0)

        erase_radar = SCREEN
        if not show_radar:
            erase_radar = pygame.Surface((200, 200), pygame.SRCALPHA)
        for radar_angle in (-60, -30, 0, 30, 60, 180):
            self.radar(radar_angle, erase_radar)
            if not show_radar:
                SCREEN.blit(erase_radar, self.image.get_rect())

        self.collision()
        last_dist = dist
        dist = self.distance(bool(lap_count % 2))
        senses = self.data()

        # last_reward -= ((senses[0] - 140) * (senses[0]) / 19600) / 2 + ((senses[4] - 140) * (senses[4]) / 19600) / 2

        if not MANUAL and READY:
            scores.append(Agent.score())
            print(Agent.score())

            # print(last_reward)
            last_reward = 0 if action == 0 else -1

            if not self.alive:
                last_reward += -10
                self.alive = True

            if dist <= 130:
                last_reward += 2
                lap_count += 1
                print("https://GOAL_TOGGLE")
                last_dist = 10000

            if last_dist > dist:
                last_reward += 0.1

            if abs(self.rect.centerx - self.origin.centerx) + abs(self.rect.centery - self.origin.centery) > 0:
                last_reward += 0.01
                self.origin = self.rect

            else:
                last_reward += -0.15

            action = Agent.update(last_reward, senses)
            self.rotate(action2rotation[action], auto=False)
            # print(action)
            if action == 0:
                car.sprite.accel = pygame.math.Vector2(math.cos(math.radians(car.sprite.angle)) * 0.5,
                                                       math.sin(math.radians(car.sprite.angle)) * -0.5)

            count -= 1

            if count == 0:
                count = 100000
                Agent.save()
                pyplot.plot(scores)

    def redraw(self, broken=0):
        self.image = pygame.image.load(NORMAL) if broken == 0 else pygame.image.load(BROKEN)
        self.rotate(0, broken=broken)
        pygame.display.flip()

    def drive(self):

        # Dampener of velocity and directional accel

        if self.vel_vector.magnitude() != 0:
            if self.drive_state:
                self.friction = self.vel_vector * 0.4
            else:
                self.friction = self.vel_vector * 0.09

        self.vel_vector += self.accel - self.friction
        self.rect.center += self.vel_vector * 6
        self.accel = pygame.math.Vector2(0, 0)

    def collision(self):

        global x, y
        global collision_point_left
        global collision_point_left_rear
        global collision_point_right
        global collision_point_right_rear

        # car body length
        length = 40
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

        collision_point_left_rear = [int(self.rect.center[0] - math.cos(math.radians(self.angle + 18)) * length),
                                     int(self.rect.center[1] + math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_right_rear = [int(self.rect.center[0] - math.cos(math.radians(self.angle - 18)) * length),
                                      int(self.rect.center[1] + math.sin(math.radians(self.angle - 18)) * length)]

        # Wall on Collision
        if SCREEN.get_at(collision_point_right) == pygame.Color(2, 105, 31, 255) \
                or SCREEN.get_at(collision_point_left) == pygame.Color(2, 105, 31, 255):
            self.alive = False
            # self.image = pygame.image.load(os.path.join("Images", "broken_car.png"))
            # pygame.display.flip()
            self.rect.center = (x, y)
            self.redraw(broken=1)
            # print(self.alive)

            # # Reset everything
            # self.rect.center = (490, 820)
            # self.origin = self.rect
            # self.vel_vector = pygame.math.Vector2(0, 0)
            # self.accel = pygame.math.Vector2(0, 0)
            # self.friction = pygame.math.Vector2(0, 0)
            # self.angle = 0

        if self.alive:
            x, y = self.rect.centerx, self.rect.centery

        # Collision Points or the hitbox of the car is only its front and back edge
        # which is further simplified to its headlights and rear lights
        erase_trash = SCREEN
        if not show_hitbox:
            erase_trash = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)
        pygame.draw.circle(erase_trash, (0, 255, 255, 0), collision_point_right, 4)
        pygame.draw.circle(erase_trash, (0, 255, 255, 0), collision_point_left, 4)
        pygame.draw.circle(erase_trash, (0, 255, 255, 0), collision_point_left_rear, 4)
        pygame.draw.circle(erase_trash, (0, 255, 255, 0), collision_point_right_rear, 4)
        if not show_hitbox:
            SCREEN.blit(erase_trash, self.image.get_rect())

    def rotate(self, rotate_by, auto=True, broken=0):

        global collision_point_left
        global collision_point_left_rear
        global collision_point_right
        global collision_point_right_rear

        if auto:
            if self.drive_state and self.direction == 1:
                self.angle -= self.rotation_vel
                self.vel_vector.rotate_ip(self.rotation_vel)
            if self.drive_state and self.direction == -1:
                self.angle += self.rotation_vel
                self.vel_vector.rotate_ip(-self.rotation_vel)
        else:
            self.angle += rotate_by / 4
            self.vel_vector.rotate_ip(rotate_by)

        # if SCREEN.get_at(collision_point_right) == pygame.Color(2, 105, 31, 255) \
        #         or SCREEN.get_at(collision_point_left) == pygame.Color(2, 105, 31, 255) \
        #         or SCREEN.get_at(collision_point_left_rear) == pygame.Color(2, 105, 31, 255) \
        #         or SCREEN.get_at(collision_point_right_rear) == pygame.Color(2, 105, 31, 255):
        #     self.alive = False
        #
        #     self.rect.center = (x, y)

        self.image = pygame.transform.rotozoom(self.original_image if broken == 0 else self.broken_image, self.angle,
                                               0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

        self.accel = self.accel.magnitude() * pygame.math.Vector2(math.cos(math.radians(self.angle)),
                                                                  math.sin(math.radians(self.angle)) * -1)

    def radar(self, radar_angle, eraser):
        length = 0
        rx = int(self.rect.center[0])
        ry = int(self.rect.center[1])

        while not SCREEN.get_at((rx, ry)) == pygame.Color(2, 105, 31, 255) and length < 200:
            length += 1
            rx = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length)
            ry = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)

        # Draw Radar
        pygame.draw.line(eraser, (255, 255, 255, 255), self.rect.center, (rx, ry), 1)
        pygame.draw.circle(eraser, (0, 255, 0, 0), (rx, ry), 3)

        distance = int(math.sqrt(math.pow(self.rect.center[0] - rx, 2)
                                 + math.pow(self.rect.center[1] - ry, 2)))

        self.radars.append([radar_angle, distance])

    def distance(self, odd=True):
        gx = start_x if odd is True else end_x
        gy = start_y if odd is True else end_y
        return np.sqrt((gx - self.rect.centerx) ** 2 + (gy - self.rect.centery) ** 2)

    def data(self):
        # input for AI, the angles do not matter to it since all points must be collision free in any case
        input = [0, 0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])

        return input


# manual
car = pygame.sprite.GroupSingle(Car())


def start():
    global drop_count
    global READY
    global start_x, start_y
    global end_x, end_y
    global dist, last_dist

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                print(pygame.mouse.get_pos())
                print("start=" + str((start_x, start_y)))
                print("end=" + str((end_x, end_y)))
                drop_count += 1
                if drop_count == 1:
                    start_x, start_y = pygame.mouse.get_pos()
                    car.sprite.rect.center = (start_x, start_y)
                if drop_count == 2:
                    endx, end_y = pygame.mouse.get_pos()
                    dist = np.sqrt((start_x - end_x) ** 2 - (start_y - end_y) ** 2)
                    READY = True
                if drop_count > 3:
                    drop_count = 3

        SCREEN.blit(TRACK, (0, 0))

        user_input = pygame.key.get_pressed()

        if user_input[pygame.K_s]:
            Agent.save()
        if user_input[pygame.K_p]:
            print(pyplot.plot(scores))

        if MANUAL:
            # User input
            user_input = pygame.key.get_pressed()
            if sum(pygame.key.get_pressed()) <= 1:
                # car.sprite.drive_state = False
                car.sprite.direction = 0
            # Drive
            if user_input[pygame.K_w]:
                car.sprite.accel = pygame.math.Vector2(math.cos(math.radians(car.sprite.angle)) * 0.5,
                                                       math.sin(math.radians(car.sprite.angle)) * -0.5)
                # car.sprite.drive_state = True
            # if user_input[pygame.K_s]:
            #     car.sprite.stop = True

            # Steer
            if user_input[pygame.K_d]:
                car.sprite.direction = 1
            if user_input[pygame.K_a]:
                car.sprite.direction = -1

        # Handover Control to AI

        # Update
        car.draw(SCREEN)

        car.sprite.update()

        # rotate by action2rotation and don't keep pressing w

        pygame.display.update()


start()
