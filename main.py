import pygame
import random
import sys
from enum import Enum

# Инициализация Pygame
pygame.init()


# Константы
class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


# Настройки игры
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)
DARK_GREEN = (0, 180, 0)
GRAY = (40, 40, 40)


class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        """Сброс змейки в начальное состояние"""
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.grow_pending = 3  # Начальная длина змейки
        self.score = 0

    def change_direction(self, new_direction):
        """Изменение направления движения"""
        # Запрещаем движение в противоположном направлении
        opposite_directions = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }

        if new_direction != opposite_directions.get(self.direction):
            self.next_direction = new_direction

    def move(self):
        """Движение змейки"""
        self.direction = self.next_direction

        # Получаем текущую позицию головы
        head_x, head_y = self.body[0]

        # Вычисляем новую позицию головы
        dx, dy = self.direction.value
        new_head = ((head_x + dx) % GRID_WIDTH, (head_y + dy) % GRID_HEIGHT)

        # Проверяем столкновение с собой
        if new_head in self.body:
            return False  # Игра окончена

        # Добавляем новую голову
        self.body.insert(0, new_head)

        # Убираем хвост, если не нужно расти
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

        return True  # Игра продолжается

    def grow(self):
        """Увеличение змейки"""
        self.grow_pending += 1
        self.score += 10

    def draw(self, screen):
        """Отрисовка змейки"""
        for i, (x, y) in enumerate(self.body):
            color = DARK_GREEN if i == 0 else GREEN  # Голова темнее
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, DARK_GREEN, rect, 1)  # Обводка


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn()

    def spawn(self, snake_body=None):
        """Создание еды в случайном месте"""
        if snake_body is None:
            snake_body = []

        while True:
            position = (random.randint(0, GRID_WIDTH - 1),
                        random.randint(0, GRID_HEIGHT - 1))
            if position not in snake_body:
                self.position = position
                break

    def draw(self, screen):
        """Отрисовка еды"""
        x, y = self.position
        rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, RED, rect)
        pygame.draw.rect(screen, (150, 0, 0), rect, 1)  # Обводка


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Змейка")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.snake = Snake()
        self.food = Food()
        self.food.spawn(self.snake.body)
        self.game_over = False
        self.paused = False

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.restart()
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif not self.paused:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(Direction.RIGHT)

        return True

    def update(self):
        """Обновление состояния игры"""
        if self.game_over or self.paused:
            return

        # Двигаем змейку
        if not self.snake.move():
            self.game_over = True
            return

        # Проверяем съедание еды
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            self.food.spawn(self.snake.body)

    def draw(self):
        """Отрисовка игры"""
        self.screen.fill(BLACK)

        # Рисуем сетку
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))

        # Рисуем объекты игры
        self.food.draw(self.screen)
        self.snake.draw(self.screen)

        # Рисуем счет
        score_text = self.font.render(f"Счет: {self.snake.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Рисуем сообщения
        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause()

        pygame.display.flip()

    def draw_game_over(self):
        """Отрисовка экрана завершения игры"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("ИГРА ОКОНЧЕНА!", True, RED)
        score_text = self.font.render(f"Финальный счет: {self.snake.score}", True, WHITE)
        restart_text = self.small_font.render("Нажмите R для перезапуска", True, WHITE)

        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))

    def draw_pause(self):
        """Отрисовка экрана паузы"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(120)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        pause_text = self.font.render("ПАУЗА", True, BLUE)
        continue_text = self.small_font.render("Нажмите P для продолжения", True, WHITE)

        self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 20))
        self.screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 20))

    def restart(self):
        """Перезапуск игры"""
        self.snake.reset()
        self.food.spawn(self.snake.body)
        self.game_over = False
        self.paused = False

    def run(self):
        """Главный игровой цикл"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()