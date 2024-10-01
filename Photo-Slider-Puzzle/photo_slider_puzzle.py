"""Recreate those platic puzzles """

from scene import *
import sound
import ui
import requests
from PIL import Image
from io import BytesIO
import random
import os
import glob


BORDER_W = 20 if min(get_screen_size()) >= 600 else 10 # breakpoint for iPad/iPhone
MIN, MAX = 3, 8
BOARD_SIZE = MIN
IMG_DIR = 'img'

class Puzzle(Scene):
    def setup(self):
        # Status
        self.initialized = False
        self.solved = False
        self.muted = False

        # Dimensions
        self.set_dimensions()
        
        # Elements
        self.root_node = Node(parent=self)
        self.background_color = '#303030'

        self.puzzle = ShapeNode(
            parent=self.root_node,
            fill_color='white',
            position=get_screen_size()/2,
            path=ui.Path.rounded_rect(
                0, 0,
                self.puzzle_w + 2 * BORDER_W,
                self.puzzle_w + 2 * BORDER_W,
                BORDER_W
                ),
            )

        # Sound Button
        self.mute_btn = SpriteNode(
            'typw:Mute', 
            parent=self.root_node, 
            position=(40, self.h - 40),
            alpha=.2,
            )

        # Refresh Button
        self.new_puzzle_btn = SpriteNode(
            'typw:Refresh',
            position=(self.w/2, self.h/2 - self.puzzle_w/2 - 60),
            alpha=.2,
            parent=self.root_node,
            )
        
        # more / less tiles button
        self.more_tiles_btn = SpriteNode(
            'typw:Plus',
            position=(self.w/2 + self.puzzle_w/2 - 60, self.h/2 - self.puzzle_w/2 - 60),
            alpha=.2,
            parent=self.root_node,
            )

        self.less_tiles_btn = SpriteNode(
            'typw:Minus',
            position=(self.w/2 - self.puzzle_w/2 + 60, self.h/2 - self.puzzle_w/2 - 60),
            alpha=.2,
            parent=self.root_node,
            )

        self.new_puzzle()

    def set_dimensions(self):
        self.w, self.h = get_screen_size()
        self.puzzle_w = int(min(self.w, self.h) - 4 * BORDER_W)
        self.tile_w = self.puzzle_w // BOARD_SIZE
        self.start_x = - BOARD_SIZE/2 * self.tile_w + self.tile_w/2
        self.start_y = BOARD_SIZE/2 * self.tile_w - self.tile_w/2
        
    def get_image(self):
        """Download photo from https://picsum.photos, slice it to tile size.
        """
        r = requests.get(f'https://picsum.photos/{self.puzzle_w}/{self.puzzle_w}?greyscale')
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content))
            img.load()
            
            for row in range(BOARD_SIZE):
                for col in range(BOARD_SIZE):
                    nr = row * BOARD_SIZE + col
                    
                    x0 = col * self.tile_w
                    x1 = x0 + self.tile_w
                    y0 = row * self.tile_w
                    y1 = y0 + self.tile_w

                    texture = img.crop((x0, y0, x1, y1))

                    # random names to avoid img drawn from memory after refresh -> always new image
                    texture_filename = f'{random.randint(1,1_000_000):0>7}.png'
                    if not os.path.exists('img'):
                      os.mkdir('img')
                    texture_filename = os.path.join('img', texture_filename)
                    texture.save(texture_filename)
                    
                    rect = ui.Path.rounded_rect(0, 0, self.tile_w, self.tile_w, BORDER_W/2)
                    tile = ShapeNode(
                        path=rect,
                        fill_color=None,
                        stroke_color='white',
                        parent=self.puzzle,
                        alpha=nr > 0, # tile 0 is empty with alpha = 0
                        position=(self.tile_w/2, self.tile_w/2),
                        )
                        
                    img_slice = SpriteNode(
                        texture_filename,  
                        parent=tile,
                        blend_mode=ui.BLEND_MULTIPLY, # crops rounded corners of image
                        )
                    tile.cell = nr
        
    def shuffle_puzzle(self):
        """ Perform moves to shuffle the board.
            Why not random? The smaller the board the higher the risk of unsolveability.
        """
        neighbours = [ +1, -1, + BOARD_SIZE, - BOARD_SIZE]
        for _ in range(BOARD_SIZE ** 2 * 2):
            neighbour = random.choice(
                [tile for tile in self.puzzle.children if any(
                    tile.cell + n == self.zero.cell for n in neighbours)])
            self.zero.cell, neighbour.cell = neighbour.cell, self.zero.cell
            
    def place_tiles(self):
        """Place tiles on board.
        Starting point is top left.
        """
        for tile in self.puzzle.children:
            r, c = divmod(tile.cell, BOARD_SIZE)
            x = self.start_x + c * self.tile_w
            y = self.start_y - r * self.tile_w
            tile.position = (x, y)
        
    def touched_tile(self, touch):
        """Match touch location to tiles and return tile (node).
        """
        for nr, tile in enumerate(self.puzzle.children):
            xy = self.puzzle.point_from_scene(touch.location)
            if tile.frame.contains_point(xy):
                return tile
            
    def touch_ended(self, touch):
        """Perform actions connected to touched nodes.
        mute_btn :          Sound on/off
        new_puzzle_btn :    (re)start game
        touched_tile:       Shift tile to empty cell
        less_tiles_btn :    decrease amount of tiles
        more_tiles_btn:     increase amount of tiles
        """
        global BOARD_SIZE

        # more tiles
        if BOARD_SIZE < MAX and self.more_tiles_btn.frame.contains_point(touch.location):
          BOARD_SIZE += 1
          if not self.muted:
            sound.play_effect('8ve:8ve-tap-hollow')
          self.new_puzzle()

        # less tiles
        if BOARD_SIZE > MIN and self.less_tiles_btn.frame.contains_point(touch.location):
          BOARD_SIZE -= 1
          if not self.muted:
            sound.play_effect('8ve:8ve-tap-hollow')
          self.new_puzzle()

        # mute toggle
        if self.mute_btn.frame.contains_point(touch.location):
            self.muted = not self.muted
            self.mute_btn.texture = [Texture('typw:Mute'),Texture('typw:Unmute') ][self.muted]
            return
            
        # refresh
        if self.new_puzzle_btn.frame.contains_point(touch.location):
            self.new_puzzle()
            return
            
        # shift tile to empty cell
        tile = self.touched_tile(touch)
        if tile and self.is_neighbour(tile) and not self.solved:
            self.zero.cell, tile.cell = tile.cell, self.zero.cell
            
            if not self.muted: sound.play_effect('8ve:8ve-tap-hollow')
            return
            
    def is_neighbour(self, tile):
        """return True if tile is direct neighbour of empty cell
        """
        return any([
            tile.cell == self.zero.cell + 1, 
            tile.cell == self.zero.cell - 1, 
            tile.cell == self.zero.cell + BOARD_SIZE,
            tile.cell == self.zero.cell - BOARD_SIZE
            ])
        
    def update(self):
        """update Scene if game is initialized.
        Stop game when puzzle is solved.
        """
        if not self.initialized:
            return
        
        self.place_tiles()
        self.zero.alpha = self.solved = self.puzzle_solved()
    
    def puzzle_solved(self):
        """Return True if all tiles are in their original cell"""
        return all(i == tile.cell for i, tile in enumerate(self.puzzle.children))
            
    def new_puzzle(self):
        """Set up for new game. Delete old stuff. Reset all status, create, shuffle and place new tiles
        """
        for tile in self.puzzle.children:
            tile.remove_from_parent()

        # delete old texture files
        textures = glob.glob(os.path.join('img', '*[0-9].png'))
        for texture in textures:
            os.remove(texture)
            
        self.set_dimensions()
        self.get_image()
        self.zero = self.puzzle.children[0]
        self.shuffle_puzzle()
        self.place_tiles()

        # fade out tile count buttons
        self.less_tiles_btn.alpha = [.2, .05][BOARD_SIZE == MIN]
        self.more_tiles_btn.alpha = [.2, .05][BOARD_SIZE == MAX]

        self.solved = False
        self.initialized = True
        
    
if __name__ == '__main__':
    game = Puzzle()
    run(game, PORTRAIT)
