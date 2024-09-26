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


DARK = '#303030'
LIGHT = '#ffffff'
BORDER_W = 20 if min(get_screen_size()) >= 600 else 10 # breakpoint for iPad/iPhone
SIZE = 3
FONT = ('<System-Bold>', 20)
IMG_DIR = 'img'

class Puzzle(Scene):
    def setup(self):
        # Status
        self.initialized = False
        self.solved = False
        self.muted = False

        # Dimensions
        self.w, self.h = get_screen_size()
        self.puzzle_w = int(0.7 * min(self.w, self.h))
        self.tile_w = self.puzzle_w // SIZE
        self.start_x = - SIZE/2 * self.tile_w + self.tile_w/2
        self.start_y = SIZE/2 * self.tile_w - self.tile_w/2
        
        # Elements
        self.root_node = Node(parent=self)
        self.background_color = DARK
        self.puzzle_frame = ShapeNode(
            parent=self.root_node,
            fill_color=LIGHT,
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
        
        self.new_puzzle()

    def save_texture(self, texture):
        """ Save tile texture under random name. This ensures no old texture will be loaded from cache.
        Player get a new photo each game.
        """
        if not os.path.exists(IMG_DIR):
            os.mkdir(IMG_DIR)
        filename = f'img/{random.randint(1, 1_000_000):0>7}.png'
        texture.save(filename)

        return filename
        
    def get_image(self):
        """Download photo from https://picsum.photos, slice it to tile size.
        Create tile nodes and store as property tile_list.
        """
        r = requests.get(f'https://picsum.photos/{self.puzzle_w}/{self.puzzle_w}?greyscale')
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content))
            img.load()
            
            for row in range(SIZE):
                for col in range(SIZE):
                    nr = row * SIZE + col
                    
                    x0 = col * self.tile_w
                    x1 = x0 + self.tile_w
                    y0 = row * self.tile_w
                    y1 = y0 + self.tile_w

                    texture = img.crop((x0, y0, x1, y1))
                    texture_filename = self.save_texture(texture)
                    
                    rect = ui.Path.rounded_rect(0, 0, self.tile_w, self.tile_w, BORDER_W/2)
                    tile = ShapeNode(
                        path=rect,
                        fill_color=None,
                        stroke_color=LIGHT,
                        parent=self.puzzle_frame,
                        alpha=nr > 0, # tile 0 is empty / invisible with alpha = 0
                        position=(self.tile_w/2, self.tile_w/2),
                        )
                        
                    img_slice = SpriteNode(
                        texture_filename,  
                        parent=tile,
                        blend_mode=ui.BLEND_MULTIPLY, # crops rounded corners of image
                        )
                    tile.cell = nr
                    self.tile_list.append(tile)
        
    def shuffle_puzzle(self):
        """ Perform moves to shuffle the board.
            Why not random? The smaller the board the higher the risk of unsolveability.
        """
        neighbours = [ +1, -1, + SIZE, - SIZE]
        for _ in range(SIZE ** 2 * 2):
            neighbour = random.choice(
                [tile for tile in self.tile_list if any(
                    tile.cell + n == self.zero.cell for n in neighbours)])
            self.zero.cell, neighbour.cell = neighbour.cell, self.zero.cell
            
    def place_tiles(self):
        """Place tiles on board.
        Starting point is top left.
        """
        for tile in self.tile_list:
            r, c = divmod(tile.cell, SIZE)
            x = self.start_x + c * self.tile_w
            y = self.start_y - r * self.tile_w
            tile.position = (x, y)
        
    def touched_tile(self, touch):
        """Match touch location to tiles and return tile (node).
        """
        for nr, tile in enumerate(self.tile_list):
            xy = self.puzzle_frame.point_from_scene(touch.location)
            if tile.frame.contains_point(xy):
                return tile
            
    def touch_ended(self, touch):
        """Perform action connected to touched node.
        mute_btn:       switch Sound on / off
        new_puzzle_btn: start new game
        touched_tile:   move tile to empty cell
        """
        # mute toggle
        if self.mute_btn.frame.contains_point(touch.location):
            self.muted = not self.muted
            self.mute_btn.texture = Texture('typw:Unmute') if self.muted else Texture('typw:Mute')
            return
            
        # refresh
        if self.new_puzzle_btn.frame.contains_point(touch.location):
            self.refresh()
            return
            
        # shift tile into empty cell
        tile = self.touched_tile(touch)
        if not tile: return
        
        if self.is_neighbour(tile) and not self.solved:
            self.zero.cell, tile.cell = tile.cell, self.zero.cell
            self.place_tiles()
            self.move_counter += 1
            
            if not self.muted: sound.play_effect('8ve:8ve-tap-hollow')
            return
            
    def is_neighbour(self, tile):
        """return True if tile is direct neighbour of empty cell
        """
        return any([
            tile.cell == self.zero.cell + 1, 
            tile.cell == self.zero.cell - 1, 
            tile.cell == self.zero.cell + SIZE, 
            tile.cell == self.zero.cell - SIZE
            ])
        
    def update(self):
        """update Scene if game is initialized.
        Stop game if puzzle is solved.
        """
        if not self.initialized:
            return
        
        self.place_tiles()
        
        if self.puzzle_solved():
            for tile in self.tile_list:
                tile.alpha = 1
            self.solved = True
    
    def puzzle_solved(self):
        """Return True if all tiles are in their original cell"""
        return all(i == tile.cell for i, tile in enumerate(self.tile_list))
        
    def refresh(self):
        """ Remove tile nodes from parent to avoid duplicates, old tiles in new game.
        """
        for tile in self.tile_list:
            tile.remove_from_parent()
        self.new_puzzle()
            
    def new_puzzle(self):
        """Set up for new game. Delete old stuff. Reset all status, create, shuffle and place new tiles
        """
        # delete old textures
        textures = glob.glob(os.path.join('img', '*.png'))
        for texture in textures:
            os.remove(texture)
            
        self.tile_list = []
        self.current = None
        self.touch_start = None
        self.move_counter = 0
        self.get_image()
        self.zero = self.tile_list[0]
        self.shuffle_puzzle()
        self.place_tiles()
        self.solved = False
        self.initialized = True
        
    
if __name__ == '__main__':
    game = Puzzle()
    run(game)
    
