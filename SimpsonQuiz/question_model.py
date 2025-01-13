import random


simpsons_characters = [
    "Homer Simpson",
    "Marge Simpson",
    "Bart Simpson",
    "Lisa Simpson",
    "Maggie Simpson",
    "Abe Simpson",
    "Ned Flanders",
    "Mr. Burns",
    "Waylon Smithers",
    "Krusty the Clown",
    "Chief Wiggum",
    "Apu Nahasapeemapetilon",
    "Milhouse Van Houten",
    "Edna Krabappel",
    "Patty Bouvier",
    "Selma Bouvier",
    "Ralph Wiggum",
    "Comic Book Guy",
    "Lenny Leonard",
    "Carl Carson",
    "Dr. Nick",
    "Frank Grimes",
    "Troy McClure",
    "Moe Szyslak",
    "Duffman",
    "Rainier Wolfcastle",
    "Principal Skinner",
    "Mayor Quimby",
]

class Question:
  def __init__(self, quote, name, image):
      self.quote = quote
      self.name = name
      self.image = image
      self.options = self.get_options()
      
  def get_options(self) -> dict:
    others = [char for char in simpsons_characters if char != self.name]
    options = random.sample(others, 3) + [self.name]
    random.shuffle(options)
    
    return dict(zip('abcd', options))
    

