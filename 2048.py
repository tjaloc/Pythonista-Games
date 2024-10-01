""" Game 2048

2048 is a simple puzzle game. Swipe right, left, up and down to move all tiles.
Tiles with the same number merge into one, doubling their value and a new tile (2 or 4) appears
randomly in an empty spot on the grid. You win when you reach 2048. You lose when there are no
more valid moves.

"""

from math import log2
from colorsys import hsv_to_rgb
import random
import numpy as np
from scene import *
import ui
import sound


DARK = '#3b3736'
BRIGHT = 'whitesmoke'
FONT = 'Helvetica-bold'
BREAKPOINT = 500

class Tile:
    def __init__(self, tile, label, row, col):
        self.tile = tile
        self.label = label
        self.row = row
        self.col = col


class Game(Scene):
    def setup(self):
        self.initialized = False
        
        # dimensions
        self.get_sizes()
        
        # Elements
        self.background_color = DARK
        self.tiles = []
        self.create_tiles()
        self.create_menu()
        
        # Sound toggle
        self.mute = False
        self.mute_toggle = SpriteNode('typb:Unmute', position=(32, self.size.h - 36), parent=self)
        
        # Start with two tiles
        self.game_over = False
        self.start_game()
        
    def get_sizes(self):
        self.screen_w, self.screen_h = get_screen_size()
        self.center_x, self.center_y = self.screen_w / 2, self.screen_h / 2
        self.matrix = int(0.9 * min(self.screen_w, self.screen_h))
        self.square = int(0.22 * self.matrix)
        self.gap = int(0.04 * self.matrix)
        self.border_radius = int(0.02 * self.matrix)
        self.menu_w = self.square * 4
        self.menu_h = self.square * 2
        self.font_size = 45 if min(self.screen_w, self.screen_h) > BREAKPOINT else 28
    
    def create_menu(self):
        self.menu = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, self.menu_w, self.menu_h, 2 * self.border_radius),
            fill_color=BRIGHT,
            alpha=0,
            position=(self.center_x, self.center_y),
            parent=self
        )
        
        self.menu_label = LabelNode(
            'Game Over', 
        font=(FONT, self.font_size * 1.5),
            color=DARK,
            alpha=1,
            position=(0, self.menu_h // 4),
        parent=self.menu
        )
        
        self.play_btn = self.create_menu_button(
            text='Play again',
            position=(self.menu_w // 4, -self.menu_h // 4),
            )
        self.quit_btn = self.create_menu_button(
            text='Quit',
            position=(-self.menu_w // 4, -self.menu_h // 4),
            )
        
    def create_menu_button(self, text, position):
        width = int(self.menu_w / 2.2)
        height = int(self.menu_h / 2.4)
        btn = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, width, height, self.border_radius),
            fill_color=DARK,
            position=position,
            parent=self.menu
        )
        
        LabelNode(
            text,
            font=(FONT, self.font_size * .9),
            color=BRIGHT,
            alpha=1,
            parent=btn
        )
        return btn
                
    def create_tiles(self):
        start_x = (self.screen_w - self.matrix) // 2
        start_y = (self.screen_h - self.matrix) // 2

        for i in range(4*4):
            r, c = divmod(i, 4)
            x = start_x + c * (self.square + self.gap)
            y = start_y + r * (self.square + self.gap)

            # create tile node
            tile = ShapeNode(
                path=ui.Path.rounded_rect(x, y, self.square, self.square, self.border_radius),
                fill_color=BRIGHT,
                stroke_color='clear',
                position=(x + self.square//2, y + self.square//2),
                parent=self
                )

            # create tile label
            label = LabelNode(
                '',
                font=(FONT, self.font_size),
                parent=tile
                )

            # store tile and label in list to reference
            self.tiles.append(Tile(tile, label, r, c))

    def collapse(self, sequence):
        # remove zeros
        sequence = [num for num in sequence if num > 0]
        seq = []

        # check and remove
        while sequence:
            if len(sequence) == 1:
                # last item
                seq.append(sequence[0])
                sequence = []
            elif sequence[0] == sequence[1]:
                # merge equal numbers
                seq.append(sequence[0] + sequence[1])
                sequence = sequence[2:]
            else:
                seq.append(sequence[0])
                sequence = sequence[1:]

        # pad with zeros
        return seq + [0] * (4 - len(seq))

    def swipe_direction(self, touch_start, touch_end):
        if not touch_start or not touch_end:
             return

        xd, yd = np.subtract(touch_end, touch_start)
        return (
            'right' if abs(xd) > abs(yd) and xd > 0 else
            'left'  if abs(xd) > abs(yd) else
            'up'    if yd > 0 else
            'down'  if yd < 0 else
            False
        )

    def swipe(self, direction):
        board_swiped = np.copy(self.board)

        if direction in ['right', 'left']:
            flip = direction == 'right'
            for i in range(4):
                row = np.flip(self.board[i, :]) if flip else self.board[i, :]
                new_row = self.collapse(row)
                board_swiped[i, :] = np.flip(new_row) if flip else new_row

        elif direction in ['up', 'down']:
            flip = direction == 'up'
            for i in range(4):
                col = np.flip(self.board[:, i]) if flip else self.board[:, i]
                new_col = self.collapse(col)
                board_swiped[:, i] = np.flip(new_col) if flip else new_col

        # check if anything has changed, invalid swipes shouldn't result in new tiles
        if not np.array_equal(board_swiped, self.board):
            self.board = board_swiped
            return True

    def add_new_tile(self):
        free_cells = np.argwhere(self.board == 0)
        if free_cells.size > 0:
            r, c = random.choice(free_cells)
            self.board[r, c] = random.choice([2,4])

    def get_color(self, num, start_hue=0.3, sat=0.6, vib=0.7):
        if num == 0:
            return BRIGHT

        hue = (log2(num) * 0.1 + start_hue) % 1
        return hsv_to_rgb(hue, sat, vib)

    def update(self):
        if not self.initialized or self.game_over:
            return

        # Update tiles and labels
        for tile in self.tiles:
            num = self.board[tile.row, tile.col]
            tile.tile.fill_color = self.get_color(num)
            tile.label.text = str(num) if num > 0 else ''

        # Check game status
        if self.win() or self.no_more_moves():
            self.menu_label.text = 'You win!' if self.win() else 'Game Over'
            self.menu.alpha = 0.9
            self.game_over = True

    def no_more_moves(self):
        for r in range(4):
            for c in range(4):
                current = self.board[r, c]

                # empty  cells 
                if current == 0:
                    return False

                # similar neighbours
                if c < 3 and self.board[r, c+1] == current:
                    return False
                if r < 3 and self.board[r+1, c] == current:
                    return False

        return True

    def win(self):
        return 2048 in self.board

    def quit_game(self):
        self.menu_label.text = 'Good Bye'
        self.run_action(Action.sequence(Action.wait(1), Action.call(self.view.close)))

    def start_game(self):
        self.board = np.zeros((4,4), dtype=int)
        for _ in range(2):
            self.add_new_tile()
        self.menu.alpha = 0
        self.game_over = False
        self.initialized = True

    def touch_began(self, touch):
        self.start_xy = touch.location

    def touch_ended(self, touch):
        # mute toggle
        if self.mute_toggle.frame.contains_point(touch.location):
            self.mute = not self.mute
            self.mute_toggle.texture = Texture(['typb:Unmute', 'typb:Mute'][self.mute])

        # game over menu
        if self.game_over:
            menu_touch = self.menu.point_from_scene(touch.location)
            if self.quit_btn.frame.contains_point(menu_touch):
                self.quit_game()
            elif self.play_btn.frame.contains_point(menu_touch):
                self.start_game()

        # swipe tiles
        direction = self.swipe_direction(self.start_xy, touch.location)
        if direction:
            if self.swipe(direction):
                if not self.mute:
                    sound.play_effect('8ve:8ve-tap-toothy')
                self.add_new_tile()

        # reset touch start
        self.start_xy = None

    
if __name__ == '__main__':
    game = Game()
    run(game)
