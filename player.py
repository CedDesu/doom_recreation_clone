from settings import *
import pygame as pg
import math


class Player:
    def __init__(self, game):
        self.game = game
        self.pos_x, self.pos_y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.shot = False
        self.health = PLAYER_MAX_HEALTH
        self.rel = 0
        self.health_recovery_delay = 700
        self.time_prev = pg.time.get_ticks()
        self.diag_move_corr = 1 / math.sqrt(2)

    def recover_health(self):
        if self.check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1

    def check_health_recovery_delay(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time_prev > self.health_recovery_delay:
            self.time_prev = time_now
            return True

    def check_game_over(self):
        if self.health < 1:
            self.game.object_renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def get_damage(self, damage):
        self.health -= damage
        self.game.object_renderer.player_damage()
        self.game.sound.player_pain.play()
        self.check_game_over()

    def single_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                self.game.sound.shotgun.play()
                self.shot = True
                self.game.weapon.reloading = True

    def movement(self):
        sin_angle = math.sin(self.angle)
        cos_angle = math.cos(self.angle)
        delta_x, delta_y = 0, 0
        speed = PLAYER_SPEED * self.game.delta_time
        speed_sin = speed * sin_angle
        speed_cos = speed * cos_angle

        keys = pg.key.get_pressed()
        num_keys_pressed = -1
        if keys[pg.K_w]:
            num_keys_pressed += 1
            delta_x += speed_cos
            delta_y += speed_sin
        if keys[pg.K_s]:
            num_keys_pressed += 1
            delta_x += -speed_cos
            delta_y += -speed_sin
        if keys[pg.K_a]:
            num_keys_pressed += 1
            delta_x += speed_sin
            delta_y += -speed_cos
        if keys[pg.K_d]:
            num_keys_pressed += 1
            delta_x += -speed_sin
            delta_y += speed_cos

        if num_keys_pressed:
            delta_x *= self.diag_move_corr
            delta_y *= self.diag_move_corr

        self.check_wall_collision(delta_x, delta_y)

        self.angle %= math.tau

    def check_wall(self, tile_x, tile_y):
        return (tile_x, tile_y) not in self.game.map.world_map

    def check_wall_collision(self, delta_x, delta_y):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.pos_x + delta_x * scale), int(self.pos_y)):
            self.pos_x += delta_x
        if self.check_wall(int(self.pos_x), int(self.pos_y + delta_y * scale)):
            self.pos_y += delta_y

    def draw(self):
        pg.draw.line(
            self.game.screen,
            'yellow',
            (self.pos_x * 100, self.pos_y * 100),
            (
                self.pos_x * 100 + WIDTH * math.cos(self.angle),
                self.pos_y * 100 + WIDTH * math.sin(self.angle)
            ),
            2
        )
        pg.draw.circle(
            self.game.screen,
            'green',
            (self.pos_x * 100, self.pos_y * 100),
            15
        )

    def mouse_control(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        if mouse_x < MOUSE_BORDER_LEFT or mouse_x > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time

    def update(self):
        self.movement()
        self.mouse_control()
        self.recover_health()

    @property
    def x(self):
        return self.pos_x

    @property
    def y(self):
        return self.pos_y

    @property
    def pos(self):
        return self.pos_x, self.pos_y

    @property
    def map_pos(self):
        return int(self.pos_x), int(self.pos_y)
