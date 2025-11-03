import pygame
import sys
import os
import random
import math
from maze_generator import generate_maze
from search_algorithms import astar
from rl_agent import RLAgent

# ---------- CONFIG ----------
TILE_SIZE = 32
GRID_W, GRID_H = 25, 17
SCREEN_W = GRID_W * TILE_SIZE
SCREEN_H = GRID_H * TILE_SIZE
FPS = 60

ASSET_DIR = "assets"

BG_COLOR = (35, 30, 25)
VISION_COLOR = (255, 100, 100, 60)
COIN_COLOR = (255, 220, 0)

# ---------- UTILITIES ----------
def load_image(name, scale=None, fallback_color=None):
    path = os.path.join(ASSET_DIR, name)
    if not os.path.exists(path):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill(fallback_color or (200, 50, 50))
        return surf
    img = pygame.image.load(path).convert_alpha()
    if scale:
        img = pygame.transform.smoothscale(img, scale)
    return img

def load_sound(name):
    path = os.path.join(ASSET_DIR, name)
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except:
            pass
    return None

# ---------- SPRITES ----------
class Robot(pygame.sprite.Sprite):
    def __init__(self, start_cell, rl_agent):
        super().__init__()
        self.walk_imgs = [
            load_image("robot_walk1.png", (TILE_SIZE - 4, TILE_SIZE - 4), (0, 255, 0)),
            load_image("robot_walk2.png", (TILE_SIZE - 4, TILE_SIZE - 4), (0, 200, 0))
        ]
        self.image = self.walk_imgs[0]
        self.rect = self.image.get_rect()
        self.cell = start_cell
        self.pos = pygame.Vector2(start_cell[0] * TILE_SIZE + TILE_SIZE // 2,
                                  start_cell[1] * TILE_SIZE + TILE_SIZE // 2)
        self.target_cell = None
        self.moving = False
        self.speed = 1.2
        self.timer = 0
        self.rl = rl_agent
        self.prev_state = None
        self.prev_action = None
        self.idle_frames = 0  # For detecting stuck state

    def action_to_delta(self, action):
        return [(0, -1), (1, 0), (0, 1), (-1, 0)][action]

    def legal_actions(self, maze):
        acts = []
        for a in range(4):
            dx, dy = self.action_to_delta(a)
            nx, ny = self.cell[0] + dx, self.cell[1] + dy
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H and maze[ny][nx] == 0:
                acts.append(a)
        return acts

    def choose_action(self, maze):
        legal = self.legal_actions(maze)
        if not legal:
            return None
        a = self.rl.choose(self.cell)
        if a not in legal:
            a = random.choice(legal)
        return a

    def start_move(self, maze):
        a = self.choose_action(maze)
        if a is None:
            self.idle_frames += 1
            return
        dx, dy = self.action_to_delta(a)
        nxt = (self.cell[0] + dx, self.cell[1] + dy)
        self.target_cell = nxt
        self.moving = True
        self.prev_state = self.cell
        self.prev_action = a
        self.idle_frames = 0

    def update(self, dt_seconds):
        if not self.moving or not self.target_cell:
            return

        target_pos = pygame.Vector2(
            self.target_cell[0] * TILE_SIZE + TILE_SIZE // 2,
            self.target_cell[1] * TILE_SIZE + TILE_SIZE // 2
        )

        direction = target_pos - self.pos
        if direction.length() < 0.5:
            self.pos = target_pos
            self.cell = self.target_cell
            self.moving = False
            self.target_cell = None
        else:
            direction = direction.normalize()
            self.pos += direction * self.speed * dt_seconds * 60

        # Animate walk
        self.timer += dt_seconds
        if self.timer > 0.3:
            self.image = self.walk_imgs[(self.walk_imgs.index(self.image) + 1) % 2]
            self.timer = 0

        self.rect.center = (int(self.pos.x), int(self.pos.y))


class Guard(pygame.sprite.Sprite):
    def __init__(self, patrol_path, maze):
        super().__init__()
        self.image = load_image("police1.png", (TILE_SIZE - 6, TILE_SIZE - 6), (255, 0, 0))
        self.rect = self.image.get_rect()
        self.path = [p for p in patrol_path if 0 <= p[0] < GRID_W and 0 <= p[1] < GRID_H and maze[p[1]][p[0]] == 0]
        if not self.path:
            self.path = [(1, 1)]
        self.idx = 0
        self.cell = self.path[self.idx]
        self.pos = pygame.Vector2(self.cell[0] * TILE_SIZE + TILE_SIZE // 2,
                                  self.cell[1] * TILE_SIZE + TILE_SIZE // 2)
        self.wait = 30
        self.timer = 0
        self.maze = maze
        self.vision_distance = 6
        self.vision_angle = math.pi / 3
        self.facing = pygame.Vector2(1, 0)

    def update(self, dt):
        self.timer += 1
        if self.timer >= self.wait:
            self.timer = 0
            self.idx = (self.idx + 1) % len(self.path)
            self.cell = self.path[self.idx]
            self.pos = pygame.Vector2(self.cell[0] * TILE_SIZE + TILE_SIZE // 2,
                                      self.cell[1] * TILE_SIZE + TILE_SIZE // 2)
            nxt = self.path[(self.idx + 1) % len(self.path)]
            dx = nxt[0] - self.cell[0]
            dy = nxt[1] - self.cell[1]
            if dx or dy:
                self.facing = pygame.Vector2(dx, dy).normalize()
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def can_see(self, bot_cell):
        gx, gy = self.cell
        bx, by = bot_cell
        dx = bx - gx
        dy = by - gy
        dist = math.hypot(dx, dy)
        if dist == 0 or dist > self.vision_distance:
            return False
        dirv = pygame.Vector2(dx / dist, dy / dist)
        dot = dirv.dot(self.facing)
        angle = math.acos(max(min(dot, 1.0), -1.0))
        if angle > self.vision_angle / 2:
            return False
        for i in range(1, int(dist) + 1):
            ix = gx + round(dx * i / dist)
            iy = gy + round(dy * i / dist)
            if not (0 <= ix < GRID_W and 0 <= iy < GRID_H) or self.maze[iy][ix] == 1:
                return False
        return True

    def draw_vision(self, screen):
        gx = self.cell[0] * TILE_SIZE + TILE_SIZE // 2
        gy = self.cell[1] * TILE_SIZE + TILE_SIZE // 2
        fdx, fdy = self.facing
        left_angle = math.atan2(fdy, fdx) - self.vision_angle / 2
        right_angle = math.atan2(fdy, fdx) + self.vision_angle / 2
        points = [(gx, gy)]
        for ang in [left_angle, right_angle]:
            px = gx + math.cos(ang) * self.vision_distance * TILE_SIZE
            py = gy + math.sin(ang) * self.vision_distance * TILE_SIZE
            points.append((px, py))
        s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        pygame.draw.polygon(s, VISION_COLOR, points)
        screen.blit(s, (0, 0))

# ---------- HELPERS ----------
def spawn_loot(maze, count=5):
    free = [(x, y) for y, row in enumerate(maze) for x, v in enumerate(row) if v == 0]
    random.shuffle(free)
    return set(free[:count])

def find_free_cell(maze):
    free = [(x, y) for y, row in enumerate(maze) for x, v in enumerate(row) if v == 0]
    return random.choice(free)

def draw_maze(screen, maze, floor_img, wall_img):
    for y, row in enumerate(maze):
        for x, v in enumerate(row):
            img = floor_img if v == 0 else wall_img
            screen.blit(img, (x * TILE_SIZE, y * TILE_SIZE))

# ---------- MAIN ----------
def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Robbery Bot RL: Mansion AI Stealth")
    clock = pygame.time.Clock()

    floor_img = load_image("floor_tile.png", (TILE_SIZE, TILE_SIZE), (90, 90, 90))
    wall_img = load_image("wall_tile.png", (TILE_SIZE, TILE_SIZE), (40, 40, 40))

    loot_img = load_image("coin.png", (TILE_SIZE - 12, TILE_SIZE - 12))
    collect_snd = load_sound("collect.wav")
    caught_snd = load_sound("caught.wav")

    rl = RLAgent(load=True)

    while True:  # full game restart loop
        maze = generate_maze(GRID_W, GRID_H)
        start_cell = find_free_cell(maze)
        bot = Robot(start_cell, rl)
        loot = spawn_loot(maze, count=8)

        guards = []
        free_cells = [(x, y) for y, row in enumerate(maze) for x, v in enumerate(row) if v == 0]
        random.shuffle(free_cells)
        for i in range(min(2, len(free_cells) // 5)):
            base = free_cells[i * 5]
            patrol = [(base[0] + dx, base[1] + dy)
                      for dx, dy in [(0, 0), (1, 0), (1, 1), (0, 1)]
                      if 0 <= base[0] + dx < GRID_W and 0 <= base[1] + dy < GRID_H and maze[base[1] + dy][base[0] + dx] == 0]
            if patrol:
                guards.append(Guard(patrol, maze))

        all_sprites = pygame.sprite.Group(bot, *guards)
        collected = 0
        running = True

        while running:
            dt = clock.tick(FPS)
            dt_seconds = dt / 1000.0

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    rl.save()
                    pygame.quit()
                    sys.exit()

            # Bot move
            if not bot.moving:
                bot.start_move(maze)

            bot.update(dt_seconds)
            for g in guards:
                g.update(dt)

            reward = -0.01
            if bot.cell in loot:
                loot.remove(bot.cell)
                collected += 1
                reward += 10
                if collect_snd:
                    collect_snd.play()

            caught = any(g.cell == bot.cell or g.can_see(bot.cell) for g in guards)
            if caught:
                reward -= 10
                if caught_snd:
                    caught_snd.play()
                rl.update(bot.prev_state, bot.prev_action, reward, bot.cell, bot.legal_actions(maze))
                rl.save()
                break  # restart maze safely

            if bot.prev_action is not None:
                rl.update(bot.prev_state, bot.prev_action, reward, bot.cell, bot.legal_actions(maze))
                bot.prev_state = None
                bot.prev_action = None

            # Detect stuck agent
            if bot.idle_frames > 60:
                break  # regenerate maze if no moves possible

            # ---------- DRAW ----------
            screen.fill(BG_COLOR)
            draw_maze(screen, maze, floor_img, wall_img)
            for g in guards:
                g.draw_vision(screen)
            for lx, ly in loot:
                rect = loot_img.get_rect(center=(lx * TILE_SIZE + TILE_SIZE // 2,
                                                 ly * TILE_SIZE + TILE_SIZE // 2))
                screen.blit(loot_img, rect)
            all_sprites.draw(screen)

            font = pygame.font.SysFont(None, 22)
            hud = font.render(f"Loot left: {len(loot)} | Eps: {rl.eps:.3f}", True, (255, 255, 255))
            screen.blit(hud, (8, SCREEN_H - 26))
            pygame.display.flip()

if __name__ == "__main__":
    main()
