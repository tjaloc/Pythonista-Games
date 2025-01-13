class QuizMaster:
  def __init__(self, questions: list):
    self.questions = questions
    self.current_question = None

  def check_answer(self, user_answer: str) -> bool:
    return self.current_question.options.get(user_answer, None) == self.current_question.name

  def next_question(self):
    self.current_question = self.questions.pop()
    
    block = 47*'-'
    quote = self.current_question.quote
    question = f"Who said:\n{block}\n»{quote}«\n{block}\n"
    options = '\n'.join([f'\t{key}) {val}' for key, val in self.current_question.options.items()])
    
    return question + options + 2*'\n'

  def has_questions(self):
    return bool(self.questions)
