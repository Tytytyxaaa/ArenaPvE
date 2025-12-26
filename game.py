import pygame
import sys
import math
from ArenaPvE.config import *
from ArenaPvE.units import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defence")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "MENU"
        self.font = pygame.font.SysFont(None, 36)
        self.ui_font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 20)
        self.title_font = pygame.font.SysFont(None, 80)
        self.menu_font = pygame.font.SysFont(None, 26)
        self.all_tower_types = [TOWER_SNIPER, TOWER_MORTAR, TOWER_ARMY_BASE, TOWER_POISON, TOWER_FLAMETHROWER, TOWER_FROST]
        self.NUM_SLOTS = 3
        self.chosen_tower_types = [TOWER_SNIPER, TOWER_MORTAR, TOWER_FROST]
        self.selected_tower_on_map = None
        self.btn_upgrade = None
        self.btn_sell = None
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        self.btn_start = pygame.Rect(center_x - 100, center_y - 120, 200, 60)
        self.btn_difficulty_select = pygame.Rect(center_x - 100, center_y - 40, 200, 60)
        self.btn_tower_select = pygame.Rect(center_x - 100, center_y + 40, 200, 60)
        self.tower_slot_rects = []
        self.btn_quit = pygame.Rect(center_x - 100, center_y + 120, 200, 60)
        self.btn_resume = pygame.Rect(center_x - 100, center_y - 40, 200, 60)
        self.btn_to_menu = pygame.Rect(center_x - 100, center_y + 40, 200, 60)
        self.game_over_stats = {}
        self.btn_game_over_to_menu = pygame.Rect(center_x - 150, center_y + 100, 300, 60)
        self.victory_stats = {}
        self.btn_victory_to_menu = pygame.Rect(center_x - 150, center_y + 100, 300, 60)
        self.PANEL_HEIGHT = 100
        self.PANEL_Y = SCREEN_HEIGHT - self.PANEL_HEIGHT
        self.tower_buttons = []
        self.setup_game_ui()
        self.chosen_slot_rects = []
        self.all_tower_rects = []
        self.btn_selection_back = pygame.Rect(center_x - 100, SCREEN_HEIGHT - 80, 200, 60)
        self.difficulty = DIFFICULTY_MEDIUM
        self.difficulty_buttons = self.setup_difficulty_buttons(center_x, center_y)
        self.reset_game()

    def setup_difficulty_buttons(self, center_x, center_y):
        btns = []
        keys = sorted(DIFFICULTY_SETTINGS.keys())
        total_height = len(keys) * 80 + (len(keys) - 1) * 20
        start_y = center_y - total_height // 2
        for i, key in enumerate(keys):
            y = start_y + i * 100
            rect = pygame.Rect(center_x - 150, y, 300, 80)
            btns.append({'rect': rect, 'id': key, 'data': DIFFICULTY_SETTINGS[key]})
        return btns

    def reset_game(self):
        settings = DIFFICULTY_SETTINGS.get(self.difficulty, DIFFICULTY_SETTINGS[DIFFICULTY_MEDIUM])
        self.wave_number = 0
        self.money = settings.get('money', 500)
        self.lives = settings.get('lives', 20)
        self.spawn_queue = []
        self.spawn_timer = 0
        self.SPAWN_DELAY = 30
        self.next_wave_timer = -1
        self.WAVE_DELAY_SEC = 5
        self.enemy_path = settings['path']
        self.waves = settings['waves']
        self.enemies_killed_total = 0
        self.selected_tower_type = None
        self.hovered_cell = None
        self.pending_tower_pos = (0, 0)
        self.pending_tower_type = None
        self.selected_tower_on_map = None
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.allied_units = []
        self.static_enemies = []

    def setup_game_ui(self, ):
        self.tower_buttons = []
        button_width = 80
        button_height = 80
        margin = 20
        start_x = 20
        for i, t_type in enumerate(self.chosen_tower_types):
            if t_type:
                rect = pygame.Rect(start_x + (button_width + margin) * i, self.PANEL_Y + 10, button_width,
                                   button_height)
                self.tower_buttons.append({'rect': rect, 'type': t_type, 'key': str(i + 1)})

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.state == "MENU":
                    self.handle_menu_events(event)
                elif self.state == "DIFFICULTY_SELECTION":
                    self.handle_difficulty_selection_events(event)
                elif self.state == "GAME":
                    self.handle_game_events(event)
                elif self.state == "PAUSE":
                    self.handle_pause_events(event)
                elif self.state == "TOWER_SELECTION":
                    self.handle_tower_selection_events(event)
                elif self.state == "GAME_OVER":
                    self.handle_game_over_events(event)
                elif self.state == "VICTORY":
                    self.handle_victory_events(event)
            if self.state == "GAME":
                self.update_game_logic()
            if self.state == "MENU":
                self.draw_menu()
            elif self.state == "DIFFICULTY_SELECTION":
                self.draw_difficulty_selection()
            elif self.state == "GAME":
                self.draw_game()
            elif self.state == "PAUSE":
                self.draw_game()
                self.draw_pause()
            elif self.state == "TOWER_SELECTION":
                self.draw_tower_selection()
            elif self.state == "GAME_OVER":
                self.draw_game_over()
            elif self.state == "VICTORY":
                self.draw_victory()
            pygame.display.flip()
            self.clock.tick(FPS)

    def handle_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_start.collidepoint(event.pos):
                if self.difficulty is None:
                    self.draw_message("Сначала выберите сложность!")
                    self.state = "DIFFICULTY_SELECTION"
                    return
                if len([t for t in self.chosen_tower_types if t is not None]) == self.NUM_SLOTS:
                    self.reset_game()
                    self.state = "GAME"
                else:
                    self.draw_message(f"Выберите {self.NUM_SLOTS} башни для начала игры.")
            elif self.btn_difficulty_select.collidepoint(event.pos):
                self.state = "DIFFICULTY_SELECTION"
            elif self.btn_tower_select.collidepoint(event.pos):
                self.state = "TOWER_SELECTION"
            elif self.btn_quit.collidepoint(event.pos):
                self.running = False

    def handle_difficulty_selection_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for btn in self.difficulty_buttons:
                if btn['rect'].collidepoint(mouse_pos):
                    self.difficulty = btn['id']
                    self.state = "MENU"
                    return
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "MENU"

    def handle_tower_selection_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.btn_selection_back.collidepoint(mouse_pos):
                if len([t for t in self.chosen_tower_types if t is not None]) == self.NUM_SLOTS:
                    self.setup_game_ui()
                    self.state = "MENU"
                return
            for i, rect in enumerate(self.all_tower_rects):
                if rect.collidepoint(mouse_pos):
                    self.select_tower_for_game(self.all_tower_types[i])
                    return
            for i, rect in enumerate(self.chosen_slot_rects):
                if rect.collidepoint(mouse_pos) and self.chosen_tower_types[i] is not None:
                    self.chosen_tower_types[i] = None
                    return

    def select_tower_for_game(self, tower_type):
        if tower_type in self.chosen_tower_types: return
        for i in range(self.NUM_SLOTS):
            if self.chosen_tower_types[i] is None:
                self.chosen_tower_types[i] = tower_type
                return

    def handle_game_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_mouse_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event.pos)
        elif event.type == pygame.KEYDOWN:
            if self.selected_tower_on_map:
                if event.key == pygame.K_e:
                    tower = self.selected_tower_on_map
                    cost = tower.get_upgrade_cost()
                    if cost > 0 and self.money >= cost:
                        self.money -= cost
                        tower.upgrade()
                        self.draw_message(f"Башня улучшена до ур. {tower.level}!")
                    elif cost == 0:
                        self.draw_message("Макс. уровень достигнут!")
                    else:
                        self.draw_message("Недостаточно денег для улучшения!")
                elif event.key == pygame.K_x:
                    self.sell_selected_tower()
            if event.key == pygame.K_SPACE:
                if self.wave_number == 0 and not self.enemies and not self.spawn_queue:
                    self.start_next_wave()
                else:
                    if not self.enemies and not self.spawn_queue and self.wave_number > 0:
                        self.start_next_wave()
            keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]
            for i, btn in enumerate(self.tower_buttons):
                if event.key == keys[i]:
                    self.pending_tower_type = btn['type']
                    self.selected_tower_on_map = None
                    break
            if event.key == pygame.K_ESCAPE:
                if self.pending_tower_type:
                    self.pending_tower_type = None
                elif self.selected_tower_on_map:
                    self.selected_tower_on_map = None
                else:
                    self.state = "PAUSE"

    def handle_pause_events(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "GAME"
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_resume.collidepoint(event.pos):
                self.state = "GAME"
            elif self.btn_to_menu.collidepoint(event.pos):
                self.state = "MENU"

    def handle_game_over_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_game_over_to_menu.collidepoint(event.pos):
                self.state = "MENU"

    def handle_victory_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_victory_to_menu.collidepoint(event.pos):
                self.state = "MENU"

    def calculate_tower_spent_cost(self, tower):
        cost = 0
        if tower.type in TOWERS:
            cost += TOWERS[tower.type][0]['cost']
            for level_data in TOWERS[tower.type][:tower.level - 1]:
                cost += level_data.get('upgrade_cost', 0)
        return cost

    def sell_selected_tower(self):
        if self.selected_tower_on_map:
            tower = self.selected_tower_on_map
            spent_cost = self.calculate_tower_spent_cost(tower)
            sell_price = int(spent_cost * 0.5)
            self.money += sell_price
            self.towers.remove(tower)
            self.selected_tower_on_map = None
            if tower.type == TOWER_ARMY_BASE and tower.spawned_unit:
                if tower.spawned_unit in self.allied_units:
                    self.allied_units.remove(tower.spawned_unit)
            self.draw_message(f"Башня продана за ${sell_price}!")
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
    def handle_mouse_click(self, pos):
        x, y = pos
        if self.selected_tower_on_map and self.btn_upgrade and self.btn_upgrade.collidepoint(pos):
            tower = self.selected_tower_on_map
            cost = tower.get_upgrade_cost()
            if cost > 0 and self.money >= cost:
                self.money -= cost
                tower.upgrade()
                self.draw_message(f"Башня улучшена до ур. {tower.level}!")
            return
        if self.selected_tower_on_map and self.btn_sell and self.btn_sell.collidepoint(pos):
            self.sell_selected_tower()
            return
        if y >= self.PANEL_Y:
            self.selected_tower_on_map = None
            for btn in self.tower_buttons:
                if btn['rect'].collidepoint(pos):
                    self.pending_tower_type = btn['type']
            return
        if self.pending_tower_type:
            cell_x = (x // TOWER_SIZE) * TOWER_SIZE
            cell_y = (y // TOWER_SIZE) * TOWER_SIZE
            tower_data = TOWERS[self.pending_tower_type][0]
            is_on_path = self.is_path_collision(cell_x, cell_y)
            is_allowed_on_path = self.pending_tower_type in [TOWER_POISON, TOWER_FLAMETHROWER, TOWER_FROST]
            if is_on_path and not is_allowed_on_path:
                return
            for tower in self.towers:
                if tower.x - TOWER_SIZE // 2 == cell_x and tower.y - TOWER_SIZE // 2 == cell_y:
                    return
            if self.money >= tower_data['cost']:
                self.towers.append(Tower(cell_x, cell_y, self.pending_tower_type))
                self.money -= tower_data['cost']
                self.pending_tower_type = None
                self.selected_tower_on_map = None
            else:
                self.draw_message("Not enough money!")
        else:
            clicked_tower = None
            for tower in self.towers:
                if math.hypot(tower.x - x, tower.y - y) <= TOWER_SIZE // 2:
                    clicked_tower = tower
                    break
            if clicked_tower:
                self.selected_tower_on_map = clicked_tower
            else:
                self.selected_tower_on_map = None

    def update_game_logic(self):
        if self.spawn_queue:
            if self.spawn_timer > 0:
                self.spawn_timer -= 1
            else:
                self.spawn_enemy(self.spawn_queue.pop(0))
                self.spawn_timer = self.SPAWN_DELAY
        if not self.enemies and not self.spawn_queue and self.wave_number > 0:
            if self.wave_number >= len(self.waves):
                self.victory()
                return
            if self.next_wave_timer == -1:
                self.next_wave_timer = self.WAVE_DELAY_SEC * FPS
            elif self.next_wave_timer > 0:
                self.next_wave_timer -= 1
            else:
                self.start_next_wave()
                self.next_wave_timer = -1
        for enemy in self.enemies[:]:
            if enemy.update():
                if enemy.reached_end:
                    self.lives -= 1
                    self.money -= 5
                else:
                    self.money += enemy.reward
                    self.enemies_killed_total += 1

                    if enemy.spawns_on_death:
                        self.static_enemies.append(StaticLavaUnit(enemy.x, enemy.y, enemy.spawned_hp))
                self.enemies.remove(enemy)
                if self.lives <= 0: self.game_over()
        for se in self.static_enemies[:]:
            if se.update():
                self.static_enemies.remove(se)
        for tower in self.towers: tower.update(self)
        for p in self.projectiles[:]:
            if p.update(self.enemies + self.static_enemies): self.projectiles.remove(p)
        for u in self.allied_units[:]:
            if u.update(self): self.allied_units.remove(u)

    def game_over(self):
        self.game_over_stats = {
            'waves': self.wave_number,
            'killed': self.enemies_killed_total,
        }
        self.state = "GAME_OVER"

    def victory(self):
        self.victory_stats = {
            'waves': self.wave_number,
            'killed': self.enemies_killed_total,
            'money': self.money
        }
        self.state = "VICTORY"

    def start_next_wave(self):
        if not hasattr(self, 'waves') or not self.waves:
            return
        if self.enemies or self.spawn_queue:
            return
        self.wave_number += 1
        self.next_wave_timer -= 1 #поменял
        if self.wave_number > len(self.waves):
            self.victory()
            return
        for enemy_type, count in self.waves[self.wave_number - 1]:
            for _ in range(count):
                self.spawn_queue.append(enemy_type)

    def spawn_enemy(self, t):
        self.enemies.append(Enemy(t, self.enemy_path))

    def handle_mouse_motion(self, pos):
        if pos[1] >= self.PANEL_Y:
            self.pending_tower_pos = (-100, -100)
            return
        cell_x = (pos[0] // TOWER_SIZE) * TOWER_SIZE
        cell_y = (pos[1] // TOWER_SIZE) * TOWER_SIZE
        self.pending_tower_pos = (cell_x, cell_y)

    def draw_placement_preview(self):
        if self.pending_tower_type and self.pending_tower_pos != (-100, -100):
            x, y = self.pending_tower_pos
            if y < self.PANEL_Y:
                tower_data = TOWERS[self.pending_tower_type][0]
                is_on_path = self.is_path_collision(x, y)
                is_allowed_on_path = self.pending_tower_type in [TOWER_POISON, TOWER_FLAMETHROWER, TOWER_FROST]
                is_occupied = False
                for tower in self.towers:
                    if tower.x - TOWER_SIZE // 2 == x and tower.y - TOWER_SIZE // 2 == y:
                        is_occupied = True
                        break
                can_place = (not is_on_path or is_allowed_on_path) and not is_occupied and self.money >= tower_data['cost']
                if can_place:
                    preview_color = (0, 255, 0, 80)
                    border_color = GREEN
                else:
                    preview_color = (255, 0, 0, 80)
                    border_color = RED
                range_val = tower_data.get('range', 0)
                center_x = x + TOWER_SIZE // 2
                center_y = y + TOWER_SIZE // 2
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.circle(overlay, preview_color, (center_x, center_y), range_val)
                self.screen.blit(overlay, (0, 0))
                pygame.draw.rect(self.screen, border_color, (x, y, TOWER_SIZE, TOWER_SIZE), 3)

    def is_path_collision(self, x, y):
        tr = pygame.Rect(x, y, TOWER_SIZE, TOWER_SIZE)
        segs = []
        for i in range(len(self.enemy_path) - 1):
            segs.append((self.enemy_path[i], self.enemy_path[i + 1]))
        pw = ENEMY_SIZE
        for (x1, y1), (x2, y2) in segs:
            l, t = min(x1, x2), min(y1, y2)
            w, h = abs(x1 - x2), abs(y1 - y2)
            if w == 0: l -= pw // 2; w = pw
            if h == 0: t -= pw // 2; h = pw
            if tr.colliderect(pygame.Rect(l, t, w, h).inflate(TOWER_SIZE / 2, TOWER_SIZE / 2)): return True
        return False

    def draw_message(self, m):
        print(m)

    def draw_menu(self):
        self.screen.fill((30, 30, 30))
        title = self.title_font.render("TOWER DEFENCE", True, GREEN)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 100)))
        mp = pygame.mouse.get_pos()
        diff_name = DIFFICULTY_SETTINGS.get(self.difficulty, {}).get('name', 'НЕ ВЫБРАНА')
        diff_color = WHITE
        if self.difficulty == DIFFICULTY_EASY:
            diff_color = GREEN
        elif self.difficulty == DIFFICULTY_MEDIUM:
            diff_color = YELLOW
        elif self.difficulty == DIFFICULTY_HARD:
            diff_color = RED
        diff_text = self.menu_font.render(f"Сложность: {diff_name}", True, diff_color)
        self.screen.blit(diff_text, diff_text.get_rect(center=(SCREEN_WIDTH // 2, 200)))
        game_ready = len([t for t in self.chosen_tower_types if t]) == self.NUM_SLOTS and self.difficulty is not None
        buttons = [
            (self.btn_start, "НАЧАТЬ ИГРУ", (0, 150, 0) if game_ready else (80, 80, 80)),
            (self.btn_difficulty_select, "ВЫБОР СЛОЖНОСТИ", (0, 100, 150)),
            (self.btn_tower_select, "ВЫБОР БАШЕН", (150, 100, 0)),
            (self.btn_quit, "ВЫХОД", (150, 0, 0))
        ]
        for btn, text, col in buttons:
            is_start_btn = (btn == self.btn_start)
            can_hover = not is_start_btn or game_ready
            c = tuple([min(255, x + 50) for x in col]) if btn.collidepoint(mp) and can_hover else col
            pygame.draw.rect(self.screen, c, btn, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, btn, 3, border_radius=10)
            t = self.menu_font.render(text, True, WHITE)
            self.screen.blit(t, t.get_rect(center=btn.center))

    def draw_difficulty_selection(self):
        self.screen.fill(DARK_BLUE)
        center_x = SCREEN_WIDTH // 2
        title = self.title_font.render("ВЫБОР СЛОЖНОСТИ", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(center_x, 100)))
        mp = pygame.mouse.get_pos()
        for btn_data in self.difficulty_buttons:
            r = btn_data['rect']
            data = btn_data['data']
            col = GRAY
            if btn_data['id'] == DIFFICULTY_EASY:
                col = GREEN
            elif btn_data['id'] == DIFFICULTY_MEDIUM:
                col = YELLOW
            elif btn_data['id'] == DIFFICULTY_HARD:
                col = RED
            c = tuple([min(255, x + 50) for x in col]) if r.collidepoint(mp) else col
            pygame.draw.rect(self.screen, c, r, border_radius=10)
            border_w = 2
            if btn_data['id'] == self.difficulty: border_w = 5
            pygame.draw.rect(self.screen, WHITE, r, border_w, border_radius=10)
            name_text = self.font.render(data['name'], True, BLACK)
            self.screen.blit(name_text, name_text.get_rect(center=(r.centerx, r.y + 25)))
            stats_text = self.small_font.render(
                f"Начало: ${data['money']} / Жизни: {data['lives']} / Путь: {data.get('path_name', 'Стандарт')}",True, WHITE)
            self.screen.blit(stats_text, stats_text.get_rect(center=(r.centerx, r.y + 55)))
        back_text = self.small_font.render("Нажмите [ESC] для возврата", True, GRAY)
        self.screen.blit(back_text, back_text.get_rect(center=(center_x, SCREEN_HEIGHT - 30)))
    def draw_tower_selection(self):
        self.screen.fill(WHITE)
        title = self.title_font.render("ВЫБОР БАШЕН", True, BLACK)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 80)))
        sw, sm = 80, 30
        start_x = (SCREEN_WIDTH - (self.NUM_SLOTS * sw + (self.NUM_SLOTS - 1) * sm)) // 2
        self.chosen_slot_rects = []
        for i in range(self.NUM_SLOTS):
            r = pygame.Rect(start_x + i * (sw + sm), 150, sw, sw)
            self.chosen_slot_rects.append(r)
            pygame.draw.rect(self.screen, GRAY, r, 0, 5)
            pygame.draw.rect(self.screen, BLACK, r, 3, 5)
            t = self.chosen_tower_types[i]
            if t:
                data = TOWERS[t][0]
                pygame.draw.circle(self.screen, data['color'], r.center, sw // 2 - 5)
            else:
                txt = self.font.render(f"{i + 1}", True, BLACK)
                self.screen.blit(txt, txt.get_rect(center=r.center))
        lbl = self.font.render("Доступные башни", True, BLACK)
        self.screen.blit(lbl, (50, 280))
        self.all_tower_rects = []
        iw, im, sx, sy = 70, 25, 50, 330
        mp = pygame.mouse.get_pos()
        for i, t_type in enumerate(self.all_tower_types):
            data = TOWERS[t_type][0]
            col = i % 5
            row = i // 5
            rect = pygame.Rect(sx + col * (iw + im), sy + row * (iw + im), iw, iw)
            self.all_tower_rects.append(rect)
            color = data['color']
            if rect.collidepoint(mp): color = tuple([min(255, x + 30) for x in color])
            if t_type in self.chosen_tower_types: color = DARK_GRAY
            pygame.draw.rect(self.screen, color, rect, 0, 5)
            pygame.draw.rect(self.screen, BLACK, rect, 2, 5)
            pygame.draw.circle(self.screen, data['color'], rect.center, iw // 2 - 5)
            pygame.draw.circle(self.screen, BLACK, rect.center, iw // 2 - 5, 1)
            name_text = self.small_font.render(data['name'], True, BLACK)
            self.screen.blit(name_text, name_text.get_rect(center=(rect.centerx, rect.y - 15)))
            price_text = self.small_font.render(f"${data['cost']}", True, BLACK)
            self.screen.blit(price_text, price_text.get_rect(center=(rect.centerx, rect.y + iw + 10)))
        col = (0, 100, 150)
        c = tuple([min(255, x + 50) for x in col]) if self.btn_selection_back.collidepoint(mp) else col
        pygame.draw.rect(self.screen, c, self.btn_selection_back, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.btn_selection_back, 3, border_radius=10)
        t = self.menu_font.render("НАЗАД", True, WHITE)
        self.screen.blit(t, t.get_rect(center=self.btn_selection_back.center))

    def draw_grid(self):
        for i in range(0, SCREEN_HEIGHT, TOWER_SIZE):
            if i < self.PANEL_Y:
                pygame.draw.line(self.screen, GRAY, (0, i), (SCREEN_WIDTH, i))
        for j in range(0, SCREEN_WIDTH, TOWER_SIZE):
            pygame.draw.line(self.screen, GRAY, (j, 0), (j, self.PANEL_Y))
        for i in range(0, SCREEN_WIDTH, TOWER_SIZE):
            for j in range(0, self.PANEL_Y, TOWER_SIZE):
                is_occupied = any(t.x - TOWER_SIZE // 2 == i and t.y - TOWER_SIZE // 2 == j for t in self.towers)
                is_on_path = self.is_path_collision(i, j)
                rect = pygame.Rect(i, j, TOWER_SIZE, TOWER_SIZE)
                if is_occupied:
                    color = (200, 100, 100, 100)
                    s = pygame.Surface((TOWER_SIZE, TOWER_SIZE), pygame.SRCALPHA)
                    s.fill(color)
                    self.screen.blit(s, rect.topleft)
                if is_on_path:
                    pass

    def draw_path(self):
        if len(self.enemy_path) < 2: return
        path_color = BROWN
        path_width = ENEMY_SIZE
        for i in range(len(self.enemy_path) - 1):
            start = self.enemy_path[i]
            end = self.enemy_path[i + 1]
            pygame.draw.line(self.screen, path_color, start, end, path_width)
        for p in self.enemy_path:
            pygame.draw.circle(self.screen, path_color, p, path_width // 2)

    def draw_tower_panel(self):
        mp = pygame.mouse.get_pos()
        for btn in self.tower_buttons:
            r = btn['rect']
            data = TOWERS[btn['type']][0]
            color = data['color']
            if self.pending_tower_type == btn['type']:
                color = tuple([min(255, x + 40) for x in color])
            elif r.collidepoint(mp):
                color = tuple([min(255, x + 20) for x in color])
            pygame.draw.rect(self.screen, color, r, border_radius=5)
            pygame.draw.rect(self.screen, BLACK, r, 2, border_radius=5)
            pygame.draw.circle(self.screen, data['color'], r.center, TOWER_SIZE // 2 - 5)
            name_text = self.small_font.render(data['name'], True, BLACK)
            self.screen.blit(name_text, name_text.get_rect(center=(r.centerx, r.y + 10)))

            price_text = self.small_font.render(f"${data['cost']}", True, BLACK)
            self.screen.blit(price_text, price_text.get_rect(center=(r.centerx, r.y + r.height - 20)))

    def draw_selected_tower_info(self):
        if not self.selected_tower_on_map:
            self.btn_upgrade = None
            self.btn_sell = None
            return
        tower = self.selected_tower_on_map
        x = SCREEN_WIDTH - 500
        y = self.PANEL_Y + 10
        width = 500
        height = self.PANEL_HEIGHT - 20
        pygame.draw.rect(self.screen, LIGHT_BLUE, (x, y, width, height), border_radius=5)
        pygame.draw.rect(self.screen, BLACK, (x, y, width, height), 2, border_radius=5)
        title_text = f"{tower.data['name']} (Ур. {tower.level})"
        t = self.ui_font.render(title_text, True, BLACK)
        self.screen.blit(t, (x + width // 2 - t.get_width() // 2, y + 5))
        stats_y = y + 30
        def get_next_stat(key, default):
            if tower.level >= 4: return default
            return TOWERS[tower.type][tower.level].get(key, default)
        current_dmg = tower.data.get('damage', 0)
        next_dmg = get_next_stat('damage', 0)
        dmg_txt = f"Урон: {current_dmg}"
        if tower.level < 4 and next_dmg != current_dmg:
            dmg_txt += f" -> {next_dmg}"
        self.screen.blit(self.ui_font.render(dmg_txt, True, BLACK), (x + 10, stats_y))
        stats_y += 30
        current_as = tower.data.get('fire_rate', 0)
        next_as = get_next_stat('fire_rate', 0)
        as_txt = f"Скорость: {FPS / current_as:.1f} /с"
        next_as_val = FPS / next_as if next_as > 0 else 0
        if tower.level < 4 and next_as != current_as:
            as_txt += f" -> {next_as_val:.1f} /с"
        self.screen.blit(self.ui_font.render(as_txt, True, BLACK), (x + 10, stats_y))
        stats_y += 30
        current_range = tower.data.get('range', 0)
        next_range = get_next_stat('range', 0)
        range_txt = f"Радиус: {current_range}"
        if tower.level < 4 and next_range != current_range:
            range_txt += f" -> {next_range}"
        self.screen.blit(self.ui_font.render(range_txt, True, BLACK), (x + 10, stats_y))
        stats_y += 30
        if tower.projectile_type == PROJECTILE_POISON:
            current_pdps = tower.data.get('poison_damage_per_sec', 0)
            next_pdps = get_next_stat('poison_damage_per_sec', 0)
            pdps_txt = f"Яд/с: {current_pdps:.1f}"
            if tower.level < 4 and next_pdps != current_pdps:
                pdps_txt += f" -> {next_pdps:.1f}"
            self.screen.blit(self.ui_font.render(pdps_txt, True, BLACK), (x + 10, stats_y))
            stats_y += 30
        if tower.projectile_type == PROJECTILE_SPLASH:
            current_sr = tower.data.get('splash_radius', 0)
            next_sr = get_next_stat('splash_radius', 0)
            sr_txt = f"Сплэш: {current_sr}"
            if tower.level < 4 and next_sr != current_sr:
                sr_txt += f" -> {next_sr}"
            self.screen.blit(self.ui_font.render(sr_txt, True, BLACK), (x + 10, stats_y))
            stats_y += 30
        if tower.projectile_type == PROJECTILE_FROST:
            current_slow = tower.data.get('slow_factor', 1.0)
            next_slow = get_next_stat('slow_factor', 1.0)
            slow_txt = f"Замедл.: {100 * (1 - current_slow):.0f}%"
            if tower.level < 4 and next_slow != current_slow:
                slow_txt += f" -> {100 * (1 - next_slow):.0f}%"
            self.screen.blit(self.ui_font.render(slow_txt, True, BLACK), (x + 10, stats_y))
            stats_y += 30
        upgrade_cost = tower.get_upgrade_cost()
        self.btn_upgrade = pygame.Rect(x + 365, self.PANEL_Y + 15, 130, 30)
        self.btn_sell = pygame.Rect(x + 365, self.PANEL_Y + 55, 130, 30)
        mp = pygame.mouse.get_pos()
        if upgrade_cost > 0:
            can_upgrade = self.money >= upgrade_cost
            color = (0, 150, 0) if can_upgrade else (80, 80, 80)
            if self.btn_upgrade.collidepoint(mp) and can_upgrade:
                color = tuple([min(255, c + 50) for c in color])
            pygame.draw.rect(self.screen, color, self.btn_upgrade, border_radius=5)
            pygame.draw.rect(self.screen, BLACK, self.btn_upgrade, 2, border_radius=5)
            upgrade_text = f"УЛУЧШИТЬ (${upgrade_cost})"
            t = self.small_font.render(upgrade_text, True, WHITE)
            self.screen.blit(t, t.get_rect(center=self.btn_upgrade.center))
        else:
            color = (0, 100, 150)
            pygame.draw.rect(self.screen, color, self.btn_upgrade, border_radius=5)
            pygame.draw.rect(self.screen, BLACK, self.btn_upgrade, 2, border_radius=5)
            t = self.small_font.render("МАКС. УРОВЕНЬ", True, WHITE)
            self.screen.blit(t, t.get_rect(center=self.btn_upgrade.center))
            self.btn_upgrade = None
        spent_cost = self.calculate_tower_spent_cost(tower)
        sell_price = int(spent_cost * 0.5)
        color = (150, 0, 0)
        if self.btn_sell.collidepoint(mp):
            color = tuple([min(255, c + 50) for c in color])
        pygame.draw.rect(self.screen, color, self.btn_sell, border_radius=5)
        pygame.draw.rect(self.screen, BLACK, self.btn_sell, 2, border_radius=5)
        sell_text = f"ПРОДАТЬ (${sell_price})"
        t = self.small_font.render(sell_text, True, WHITE)
        self.screen.blit(t, t.get_rect(center=self.btn_sell.center))
        tower.draw_range(self.screen)

    def draw_ui(self):
        pygame.draw.rect(self.screen, GRAY, (0, self.PANEL_Y, SCREEN_WIDTH, self.PANEL_HEIGHT))
        pygame.draw.line(self.screen, BLACK, (0, self.PANEL_Y), (SCREEN_WIDTH, self.PANEL_Y), 3)
        self.draw_tower_panel()
        self.draw_selected_tower_info()
        self.screen.blit(self.font.render(f"Деньги: ${self.money}", True, BLACK), (10, 10))
        color = BLACK
        if self.lives < 5: color = RED
        self.screen.blit(self.font.render(f"Жизни: {self.lives}", True, color), (10, 50))
        w_total = len(self.waves)
        w = self.font.render(f"Волна: {self.wave_number}/{w_total}", True, BLACK)
        self.screen.blit(w, (SCREEN_WIDTH - w.get_width() - 10, 10))
        if self.next_wave_timer > 0:
            timer_text = f"След.: {math.ceil(self.next_wave_timer / FPS)}с"
            t = self.font.render(timer_text, True, RED)
            self.screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, 10))

    def draw_game(self):
        self.screen.fill(WHITE)
        self.draw_grid()
        self.draw_path()
        for se in self.static_enemies: se.draw(self.screen)
        for tower in self.towers: tower.draw(self.screen)
        for unit in self.allied_units: unit.draw(self.screen)
        for enemy in self.enemies: enemy.draw(self.screen)
        for p in self.projectiles: p.draw(self.screen)
        self.draw_placement_preview()
        self.draw_ui()

    def draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        center_x = SCREEN_WIDTH // 2
        title = self.title_font.render("ПАУЗА", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(center_x, 150)))
        mp = pygame.mouse.get_pos()
        buttons = [
            (self.btn_resume, "ПРОДОЛЖИТЬ", (0, 150, 0)),
            (self.btn_to_menu, "ВЫЙТИ В МЕНЮ", (150, 80, 0))
        ]
        for btn, text, col in buttons:
            c = tuple([min(255, x + 50) for x in col]) if btn.collidepoint(mp) else col
            pygame.draw.rect(self.screen, c, btn, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, btn, 3, border_radius=10)
            t = self.menu_font.render(text, True, WHITE)
            self.screen.blit(t, t.get_rect(center=btn.center))

    def draw_game_over(self):
        self.screen.fill(BLACK)
        center_x = SCREEN_WIDTH // 2
        title = self.title_font.render("ИГРА ОКОНЧЕНА", True, RED)
        self.screen.blit(title, title.get_rect(center=(center_x, 150)))
        stats = [
            f"Волн пройдено: {self.game_over_stats['waves']}",
            f"Врагов убито: {self.game_over_stats['killed']}",
        ]
        stats_y = 250
        for s in stats:
            t = self.font.render(s, True, WHITE)
            self.screen.blit(t, t.get_rect(center=(center_x, stats_y)))
            stats_y += 40
        mp = pygame.mouse.get_pos()
        col = (150, 80, 0)
        c = tuple([min(255, x + 50) for x in col]) if self.btn_game_over_to_menu.collidepoint(mp) else col
        pygame.draw.rect(self.screen, c, self.btn_game_over_to_menu, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.btn_game_over_to_menu, 3, border_radius=10)
        t = self.menu_font.render("ВЕРНУТЬСЯ В МЕНЮ", True, WHITE)
        self.screen.blit(t, t.get_rect(center=self.btn_game_over_to_menu.center))

    def draw_victory(self):
        self.screen.fill(WIN_GREEN)
        center_x = SCREEN_WIDTH // 2
        title = self.title_font.render("ПОБЕДА!", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(center_x, 150)))
        stats = [
            f"Волн пройдено: {self.victory_stats['waves']}",
            f"Врагов убито: {self.victory_stats['killed']}",
            f"Оставшиеся деньги: ${self.victory_stats['money']}"
        ]
        stats_y = 250
        for s in stats:
            t = self.font.render(s, True, WHITE)
            self.screen.blit(t, t.get_rect(center=(center_x, stats_y)))
            stats_y += 40
        mp = pygame.mouse.get_pos()
        col = (0, 100, 150)
        c = tuple([min(255, x + 50) for x in col]) if self.btn_victory_to_menu.collidepoint(mp) else col
        pygame.draw.rect(self.screen, c, self.btn_victory_to_menu, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, self.btn_victory_to_menu, 3, border_radius=10)
        t = self.menu_font.render("ВЕРНУТЬСЯ В МЕНЮ", True, WHITE)
        self.screen.blit(t, t.get_rect(center=self.btn_victory_to_menu.center))


if __name__ == '__main__':
    try:
        g = Game()
        g.run()
    finally:
        pygame.quit()
        sys.exit()



