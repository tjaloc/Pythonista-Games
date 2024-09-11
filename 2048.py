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

class Game(Scene):
    def setup(self):
        self.initialized = False
        
        # dimensions
        self.screen_w, self.screen_h = 0, 0
        self.center_x, self.center_y = 0, 0
        self.matrix = 0
        self.square = 0
        self.gap = 0
        self.border_radius = 0
        self.fontsize = 0
        self.menu_w = 0
        self.menu_h = 0
        self.get_sizes()
        
        # Elements
        self.background_color = DARK
        self.root_node = Node(parent=self)
        self.board = None
        self.tiles = {}
        self.create_tiles()
        
        # Game Over Menu Setup
        self.menu_label = None
        self.play_btn = None
        self.quit_btn = None
        self.menu = self.create_menu()
        
        # Sound toggle
        self.mute = False
        self.mute_toggle = SpriteNode('typb:Unmute', position=(32, self.size.h - 36), parent=self)
        
        # Start with two tiles
        self.game_over = False
        self.start_game()
        
    def get_sizes(self):
        self.screen_w, self.screen_h = get_screen_size()
        self.center_x, self.center_y = self.screen_w / 2, self.screen_h / 2
        shorter_side = min(self.screen_w, self.screen_h)
        self.matrix = int(0.6 * shorter_side) if shorter_side > BREAKPOINT else int(0.6 * shorter_side)
        self.square = int(0.22 * self.matrix)
        self.gap = int(0.04 * self.matrix)
        self.border_radius = int(0.02 * self.matrix)
        self.menu_w = self.square * 6
        self.menu_h = self.square * 4
        self.font_size = 35 if shorter_side > BREAKPOINT else 20
    
    def create_menu(self):
        menu = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, self.menu_w, self.menu_h, 2 * self.border_radius),
            fill_color=BRIGHT,
            alpha=0,
            position=(self.center_x, self.center_y),
            parent=self
        )
        self.menu_label = LabelNode(
            'Game Over', 
            font=(FONT, self.font_size * 2), 
            color=DARK,
            alpha=1,
            position=(0, self.menu_h // 4),
            parent=menu
        )
        self.play_btn = self.create_button(
            parent=menu, 
            text='Play again',
            position=(self.menu_w // 4, -self.menu_h // 4),
            width=int(self.square * 2.5), 
            height=self.square
        )
        self.quit_btn = self.create_button(
            parent=menu, 
            text='Quit',
            position=(-self.menu_w // 4, -self.menu_h // 4),
            width=int(self.square * 2.5), 
            height=self.square
        )
        
        return menu
    
    def create_button(self, parent, text, position, width, height):
        btn = ShapeNode(
            path=ui.Path.rounded_rect(0, 0, width, height, self.border_radius),
            fill_color=DARK, #BTN_COLOR,
            position=position,
            parent=parent
        )
        
        LabelNode(
            text,
            font=(FONT, self.font_size),
            color=BRIGHT, #DARK,
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
                parent=self.root_node,
                )
                
            # create tile label
            label = LabelNode(
                '',
                font=(FONT, self.font_size),
                parent=tile
                )
            
            # store tile and label in dict to reference
            self.tiles[(r, c)] = {'tile': tile, 'label': label}
    
    def pad(self, sequence):
        return sequence + [0] * (4 - len(sequence))
    
    def collapse(self, sequence):
        # shift tiles to side
        seq = self.pad([num for num in sequence if num > 0])
        
        # sum equal neighbors
        i = 0
        new_seq = []
        while i < 4:
            if i < 3 and seq[i] == seq[i+1]:
                new_seq.append(sum(seq[i:i+2]))
                i += 2
            else:
                new_seq.append(seq[i])
                i += 1
        
        return self.pad(new_seq)
                
    def swipe_direction(self, touch_start, touch_end):
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
        if not self.initialized:
            return
            
        if self.game_over:
            return
        
        # Update all tiles and labels
        for (r, c), nodes in self.tiles.items():
            num = self.board[r, c]
            nodes['tile'].fill_color = self.get_color(num)
            nodes['label'].text = str(num) if num > 0 else ''
        
        # Check game status
        if self.win() or self.no_more_moves():
            self.menu_label.text = 'You win!' if self.win() else 'Game Over'
            self.menu.alpha = 0.9
            self.game_over = True
            
    def no_more_moves(self):
        if 0 in self.board:
            return False
        
        for i in range(4*4):
            r, c = divmod(i, 4)
            current = self.board[r, c]
            if (r < 3 and self.board[r+1, c] == current) or (c < 3 and self.board[r, c+1] == current):
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
        if self.touched_node(self.mute_toggle, touch.location):
            self.mute = not self.mute
            self.mute_toggle.texture = Texture(['typb:Unmute', 'typb:Mute'][self.mute])
        
        # game over menue
        if self.game_over:
            if self.touched_node(self.quit_btn, touch.location):
                self.quit_game()
            elif self.touched_node(self.play_btn, touch.location):
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

    def touched_node(self, node, touch) -> bool:
        touch_x, touch_y = touch
        scene_x, scene_y = node.point_to_scene((0, 0))
        node_w, node_h = node.size
        
        return (
            scene_x - node_w/2 <= touch_x <= scene_x + node_w/2 and \
            scene_y - node_h/2 <= touch_y <= scene_y + node_h/2
        )
    
if __name__ == '__main__':
    game = Game()
    run(game)
    
