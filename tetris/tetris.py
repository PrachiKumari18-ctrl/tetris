import pygame
import random

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 450, 750  # 15 cols, 25 rows
BLOCK_SIZE = 30
COLS, ROWS = SCREEN_WIDTH // BLOCK_SIZE, SCREEN_HEIGHT // BLOCK_SIZE
FPS = 60
FALL_DELAY = 500  # milliseconds

# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLACK = (0, 0, 0)
COLORS = [
    (0, 255, 255), (255, 255, 0), (128, 0, 128),
    (0, 255, 0), (255, 0, 0), (255, 165, 0), (0, 0, 255),
    (255, 105, 180)
]

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 1], [0, 1, 0]]
]

# Classes
class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

# Utility Functions
def check_collision(grid, shape, offset):
    ox, oy = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if (x + ox < 0 or x + ox >= COLS or y + oy >= ROWS or grid[y + oy][x + ox]):
                    return True
    return False

def merge(grid, shape, offset, color):
    ox, oy = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                grid[y + oy][x + ox] = color

def clear_lines(grid):
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    cleared = ROWS - len(new_grid)
    for _ in range(cleared):
        new_grid.insert(0, [0 for _ in range(COLS)])
    return new_grid, cleared

def draw_grid(screen, grid):
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
            color = grid[y][x] if grid[y][x] != 0 else GRAY
            pygame.draw.rect(screen, color, rect, 0 if grid[y][x] else 1)

def draw_shape(screen, shape, offset, color):
    ox, oy = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((x + ox)*BLOCK_SIZE, (y + oy)*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, color, rect)

def draw_ui(screen, next_block, lives):
    font = pygame.font.SysFont('Arial', 20)
    next_text = font.render("Next:", True, WHITE)
    screen.blit(next_text, (SCREEN_WIDTH + 20, 20))

    for y, row in enumerate(next_block.shape):
        for x, cell in enumerate(row):
            if cell:
                rect = pygame.Rect(SCREEN_WIDTH + 20 + x*BLOCK_SIZE, 40 + y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, next_block.color, rect)

    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(lives_text, (SCREEN_WIDTH + 20, 200))

def show_game_over(screen):
    font = pygame.font.SysFont('Arial', 40, bold=True)
    text = font.render('Game Over', True, (255, 0, 0))
    screen.blit(text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20))
    pygame.display.flip()
    pygame.time.wait(3000)

# Main Game Loop
screen = pygame.display.set_mode((SCREEN_WIDTH + 150, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()

grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
current = Tetromino()
next_block = Tetromino()
lives = 3
fall_time = 0
running = True
game_over = False

while running:
    screen.fill(BLACK)
    dt = clock.tick(FPS)
    fall_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_LEFT:
                    if not check_collision(grid, current.shape, (current.x - 1, current.y)):
                        current.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    if not check_collision(grid, current.shape, (current.x + 1, current.y)):
                        current.move(1, 0)
                elif event.key == pygame.K_DOWN:
                    if not check_collision(grid, current.shape, (current.x, current.y + 1)):
                        current.move(0, 1)
                elif event.key == pygame.K_UP:
                    rotated = [list(row) for row in zip(*current.shape[::-1])]
                    if not check_collision(grid, rotated, (current.x, current.y)):
                        current.rotate()

    if not game_over and fall_time > FALL_DELAY:
        fall_time = 0
        if not check_collision(grid, current.shape, (current.x, current.y + 1)):
            current.move(0, 1)
        else:
            merge(grid, current.shape, (current.x, current.y), current.color)
            grid, _ = clear_lines(grid)
            current = next_block
            next_block = Tetromino()
            if check_collision(grid, current.shape, (current.x, current.y)):
                lives -= 1
                if lives > 0:
                    current = Tetromino()
                else:
                    game_over = True
                    show_game_over(screen)

    draw_grid(screen, grid)
    if not game_over:
        draw_shape(screen, current.shape, (current.x, current.y), current.color)
    draw_ui(screen, next_block, lives)
    pygame.display.flip()

pygame.quit()
