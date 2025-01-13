import requests


class SimpsonsAPI:
  def __init__(self, num: int=5):
    self.retry = 0
    self.nun = num
    self.data = None
    self.endpoint = f'http://thesimpsonsquoteapi.glitch.me/quotes?count={num}'
    
  def get_quotes(self):
    response = requests.get(
      self.endpoint, 
      timeout=2,
      )
    if response.status_code == 200:
      self.data = response.json()
      return self.data
    else:
      print('Error', response.status_code)
      return False

