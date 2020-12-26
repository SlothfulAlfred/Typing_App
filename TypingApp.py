import pygame
import random
from english_words import english_words_alpha_set as all_words

all_words = list(all_words)

pygame.init()
screen = pygame.display.set_mode((800,400))
clock = pygame.time.Clock()

# defining fonts
font = pygame.font.SysFont("courier", 20)
mistake_font = pygame.font.SysFont("courier", 20)
mistake_font.underline = True
title = pygame.font.SysFont("Calibri", 28)

# game variables
first_key_down = True
correct_chars = 0
mistakes = 0
time_remaining = 60
capital = False
active = True

# User events
GAME_OVER = pygame.USEREVENT
TIME_UPDATE = pygame.USEREVENT + 1

# function to check input
def correct_input(event):
    current = text.find_current()
    current = ord(text.lines[current[0]].char_list[current[1]])
    typed = int(event.key)
    # breaks out of function if input is not a letter from the alphabet or space
    if not (97 <= typed <= 122 or typed == 32):
        return False

    # deals with the special case of spaces
    if typed == 32:
        if typed == current:
            return True
        return False

    # adjusts for capital and deals with normal case
    if capital == True:
        typed -= 32
    if current == typed:
        return True
    return False

def game_over():
    cpm = correct_chars - mistakes
    wpm = int(cpm / 5)
    accuracy = int(correct_chars / (mistakes + correct_chars) * 100)
    cpm_text = title.render(f"Your CPM (Characters per minute): {cpm}", True, (255, 255, 255))
    wpm_text = title.render(f'Your WPM (Words per minute): {wpm}', True, (255, 255, 255))
    acc_text = title.render(f"Your accuracy was {accuracy}%", True, (255, 255, 255))
    return cpm_text, wpm_text, acc_text



class LINE:
    def __init__(self):
        # min number of character per line
        self.min_chars = 52
        # list of characters in the line, including spaces
        self.char_list = []
        # list of colors of each character
        self.color_list = []

        # filling up char_list with random words followed by a space
        while len(self.char_list) <= self.min_chars:
            word = random.choice(all_words)
            for letter in word:
                self.char_list.append(letter)
            self.char_list.append(' ')

        self.check()

        # filling color list with default value 
        for x in range(len(self.char_list)):
            self.color_list.append((255,255,255))

    def draw_text(self, y_pos):
        x_pos = 50
        for i in range(len(self.char_list)):
            if self.color_list[i] == (255, 0, 0):
                rendered = mistake_font.render(self.char_list[i], True, self.color_list[i])
            else:
                rendered = font.render(self.char_list[i], True, self.color_list[i])
            screen.blit(rendered, (x_pos, y_pos))
            x_pos += 12

    def check(self):
        if len(self.char_list) > 60:
            self.char_list.clear()
            self.__init__()


class TEXT:
    def __init__(self, num_of_lines):
        self.lines = []
        # number of inputted characters
        self.inputted = 0
        # index of line displayed at top of text block
        self.top_index = 0
        # index of line displayed at bottom of text block
        self.bottom_index = 7
        # y position of bottom text block
        self.y_pos = 50

        # filling up list of lines
        for i in range(num_of_lines):
            self.lines.append(LINE())

    def draw_text(self):
        line = self.top_index
        y = self.y_pos
        while line <= self.bottom_index:
            self.lines[line].draw_text(y)
            y += 32
            line += 1

    def find_current(self) -> tuple:
        inputted = self.inputted
        for line in range(len(self.lines)):
            for letter in range(len(self.lines[line].char_list)):
                if inputted <= 0:
                    return line, letter
                inputted -= 1

        # returns None if all letters have been typed 
        return None

    def change_color(self, color='white'):
        # find current character's line and letter index
        changed = self.find_current()
        if color == 'white':
            new_color = (255, 255, 255)
        elif color == 'red':
            new_color = (255, 0, 0)
        elif color == 'green':
            new_color = (0, 255, 0)
        else:
            new_color = (255, 255, 255)
        # assigns the new color the current character
        self.lines[changed[0]].color_list[changed[1]] = new_color

    def is_mistake(self):
        char_pos = self.find_current()
        char_color = self.lines[char_pos[0]].color_list[char_pos[1]]
        if char_color == (255, 0, 0):
            return True
        return False

    def update(self):
        self.top_index = self.inputted // 60
        self.bottom_index = self.top_index + 7

text = TEXT(20)

running = True
while running:
    screen.fill((0,0,0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == GAME_OVER:
            active = False
            end_screen_text = game_over()

        if active:
        # does not run when game has ended
            if event.type == TIME_UPDATE:
                time_remaining -= 1

            if event.type == pygame.KEYDOWN:
                if first_key_down:
                     pygame.time.set_timer(GAME_OVER, 60000)
                     pygame.time.set_timer(TIME_UPDATE, 1000)
                     first_key_down = False

                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT or event.key == pygame.K_CAPSLOCK:
                    capital = True

                elif event.key == pygame.K_BACKSPACE:
                    text.inputted -= 1
                    if text.is_mistake():
                        mistakes -= 1
                    else:
                        correct_chars -= 1
                    text.change_color('white')
                
                else:
                    correct = correct_input(event)
                    if correct:
                        text.change_color('green')
                        correct_chars += 1
                    else:
                        text.change_color('red')
                        mistakes += 1
                    text.inputted += 1

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT or event.key == pygame.K_CAPSLOCK:
                    capital = False

    if active:
        # displaying scoreboard
        scoreboard = title.render(f"Correct: {correct_chars}   Mistakes: {mistakes}   Time: {time_remaining}", True, (255, 255, 255))
        screen.blit(scoreboard, (25, 10))

        # displaying text 
        text.draw_text()
        text.update()

    else:
        # displaying end screen
        screen.blit(end_screen_text[0], (50, 100))
        screen.blit(end_screen_text[1], (50, 150))
        screen.blit(end_screen_text[2], (50, 200))

    # updating screen and limiting framerate
    pygame.display.update()
    clock.tick(250)