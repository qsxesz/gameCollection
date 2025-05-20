import pygame
import sys
import random
from pygame import mixer
import logging
import os
import tkinter as tk
from tkinter import filedialog

class CuteGameHub:
    def __init__(self):
        pygame.init()
        mixer.init()
        self.music_enabled = True
        self.volume_level = mixer.music.get_volume()  # начальный уровень громкости (0.0 - 1.0)
        self.dragging_volume = False
        # Настройка логгирования
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("CuteGameHub")

        # Настройки окна
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Cute Game Hub")

        # Цвета
        self.BG_COLOR = (255, 228, 225)  # Мятный
        self.TEXT_COLOR = (139, 125, 171)  # Фиолетовый
        self.BUTTON_COLOR = (255, 209, 220)  # Розовый
        self.BUTTON_HOVER = (255, 182, 193)  # Ярко-розовый
        self.ACCENT_COLOR = (255, 105, 180)  # Ярко-розовый

        # Шрифты
        self.load_fonts()

        # Состояния
        self.state = "main_menu"
        self.running = True
        self.music_enabled = True

        # Состояния
        self.states = {
            "main_menu": self.main_menu,
            "music_selection": self.music_selection
        }

        # Игры
        self.games = {
            "Крестики-Нолики": self.run_tic_tac_toe,
            "Wordle": self.run_wordle,
            "Найди пары": self.run_memory_game
        }

        # Загрузка изображений
        self.load_images()

        # Загрузка музыки
        self.load_music()


    def add_custom_music(self):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
        if file_path:
            dest_folder = "assets/sounds/custom_music"
            os.makedirs(dest_folder, exist_ok=True)
            import shutil
            filename = os.path.basename(file_path)
            shutil.copy(file_path, os.path.join(dest_folder, filename))
            self.load_music()

    def change_music(self, file_path):
        """Изменяет текущий трек"""
        try:
            mixer.music.stop()
            mixer.music.load(file_path)
            if self.music_enabled:
                mixer.music.play(-1)
        except Exception as e:
            self.logger.error(f"Ошибка при смене музыки: {e}")

    def load_fonts(self):
        """Загрузка шрифтов"""
        font_paths = [
            "assets/fonts/cute_font.ttf",
            None  # Для использования системных шрифтов
        ]

        for path in font_paths:
            try:
                if path:
                    self.font_large = pygame.font.Font(path, 60)
                    self.font_medium = pygame.font.Font(path, 40)
                    self.font_small = pygame.font.Font(path, 30)
                    break
            except:
                continue

    def load_images(self):
        """Загрузка изображений"""
        try:
            self.background = pygame.image.load("assets/images/cute_bg.png").convert()
            self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
            self.button_img = pygame.image.load("assets/images/cute_button.png").convert_alpha()

        except Exception as e:
            self.logger.warning(f"Не удалось загрузить изображения: {e}")
            self.background = None
            self.button_img = None

    def load_music(self):
        """Загрузка и настройка музыки"""
        try:
            mixer.music.load("assets/sounds/cute_music.mp3")
            mixer.music.set_volume(0.3)
            if self.music_enabled:
                mixer.music.play(-1)  # Зациклить
        except Exception as e:
            self.logger.warning(f"Не удалось загрузить музыку: {e}")

    def toggle_music(self):
        """Включение/выключение музыки"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            mixer.music.play(-1)
        else:
            mixer.music.stop()

    def music_selection(self):
        self.screen.fill(self.BG_COLOR)
        self.draw_text("Выберите музыку", self.font_medium, self.ACCENT_COLOR, self.screen_width // 2, 80)

        music_dir = "assets/sounds/custom_music"
        default_music = ["assets/sounds/cute_music.mp3"]
        custom_files = [os.path.join(music_dir, f) for f in os.listdir(music_dir) if f.endswith(".mp3")] if os.path.exists(music_dir) else []
        all_music = default_music + custom_files
        labels = ["Стандартная"] + [os.path.basename(f) for f in custom_files]

        button_y_start = 150
        button_rects = []
        for i, label in enumerate(labels):
            rect = self.draw_button(label, self.screen_width // 2, button_y_start + i * 80)
            button_rects.append((rect, all_music[i]))

        add_rect = self.draw_button("Добавить свою музыку", self.screen_width // 2, button_y_start + len(labels) * 80)
        back_rect = self.draw_button("Назад", self.screen_width // 2, 550)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if back_rect.collidepoint(pos):
                    self.state = "main_menu"
                elif add_rect.collidepoint(pos):
                    self.add_custom_music()
                else:
                    for rect, path in button_rects:
                        if rect.collidepoint(pos):
                            self.change_music(path)

        pygame.display.flip()

    def draw_text(self, text, font, color, x, y):
        """Вспомогательная функция для отрисовки текста"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def draw_button(self, text, x, y, width=300, height=80):
        """Рисует кнопку и возвращает её rect"""
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(x - width // 2, y - height // 2, width, height)

        # Проверка наведения мыши
        if button_rect.collidepoint(mouse_pos):
            color = self.BUTTON_HOVER
        else:
            color = self.BUTTON_COLOR

        # Рисуем кнопку
        if self.button_img:
            img = pygame.transform.scale(self.button_img, (width, height))
            self.screen.blit(img, button_rect)
        else:
            pygame.draw.rect(self.screen, color, button_rect, border_radius=20)
            pygame.draw.rect(self.screen, self.ACCENT_COLOR, button_rect, 3, border_radius=20)

        # Текст на кнопке
        text_rect = self.draw_text(text, self.font_small, self.TEXT_COLOR, x, y)
        return button_rect

    def main_menu(self):
        """Главное меню"""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)

        # Заголовок
        self.draw_text("Cute Game Collection", self.font_large, self.ACCENT_COLOR,
                       self.screen_width // 2, 100)

        # Кнопки
        start_rect = self.draw_button("Начать игру", self.screen_width // 2, 200)
        settings_rect = self.draw_button("Настройки", self.screen_width // 2, 300)
        music_text = "Выкл. музыку" if self.music_enabled else "Вкл. музыку"
        music_rect = self.draw_button(music_text, self.screen_width // 2, 400)
        exit_rect = self.draw_button("Выход", self.screen_width // 2, 500)

        # Рисуем ползунок громкости
        slider_x = self.screen_width // 2 - 150
        slider_y = 520 - 80
        slider_width = 300
        slider_height = 10
        pygame.draw.rect(self.screen, self.TEXT_COLOR, (slider_x, slider_y, slider_width, slider_height),
                         border_radius=5)

        # Ползунок
        slider_handle_radius = 10
        slider_value = int(slider_x + self.volume_level * slider_width)
        handle_rect = pygame.draw.circle(
            self.screen,
            self.ACCENT_COLOR,
            (slider_value, slider_y + slider_height // 2),
            slider_handle_radius
        )

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_rect.collidepoint(mouse_pos):
                    self.state = "game_selection"
                elif settings_rect.collidepoint(mouse_pos):
                    self.state = "music_selection"
                elif music_rect.collidepoint(mouse_pos):
                    self.toggle_music()
                    return
                elif exit_rect.collidepoint(mouse_pos):
                    self.quit_game()
                elif handle_rect.collidepoint(mouse_pos):
                    self.dragging_volume = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_volume = False
            elif event.type == pygame.MOUSEMOTION:
                if getattr(self, 'dragging_volume', False):
                    x = max(slider_x, min(event.pos[0], slider_x + slider_width))
                    self.volume_level = (x - slider_x) / slider_width
                    mixer.music.set_volume(self.volume_level)

        pygame.display.flip()

    def game_selection(self):
        """Экран выбора игры"""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BG_COLOR)

        # Заголовок
        self.draw_text("Выбери игру!", self.font_large, self.ACCENT_COLOR,
                       self.screen_width // 2, 80)

        # Кнопки игр
        game_rects = {}
        y_pos = 180
        for i, game in enumerate(self.games.keys()):
            rect = self.draw_button(game, self.screen_width // 2, y_pos + i * 100)
            game_rects[game] = rect

        # Кнопка назад
        back_rect = self.draw_button("Назад", self.screen_width // 2, 550)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                for game, rect in game_rects.items():
                    if rect.collidepoint(mouse_pos):
                        self.games[game]()

                if back_rect.collidepoint(mouse_pos):
                    self.state = "main_menu"

        pygame.display.flip()

    def run_tic_tac_toe(self):
        """Игра Крестики-Нолики"""
        # Инициализация игры
        board = [["", "", ""], ["", "", ""], ["", "", ""]]
        current_player = "X"
        game_over = False
        winner = None

        # Размеры и позиции
        cell_size = 90
        grid_start_x = self.screen_width // 2 - cell_size * 1.5
        grid_start_y = self.screen_height // 2 - cell_size * 2.3

        # Основной цикл игры
        running = True
        while running:
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(self.BG_COLOR)

            # Заголовок
            self.draw_text("Крестики-Нолики", self.font_medium, self.ACCENT_COLOR,
                           self.screen_width // 2, 50)

            # Рисуем сетку
            for i in range(3):
                for j in range(3):
                    rect = pygame.Rect(
                        grid_start_x + j * cell_size,
                        grid_start_y + i * cell_size,
                        cell_size, cell_size
                    )
                    pygame.draw.rect(self.screen, self.BUTTON_COLOR, rect, border_radius=10)
                    pygame.draw.rect(self.screen, self.ACCENT_COLOR, rect, 3, border_radius=10)

                    # Рисуем X или O
                    if board[i][j] == "X":
                        self.draw_text("X", self.font_large, (255, 100, 100),
                                       rect.centerx, rect.centery)
                    elif board[i][j] == "O":
                        self.draw_text("O", self.font_large, (100, 100, 255),
                                       rect.centerx, rect.centery)

            # Кнопка назад
            back_rect = self.draw_button("Меню", self.screen_width // 2, 550)

            # Проверка победы
            if not game_over:
                winner = self.check_tic_tac_toe_winner(board)
                if winner or all(board[i][j] for i in range(3) for j in range(3)):
                    game_over = True

            # Отображение результата
            if game_over:
                if winner:
                    text = f"Победил {winner}!"
                else:
                    text = "Ничья!"

                self.draw_text(text, self.font_medium, self.ACCENT_COLOR,
                               self.screen_width // 2, 400)
                restart_rect = self.draw_button("Играть снова", self.screen_width // 2, 470)

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if back_rect.collidepoint(mouse_pos):
                        running = False

                    if game_over and "restart_rect" in locals():
                        if restart_rect.collidepoint(mouse_pos):
                            # Сброс игры
                            board = [["", "", ""], ["", "", ""], ["", "", ""]]
                            current_player = "X"
                            game_over = False
                            winner = None

                    if not game_over:
                        # Обработка хода
                        for i in range(3):
                            for j in range(3):
                                rect = pygame.Rect(
                                    grid_start_x + j * cell_size,
                                    grid_start_y + i * cell_size,
                                    cell_size, cell_size
                                )
                                if rect.collidepoint(mouse_pos) and not board[i][j]:
                                    board[i][j] = current_player
                                    current_player = "O" if current_player == "X" else "X"

            pygame.display.flip()

        self.state = "game_selection"

    def check_tic_tac_toe_winner(self, board):
        """Проверяет победителя в Крестиках-Ноликах"""
        # Проверка строк
        for row in board:
            if row[0] == row[1] == row[2] != "":
                return row[0]

        # Проверка столбцов
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != "":
                return board[0][col]

        # Проверка диагоналей
        if board[0][0] == board[1][1] == board[2][2] != "":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != "":
            return board[0][2]

        return None

    def run_wordle(self):
        """Игра Wordle (упрощенная версия)"""
        # Список слов одной длины (5 букв)
        words = ["КОШКА", "СОБАКА", "ДЕРЕВО", "ЦВЕТОК", "СОЛНЦЕ",
                 "РАДУГА", "МЫШКА", "ПЧЕЛА", "ЛОДКА", "ВЕТЕР"]
        secret_word = random.choice(words).lower()
        attempts = 5
        current_attempt = 0
        guesses = [""] * attempts
        game_over = False

        # Размеры и позиции
        letter_size = 60
        word_length = len(secret_word)
        grid_start_x = self.screen_width // 2 - (word_length * letter_size) // 2
        grid_start_y = 100

        # Основной цикл игры
        running = True
        current_guess = ""

        while running:
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(self.BG_COLOR)

            # Заголовок
            self.draw_text("Wordle", self.font_medium, self.ACCENT_COLOR,
                           self.screen_width // 2, 50)

            # Рисуем сетку для букв
            for i in range(attempts):
                for j in range(word_length):
                    rect = pygame.Rect(
                        grid_start_x + j * letter_size,
                        grid_start_y + i * letter_size,
                        letter_size - 5, letter_size - 5
                    )
                    pygame.draw.rect(self.screen, self.BUTTON_COLOR, rect, border_radius=8)
                    pygame.draw.rect(self.screen, self.ACCENT_COLOR, rect, 2, border_radius=8)

                    # Отображаем буквы
                    if i < current_attempt:
                        if j < len(guesses[i]):
                            # Проверяем правильность буквы
                            if guesses[i][j] == secret_word[j]:
                                color = (144, 238, 144)  # Светло-зеленый - правильная позиция
                            elif guesses[i][j] in secret_word:
                                color = (255, 255, 153)  # Желтый - есть в слове
                            else:
                                color = (211, 211, 211)  # Серый - нет в слове

                            pygame.draw.rect(self.screen, color, rect, border_radius=8)
                            self.draw_text(guesses[i][j], self.font_small, self.TEXT_COLOR,
                                           rect.centerx, rect.centery)
                    elif i == current_attempt and j < len(current_guess):
                        self.draw_text(current_guess[j], self.font_small, self.TEXT_COLOR,
                                       rect.centerx, rect.centery)

            # Кнопка назад
            back_rect = self.draw_button("Меню", self.screen_width // 2, 550)

            # Отображение результата
            if game_over:
                if current_attempt < attempts and guesses[current_attempt - 1] == secret_word:
                    text = "Поздравляем! Вы угадали!"
                else:
                    text = f"Правильное слово: {secret_word}"

                self.draw_text(text, self.font_small, self.ACCENT_COLOR,
                               self.screen_width // 2, 80)
                restart_rect = self.draw_button("Играть снова", self.screen_width // 2, 455)

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if back_rect.collidepoint(mouse_pos):
                        running = False

                    if game_over and "restart_rect" in locals():
                        if restart_rect.collidepoint(mouse_pos):
                            # Сброс игры
                            return self.run_wordle()

                if not game_over and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(current_guess) == word_length:
                        guesses[current_attempt] = current_guess
                        current_attempt += 1

                        if current_guess == secret_word or current_attempt >= attempts:
                            game_over = True

                        current_guess = ""
                    elif event.key == pygame.K_BACKSPACE:
                        current_guess = current_guess[:-1]
                    elif event.unicode.isalpha() and len(current_guess) < word_length:
                        current_guess += event.unicode.lower()

            pygame.display.flip()

        self.state = "game_selection"

    def run_memory_game(self):
        """Игра 'Найди пары'"""
        symbols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        card_values = symbols * 2  # Создаем пары
        random.shuffle(card_values)
        card_width, card_height = 120, 80
        margin = 20
        grid_width = 4
        grid_height = 4
        total_width = grid_width * (card_width + margin) - margin
        total_height = grid_height * (card_height + margin) - margin
        start_x = (self.screen_width - total_width) // 2
        start_y = (self.screen_height - total_height) // 2 - 30

        cards = []
        for i in range(grid_height):
            for j in range(grid_width):
                idx = i * grid_width + j
                if idx < len(card_values):
                    card = {
                        'value': card_values[idx],
                        'rect': pygame.Rect(
                            start_x + j * (card_width + margin),
                            start_y + i * (card_height + margin),
                            card_width, card_height
                        ),
                        'revealed': False,
                        'solved': False
                    }
                    cards.append(card)

        selected = None
        pairs_found = 0
        game_over = False
        waiting = False

        running = True
        while running:
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(self.BG_COLOR)

            # Заголовок
            self.draw_text("Найди пары", self.font_medium, self.ACCENT_COLOR,
                           self.screen_width // 2, 50)

            # Рисуем карточки
            for card in cards:
                if card['solved']:
                    color = (200, 255, 200)
                elif card['revealed']:
                    color = (255, 255, 200)
                else:
                    color = self.BUTTON_COLOR
                pygame.draw.rect(self.screen, color, card['rect'], border_radius=15)
                pygame.draw.rect(self.screen, self.ACCENT_COLOR, card['rect'], 3, border_radius=15)
                if card['revealed'] or card['solved']:
                    self.draw_text(card['value'], self.font_medium, self.TEXT_COLOR,
                                   card['rect'].centerx, card['rect'].centery)
                else:
                    pygame.draw.circle(self.screen, self.ACCENT_COLOR, card['rect'].center, 30, 3)

            back_rect = self.draw_button("Меню", self.screen_width // 2, 550)

            # Проверка завершения игры
            if pairs_found == len(symbols):
                game_over = True
                self.draw_text("Вы нашли все пары!", self.font_medium, self.ACCENT_COLOR,
                               self.screen_width // 2, 410)
                restart_rect = self.draw_button("Начать снова", self.screen_width // 2, 475)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if back_rect.collidepoint(mouse_pos):
                        running = False
                    if game_over and "restart_rect" in locals() and restart_rect.collidepoint(mouse_pos):
                        # Сброс игры через рестарт
                        return self.run_memory_game()
                if not game_over and event.type == pygame.MOUSEBUTTONDOWN and not waiting:
                    for card in cards:
                        if not card['revealed'] and not card['solved'] and card['rect'].collidepoint(mouse_pos):
                            card['revealed'] = True
                            if selected is None:
                                selected = card
                            else:
                                if selected['value'] == card['value']:
                                    selected['solved'] = True
                                    card['solved'] = True
                                    pairs_found += 1
                                    selected = None
                                else:
                                    waiting = True
                                    pygame.time.set_timer(pygame.USEREVENT, 500)
                if event.type == pygame.USEREVENT and waiting:
                    for card in cards:
                        if card['revealed'] and not card['solved']:
                            card['revealed'] = False
                    selected = None
                    waiting = False
                    pygame.time.set_timer(pygame.USEREVENT, 0)

            pygame.display.flip()

        self.state = "game_selection"

    def quit_game(self):
        """Корректное завершение игры"""
        self.running = False
        pygame.quit()
        sys.exit()

    def run(self):
        """Основной цикл программы"""
        while self.running:
            if self.state == "main_menu":
                self.main_menu()
            elif self.state == "game_selection":
                self.game_selection()
            elif self.state == "music_selection":  # <-- Добавить эту строку
                self.music_selection()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    hub = CuteGameHub()
    hub.run()