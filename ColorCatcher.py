""" COLOR CATCHER GAME
Get your cranky neck and back some movement. Hold Your iPhone and replicate the given center color by moving your
cellphone around the x, y, z-axis. Each represents one value of HSV color. Once you phone's position matches a value
this value is locked and a star appears. Go get the other values. As soon as you caught all three values you get a
new color.

You can be efficient and only move your phone/ wrist or make big movements, use your arm and upper body o loosen you
stiff desk-worker physique.
"""
from scene import *
import math
import motion
import colorsys
import random 
import sound

A = Action

class ColorFinder(Scene):
  def setup(self):
    self.active = True
    self.decimal = 2
    self.wins = 0
    self.target_h, self.target_s, self.target_v = self.random_hsv()
    
    self.h, self.s, self.v = None, None, None
    self.roll, self.pitch, self.yaw = 1, 1, 1
    motion.start_updates()
    
    self.color_nodes_setup()
    self.star_nodes_setup()
      
    self.label_wins = LabelNode(
      text=f'Found: {self.wins}',
      position=(30, self.size.h -40),
      anchor_point=(0, 1),
      font=('<System>', 16),
      color='goldenrod',
      alpha=1,
      parent=self,
      )
    
  def color_nodes_setup(self):
    nodes_info = [
        { # glow
          'radius': min(self.size)/2 + 145,
          'color': colorsys.hsv_to_rgb(
            self.target_h, 
            self.target_s, 
            self.target_v), 
          'alpha': 0},
        { # search
          'radius': min(self.size)/2 + 150, 
          'color': 'black', 
          'alpha': 1},
        { # target
          'radius': min(self.size)/2, 
          'color': colorsys.hsv_to_rgb(
            self.target_h, 
            self.target_s, 
            self.target_v), 
          'alpha': 1}
    ]

    self.glow, self.search, self.target = [
      ShapeNode(
          ui.Path.oval(0, 0, info['radius'], info['radius']),
          color=info['color'],
          alpha=info['alpha'],
          position=self.size/2,
          parent=self,
          ) 
      for info in nodes_info ]
  
  def star_nodes_setup(self):
    pos_x = [-20,  0, 20]
    self.label_h, self.label_s, self.label_v = [
      LabelNode(
        text='⭐️',
        position=(x, self.search.size.h * 0.55),
        font=('<System>', 10),
        alpha=0,
        parent=self.search,
      ) for x in pos_x ]
  
  def glow_animation(self):
    self.glow.color = getattr(self.target, 'color')
    grow = A.group(
      A.scale_to(3, 0.5),
      A.fade_to(0.3, 0.5),
      )
    shrink = A.group(
      A.scale_to(1.0, 0.5),
      A.fade_to(0, 0.5),
      )
    glow_sequence = A.sequence(grow, shrink, A.call(self.reset))
    self.glow.run_action(glow_sequence)
    
  def color_correct(self):
    return all([self.h, self.s, self.v])
    
  def random_hsv(self):
    return tuple([round(
      random.uniform(1/100, 1), self.decimal) for val in 'hsv'])
  
  def get_val(self, label):
    # check if already found value
    found = getattr(self, label)
    if found: return found
    
    # formula for h/s/v values
    val_calculation = {
      'h': round(((math.degrees(self.yaw)%360) / 360), self.decimal),
      's': round(abs(abs(self.roll/math.pi) -1), 
        self.decimal),
      'v': round(abs(abs(self.pitch/(math.pi/2)) -1), self.decimal)
    }
    val = val_calculation[label]
    
    # check if target found
    if val == getattr(self, f'target_{label}'):
      sound.play_effect('ui:switch6', 0.1)
      getattr(self, f'label_{label}').alpha = 1
      setattr(self, label, val)
    
    return val
    
  def get_hsv(self):
    self.roll, self.pitch, self.yaw = motion.get_attitude()
    return colorsys.hsv_to_rgb(
      self.get_val('h'), 
      self.get_val('s'), 
      self.get_val('v'))
      
  def update(self):
    if self.active:
      self.search.color = self.get_hsv()
      
      if self.color_correct():
        self.active = False
        self.wins += 1
        self.label_wins.text = f'Found: {self.wins}'
        self.glow_animation()
        
  def new_target(self):
    self.target_h, self.target_s, self.target_v = self.random_hsv()
    self.target.color = colorsys.hsv_to_rgb(
      self.target_h, self.target_s, self.target_v)

  def reset(self):
    self.new_target()
    
    # clear hsv and switch off text labels
    self.h, self.s, self.v = None, None, None
    for label in [
      self.label_h, self.label_s, self.label_v]: 
      label.alpha=0
    
    self.active = True

if __name__ == '__main__':
  run(ColorFinder(), PORTRAIT, frame_interval=2)
  
