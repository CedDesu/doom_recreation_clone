from sprite_object import *
from random import randint, random


class NPC(AnimatedSprite):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_images = self.get_images(self.path + '/attack')
        self.death_images = self.get_images(self.path + '/death')
        self.idle_images = self.get_images(self.path + '/idle')
        self.pain_images = self.get_images(self.path + '/pain')
        self.walk_images = self.get_images(self.path + '/walk')

        self.attack_dist = randint(3, 6)
        self.speed = 0.03
        self.size = 20
        self.health = 100
        self.attack_damage = 10
        self.accuracy = 0.15
        self.alive = True
        self.pain = False
        self.ray_cast_value = False
        self.frame_counter = 0
        self.player_search_trigger = False

        # Rename position attributes if not already handled in parent
        self.pos_x = pos[0]
        self.pos_y = pos[1]

    def update(self):
        self.check_animation_time()
        self.get_sprite()
        self.run_logic()

    def check_wall(self, var_x, var_y):
        return (var_x, var_y) not in self.game.map.world_map

    def check_wall_collision(self, delta_x, delta_y):
        if self.check_wall(int(self.pos_x + delta_x * self.size), int(self.pos_y)):
            self.pos_x += delta_x
        if self.check_wall(int(self.pos_x), int(self.pos_y + delta_y * self.size)):
            self.pos_y += delta_y

    def movement(self):
        next_pos = self.game.pathfinding.get_path(self.map_pos, self.game.player.map_pos)
        next_x, next_y = next_pos

        if next_pos not in self.game.object_handler.npc_positions:
            angle = math.atan2(next_y + 0.5 - self.pos_y, next_x + 0.5 - self.pos_x)
            delta_x = math.cos(angle) * self.speed
            delta_y = math.sin(angle) * self.speed
            self.check_wall_collision(delta_x, delta_y)

    def attack(self):
        if self.animation_trigger:
            self.game.sound.npc_shot.play()
            if random() < self.accuracy:
                self.game.player.get_damage(self.attack_damage)

    def animate_death(self):
        if not self.alive:
            if self.game.global_trigger and self.frame_counter < len(self.death_images) - 1:
                self.death_images.rotate(-1)
                self.image = self.death_images[0]
                self.frame_counter += 1

    def animate_pain(self):
        self.animate(self.pain_images)
        if self.animation_trigger:
            self.pain = False

    def check_hit_in_npc(self):
        if self.ray_cast_value and self.game.player.shot:
            if HALF_WIDTH - self.sprite_half_width < self.screen_x < HALF_WIDTH + self.sprite_half_width:
                self.game.sound.npc_pain.play()
                self.game.player.shot = False
                self.pain = True
                self.health -= self.game.weapon.damage
                self.check_health()

    def check_health(self):
        if self.health < 1:
            self.alive = False
            self.game.sound.npc_death.play()

    def run_logic(self):
        if self.alive:
            self.ray_cast_value = self.ray_cast_player_npc()
            self.check_hit_in_npc()

            if self.pain:
                self.animate_pain()
            elif self.ray_cast_value:
                self.player_search_trigger = True

                if self.dist < self.attack_dist:
                    self.animate(self.attack_images)
                    self.attack()
                else:
                    self.animate(self.walk_images)
                    self.movement()
            elif self.player_search_trigger:
                self.animate(self.walk_images)
                self.movement()
            else:
                self.animate(self.idle_images)
        else:
            self.animate_death()

    @property
    def map_pos(self):
        return int(self.pos_x), int(self.pos_y)

    def ray_cast_player_npc(self):
        if self.game.player.map_pos == self.map_pos:
            return True

        wall_dist_vertical, wall_dist_horizontal = 0, 0
        player_dist_vertical, player_dist_horizontal = 0, 0

        origin_x, origin_y = self.game.player.pos
        map_x, map_y = self.game.player.map_pos

        ray_angle = self.theta
        sin_angle = math.sin(ray_angle)
        cos_angle = math.cos(ray_angle)

        # Horizontal ray
        hor_y, step_y = (map_y + 1, 1) if sin_angle > 0 else (map_y - 1e-6, -1)
        depth_horizontal = (hor_y - origin_y) / sin_angle
        hor_x = origin_x + depth_horizontal * cos_angle

        delta_depth = step_y / sin_angle
        delta_x = delta_depth * cos_angle

        for i in range(MAX_DEPTH):
            tile_horizontal = int(hor_x), int(hor_y)
            if tile_horizontal == self.map_pos:
                player_dist_horizontal = depth_horizontal
                break
            if tile_horizontal in self.game.map.world_map:
                wall_dist_horizontal = depth_horizontal
                break
            hor_x += delta_x
            hor_y += step_y
            depth_horizontal += delta_depth

        # Vertical ray
        vert_x, step_x = (map_x + 1, 1) if cos_angle > 0 else (map_x - 1e-6, -1)
        depth_vertical = (vert_x - origin_x) / cos_angle
        vert_y = origin_y + depth_vertical * sin_angle

        delta_depth = step_x / cos_angle
        delta_y = delta_depth * sin_angle

        for i in range(MAX_DEPTH):
            tile_vertical = int(vert_x), int(vert_y)
            if tile_vertical == self.map_pos:
                player_dist_vertical = depth_vertical
                break
            if tile_vertical in self.game.map.world_map:
                wall_dist_vertical = depth_vertical
                break
            vert_x += step_x
            vert_y += delta_y
            depth_vertical += delta_depth

        player_distance = max(player_dist_vertical, player_dist_horizontal)
        wall_distance = max(wall_dist_vertical, wall_dist_horizontal)

        return (0 < player_distance < wall_distance) or not wall_distance

    def draw_ray_cast(self):
        pg.draw.circle(self.game.screen, 'red', (100 * self.pos_x, 100 * self.pos_y), 15)
        if self.ray_cast_player_npc():
            pg.draw.line(
                self.game.screen, 'orange',
                (100 * self.game.player.x, 100 * self.game.player.y),
                (100 * self.pos_x, 100 * self.pos_y), 2
            )


class SoldierNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/soldier/0.png', pos=(10.5, 5.5),
                 scale=0.6, shift=0.38, animation_time=180):
        super().__init__(game, path, pos, scale, shift, animation_time)


class CacoDemonNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/caco_demon/0.png', pos=(10.5, 6.5),
                 scale=0.7, shift=0.27, animation_time=250):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 1.0
        self.health = 150
        self.attack_damage = 25
        self.speed = 0.05
        self.accuracy = 0.35


class CyberDemonNPC(NPC):
    def __init__(self, game, path='resources/sprites/npc/cyber_demon/0.png', pos=(11.5, 6.0),
                 scale=1.0, shift=0.04, animation_time=210):
        super().__init__(game, path, pos, scale, shift, animation_time)
        self.attack_dist = 6
        self.health = 350
        self.attack_damage = 15
        self.speed = 0.055
        self.accuracy = 0.25