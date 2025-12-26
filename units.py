import math
from config import *


class Tower:
    def __init__(self, x, y, t_type):
        self.x = x + TOWER_SIZE // 2
        self.y = y + TOWER_SIZE // 2
        self.type = t_type
        self.level = 1
        self.data = TOWERS[t_type][0]
        self.projectile_type = self.data.get('projectile_type', PROJECTILE_HOMING)
        self.damage = self.data['damage']
        self.range = self.data['range']
        self.fire_rate = self.data['fire_rate']
        self.fire_cooldown = 0
        self.splash_radius = self.data.get('splash_radius', 0)
        self.poison_duration = self.data.get('poison_duration', 0)
        self.poison_damage_per_sec = self.data.get('poison_damage_per_sec', 0)
        self.speed_boost = self.data.get('speed_boost', 0)
        self.slow_factor = self.data.get('slow_factor', 1.0)
        self.slow_duration = self.data.get('slow_duration', 0)
        self.spawned_unit = None

    def get_upgrade_cost(self):
        if self.level >= 4:
            return 0
        return TOWERS[self.type][self.level].get('upgrade_cost', 0)

    def upgrade(self):
        if self.level < 4:
            self.level += 1
            self.data = TOWERS[self.type][self.level - 1]
            self.damage = self.data['damage']
            self.range = self.data['range']
            self.fire_rate = self.data['fire_rate']
            self.splash_radius = self.data.get('splash_radius', 0)
            self.poison_duration = self.data.get('poison_duration', 0)
            self.poison_damage_per_sec = self.data.get('poison_damage_per_sec', 0)
            self.slow_factor = self.data.get('slow_factor', 1.0)
            self.slow_duration = self.data.get('slow_duration', 0)

    def find_target(self, enemies):
        if self.type in [TOWER_ARMY_BASE, TOWER_FROST]:
            targets = enemies
        else:
            targets = [e for e in enemies if isinstance(e, Enemy)]
        target = None
        max_progress_found = -1
        for e in targets:
            if math.hypot(e.x - self.x, e.y - self.y) <= self.range:
                if isinstance(e, StaticLavaUnit):
                    progress_to_compare = 0
                else:
                    if e.is_phantom and self.type != TOWER_SNIPER:
                        continue
                    progress_to_compare = e.path_progress
                if progress_to_compare > max_progress_found:
                    max_progress_found = progress_to_compare
                    target = e
        return target

    def fire(self, game, target):
        if self.fire_cooldown > 0: return
        if self.type == TOWER_ARMY_BASE:
            if self.spawned_unit is None:
                reverse_path = list(reversed(game.enemy_path))
                new_unit = AlliedUnit(self.x, self.y, reverse_path, self.data)
                game.allied_units.append(new_unit)
                self.spawned_unit = new_unit
                self.fire_cooldown = self.fire_rate
        else:
            p = Projectile.create(self.x, self.y, target, self.data)
            game.projectiles.append(p)
            self.fire_cooldown = self.fire_rate

    def update(self, game):
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        if self.type == TOWER_ARMY_BASE:
            if self.spawned_unit and (self.spawned_unit.health <= 0 or self.spawned_unit.reached_end):
                self.spawned_unit = None
            if self.spawned_unit is None and self.fire_cooldown <= 0:
                self.fire(game, None)
            return
        target = self.find_target(game.enemies + game.static_enemies)
        if target:
            self.fire(game, target)

    def draw(self, s):
        pygame.draw.circle(s, self.data['color'], (self.x, self.y), TOWER_SIZE // 2)
        pygame.draw.circle(s, BLACK, (self.x, self.y), TOWER_SIZE // 2, 2)
        if self.level > 1:
            lvl_txt = pygame.font.SysFont(None, 18).render(str(self.level), True, BLACK)
            s.blit(lvl_txt, lvl_txt.get_rect(center=(self.x + TOWER_SIZE // 2 - 5, self.y - TOWER_SIZE // 2 + 5)))

    def draw_range(self, s):
        color = (255, 255, 255, 100)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(overlay, color, (self.x, self.y), self.range)
        s.blit(overlay, (0, 0))
        pygame.draw.circle(s, WHITE, (self.x, self.y), self.range, 1)


class StaticLavaUnit:
    def __init__(self, x, y, hp):
        self.x = x
        self.y = y
        self.mhp = hp
        self.health = hp
        self.radius = ENEMY_SIZE // 2
        self.color = LAVA_COLOR
        self.timer = 5 * FPS

    def take_damage(self, damage, proj_type):
        self.health -= damage

    def update(self):
        self.timer -= 1
        if self.health <= 0 or self.timer <= 0:
            return True
        return False

    def draw(self, s):
        pygame.draw.circle(s, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(s, BLACK, (int(self.x), int(self.y)), self.radius, 1)
        hp_ratio = max(0, self.health / self.mhp)
        hb_width = self.radius * 2 + 4
        hb_x, hb_y = int(self.x - hb_width / 2), int(self.y - self.radius - 8)
        pygame.draw.rect(s, RED, (hb_x, hb_y, hb_width, 4))
        pygame.draw.rect(s, GREEN, (hb_x, hb_y, hb_width * hp_ratio, 4))
        pygame.draw.rect(s, BLACK, (hb_x, hb_y, hb_width, 4), 1)


class AlliedUnit:
    def __init__(self, tower_x, tower_y, path, data):
        self.path = path
        self.x, self.y = self.path[0]
        self.idx = 1
        self.mhp = data['unit_hp']
        self.health = self.mhp
        self.speed = data['unit_speed']
        self.color = DARK_GRAY
        self.radius = TOWER_SIZE // 3
        self.reached_end = False

    def take_damage(self, damage, proj_type):
        self.health -= damage

    def update(self, game):
        if self.health <= 0:
            return True
        enemy_to_collide = None
        for e in [en for en in game.enemies if isinstance(en, Enemy)]:
            if math.hypot(e.x - self.x, e.y - self.y) <= self.radius + e.radius:
                enemy_to_collide = e
                break
        if enemy_to_collide:
            enemy = enemy_to_collide
            if self.health >= enemy.health:
                self.health -= enemy.health
                game.money += enemy.reward
                game.enemies_killed_total += 1
                game.enemies.remove(enemy)
            else:
                enemy.health -= self.health
                self.health = 0
                return True
        if self.idx < len(self.path):
            tx, ty = self.path[self.idx]
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            if dist < self.speed:
                self.x, self.y = tx, ty
                self.idx += 1
            elif dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
        elif self.idx >= len(self.path):
            self.reached_end = True
            return True
        return False

    def draw(self, s):
        pygame.draw.circle(s, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(s, BLACK, (int(self.x), int(self.y)), self.radius, 1)
        hp_ratio = max(0, self.health / self.mhp)
        hb_width = self.radius * 2 + 4
        hb_x, hb_y = int(self.x - hb_width / 2), int(self.y - self.radius - 8)
        pygame.draw.rect(s, RED, (hb_x, hb_y, hb_width, 4))
        pygame.draw.rect(s, GREEN, (hb_x, hb_y, hb_width * hp_ratio, 4))
        pygame.draw.rect(s, BLACK, (hb_x, hb_y, hb_width, 4), 1)


class Enemy:
    def __init__(self, t, path):
        self.type = t
        self.path = path
        self.idx = 1
        self.x, self.y = self.path[0]
        data = ENEMIES[t]
        self.mhp = data['health']
        self.health = self.mhp
        self.initial_speed = data['speed']
        self.reward = data['reward']
        self.color = data['color']
        self.radius = ENEMY_SIZE // 2
        self.path_progress = 0
        self.reached_end = False
        self.poisoned = False
        self.p_timer = 0
        self.p_dmg = 0
        self.speed_boost = 0
        self.slow_factor = 1.0
        self.frozen_timer = 0
        self.is_phantom = data.get('is_phantom', False)
        self.spawns_on_death = data.get('spawns_on_death', False)
        self.spawned_hp = data.get('spawned_hp', 0)
        self.is_armored = data.get('is_armored', False)

    def current_speed(self):
        s = self.initial_speed + self.speed_boost

        if self.frozen_timer > 0:
            s *= self.slow_factor

        return max(0.1, s)

    def take_damage(self, damage, proj_type):
        if self.is_armored and proj_type != PROJECTILE_SPLASH:
            damage = max(1, damage - 5)

        if self.is_phantom and proj_type == PROJECTILE_HOMING and damage > 0:
            self.is_phantom = False

        self.health -= damage

    def update(self):
        if self.health <= 0:
            return True

        self.speed_boost = max(0, self.speed_boost - 0.005)

        if self.p_timer > 0:
            self.health -= self.p_dmg
            self.p_timer -= 1
            if self.health <= 0: return True

        if self.frozen_timer > 0:
            self.frozen_timer -= 1
            if self.frozen_timer <= 0:
                self.slow_factor = 1.0

        if self.idx >= len(self.path):
            self.reached_end = True
            return True

        tx, ty = self.path[self.idx]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        current_s = self.current_speed()

        if dist < current_s:
            self.path_progress += dist
            self.x, self.y = tx, ty
            self.idx += 1
            return False

        self.x += (dx / dist) * current_s
        self.y += (dy / dist) * current_s
        self.path_progress += current_s
        return False

    def apply_poison(self, dur, dmg):
        self.poisoned = True
        self.p_timer = dur
        self.p_dmg = dmg / FPS

    def apply_speed_boost(self, boost):
        self.speed_boost = max(self.speed_boost, boost)

    def apply_slow(self, factor, duration):
        if factor < self.slow_factor:
            self.slow_factor = factor
        if factor <= self.slow_factor:
            self.frozen_timer = duration

    def draw(self, s):
        color = self.color

        if self.is_phantom:
            temp_surface = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
            temp_surface.fill((255, 255, 255, 0))
            pygame.draw.circle(temp_surface, (self.color[0], self.color[1], self.color[2], 50),
                               (ENEMY_SIZE // 2, ENEMY_SIZE // 2), self.radius)
            s.blit(temp_surface, (int(self.x - self.radius), int(self.y - self.radius)))
            return

        pygame.draw.circle(s, color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(s, BLACK, (int(self.x), int(self.y)), self.radius, 1)

        hp_ratio = max(0, self.health / self.mhp)
        hb_width = self.radius * 2 + 4
        hb_x, hb_y = int(self.x - hb_width / 2), int(self.y - self.radius - 8)

        pygame.draw.rect(s, RED, (hb_x, hb_y, hb_width, 4))
        pygame.draw.rect(s, GREEN, (hb_x, hb_y, hb_width * hp_ratio, 4))
        pygame.draw.rect(s, BLACK, (hb_x, hb_y, hb_width, 4), 1)

        status_x = int(self.x - self.radius)
        status_y = int(self.y + self.radius + 2)

        if self.poisoned and self.p_timer > 0:
            pygame.draw.circle(s, PURPLE, (status_x, status_y), 3)
            status_x += 8
        if self.frozen_timer > 0 and self.slow_factor < 1.0:
            pygame.draw.circle(s, LIGHT_BLUE, (status_x, status_y), 3)
            status_x += 8
        if self.speed_boost > 0:
            pygame.draw.circle(s, YELLOW, (status_x, status_y), 3)


class Projectile:
    def __init__(self, x, y, target, data, proj_type):
        self.x = x
        self.y = y
        self.target = target
        self.proj_type = proj_type
        self.damage = data['damage']
        self.color = BLACK
        self.radius = 4
        self.speed = 10
        self.splash_radius = data.get('splash_radius', 0)
        self.poison_duration = data.get('poison_duration', 0)
        self.poison_damage_per_sec = data.get('poison_damage_per_sec', 0)
        self.slow_factor = data.get('slow_factor', 1.0)
        self.slow_duration = data.get('slow_duration', 0)
        self.speed_boost = data.get('speed_boost', 1.0)
        self.mhp = 1

    @staticmethod
    def create(x, y, target, data):
        proj_type = data['projectile_type']

        if proj_type == PROJECTILE_SPLASH:
            return SplashProjectile(x, y, target, data)
        elif proj_type == PROJECTILE_FLAME:
            return FlameProjectile(x, y, target, data)
        elif proj_type == PROJECTILE_POISON:
            return PoisonProjectile(x, y, target, data)
        elif proj_type == PROJECTILE_FROST:
            return FrostProjectile(x, y, target, data)
        elif proj_type == PROJECTILE_ARMY_BASE:
            return ArmyBaseProjectile(x, y, target, data)
        else:
            return HomingProjectile(x, y, target, data)

    def update(self, enemies):
        if self.target is None or self.target.health <= 0 or (
                isinstance(self.target, Enemy) and self.target.reached_end):
            self.find_new_target(enemies)

        if self.target is None:
            return True

        dx, dy = self.target.x - self.x, self.target.y - self.y
        d = math.hypot(dx, dy)

        if d <= self.speed + 15 + self.radius + 4:
            self.x, self.y = self.target.x, self.target.y
            self.on_hit(enemies)
            return True

        self.x += (dx / d) * self.speed
        self.y += (dy / d) * self.speed
        return False

    def find_new_target(self, enemies):
        min_dist = float('inf')
        new_target = None
        for e in enemies:
            d = math.hypot(e.x - self.x, e.y - self.y)
            if d < min_dist:
                min_dist = d
                new_target = e
        self.target = new_target

    def on_hit(self, e):
        if self.target:
            self.target.take_damage(self.damage, self.proj_type)

    def draw(self, s):
        pygame.draw.circle(s, self.color, (int(self.x), int(self.y)), self.radius)


class HomingProjectile(Projectile):
    def __init__(self, x, y, t, d):
        super().__init__(x, y, t, d, PROJECTILE_HOMING)
        self.speed = 20
        self.color = BLUE
        self.radius = 6


class SplashProjectile(Projectile):
    def __init__(self, x, y, t, d):
        super().__init__(x, y, t, d, PROJECTILE_SPLASH)
        self.speed = 8
        self.color = ORANGE
        self.radius = 8

    def on_hit(self, enemies):
        if not self.target: return

        self.target.take_damage(self.damage, self.proj_type)

        splash_damage = self.damage // 2

        for e in enemies:
            if math.hypot(e.x - self.target.x, e.y - self.target.y) <= self.splash_radius and e != self.target:
                e.take_damage(splash_damage, self.proj_type)


class FlameProjectile(Projectile):
    def __init__(self, x, y, t, d):
        super().__init__(x, y, t, d, PROJECTILE_FLAME)
        self.speed = 25
        self.color = RED
        self.radius = 5
        self.duration = 5

    def update(self, enemies):
        if self.duration <= 0: return True
        self.duration -= 1

        for e in [en for en in enemies if isinstance(en, Enemy)]:
            if math.hypot(e.x - self.x, e.y - self.y) <= self.splash_radius:
                e.take_damage(self.damage, self.proj_type)
                e.apply_speed_boost(self.speed_boost)

        if self.target and self.target.health > 0 and not (isinstance(self.target, Enemy) and self.target.reached_end):
            dx, dy = self.target.x - self.x, self.target.y - self.y
            d = math.hypot(dx, dy)
            if d > 0:
                self.x += (dx / d) * self.speed
                self.y += (dy / d) * self.speed

        return False

    def on_hit(self, e):
        pass


class PoisonProjectile(Projectile):
    def __init__(self, x, y, t, d):
        super().__init__(x, y, t, d, PROJECTILE_POISON)
        self.speed = 15
        self.color = PURPLE
        self.radius = 7

    def on_hit(self, e):
        if self.target and isinstance(self.target, Enemy):
            self.target.take_damage(self.damage, self.proj_type)
            self.target.apply_poison(self.poison_duration, self.poison_damage_per_sec * self.poison_duration / FPS)


class FrostProjectile(Projectile):
    def __init__(self, x, y, t, d):
        super().__init__(x, y, t, d, PROJECTILE_FROST)
        self.speed = 10
        self.color = LIGHT_BLUE
        self.radius = 8

    def on_hit(self, e):
        if self.target and isinstance(self.target, Enemy):
            self.target.take_damage(self.damage, self.proj_type)
            self.target.apply_slow(self.slow_factor, self.slow_duration)


class ArmyBaseProjectile(Projectile):
    def __init__(self, x, y, t, d):
        super().__init__(x, y, t, d, PROJECTILE_ARMY_BASE)
        self.speed = 10
        self.color = DARK_GRAY
        self.radius = 5
        self.hp = 100
        self.mhp = 100
        self.hp_to_damage = 0

    def update(self, enemies):
        return True

    def draw(self, s):
        pass



