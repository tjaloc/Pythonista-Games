import console
import requests
from io import BytesIO
from PIL import Image

from api_handler import SimpsonsAPI
from quizmaster import QuizMaster
from question_model import Question


def print_quiz_title(num=0):
  print(
    'THE SIMPSONS QUIZ', 
    f'Question #{num}' if num else '', 
    sep='\n', end=2*'\n')

def get_answer(question, options='abcd'):
  while True:
    answer = input(question).strip().lower()
    if answer in options:
      return answer
    else:
      # Feedback
      opts = ', '.join(list(options))
      opts.replace(f', {options[-1]}', f' or {options[-1]}')
      print(f'Please answer with {opts}.\n\n')
  
def show_image(link):
  r = requests.get(link)

  if r.status_code == 200:
    img = Image.open(BytesIO(r.content))
    w, h = img.size
    scale = 200 / max(w, h) 
    img = img.resize((int(w * scale), int(h * scale)))
    img.show()
  
def get_question_bank(n):
  api = SimpsonsAPI()
  api.get_quotes()
  question_bank = [Question(x['quote'], x['character'], x['image']) for x in api.data]
  
  return question_bank
    
def play_again():
  options = 'yn'
  q = f'Do you want to play again? [y]es or [n]o? \n'
  
  while True:
    answer = input(q).strip().lower()
    if answer in options:
      return answer == 'y'
  
if __name__ == '__main__':
  num = 5     # max quotes in api = 50
  points = 0   # count correct answers
  quotes = 0   # count questions
  
  question_bank = get_question_bank(num)
  quizmaster = QuizMaster(question_bank)
  
  while True:
    console.clear()
    
    # ask question
    question = quizmaster.next_question()
    name = quizmaster.current_question.name
    image = quizmaster.current_question.image
    quotes += 1
    print_quiz_title(quotes)
    
    # get answer and check
    answer = get_answer(question)
    correct = quizmaster.check_answer(answer)
    points += correct
    show_image(image)
    result = 'Correct' if correct else 'Wrong'
    print(f"{result}, {name} said it.\n")
    
    # how to continue
    if not quizmaster.has_questions():
      # new quiz
      if play_again():
        question_bank = get_question_bank(num)
        quizmaster = QuizMaster(question_bank)
        games += 1
      else:
        # exit
        break
    else:
      # go to next question
      input('NEXT >>>'.rjust(47))
  
  # good bye message
  console.clear()
  print_quiz_title()
  print(f"That's it. You got {points} of {quotes} quotes correct.")
  
