import console


class TicTacToe():
    def __init__(self):
        self.player = 1 # Player can be 1 or -1
        self.score = {-1: 0, 1: 0}
        self.symbols = ["⬜️", "❌", "⭕️"]
        self.board = self.clear_board()
        self.winner = None
        self.game_on = True
        print(f'TIC TAC TOE\n{self.player} begins.')
        self.start()

    def game_over(self):
        # all winning cell combos
        wins = [
            ['a1', 'b1', 'c1'], ['a2', 'b2', 'c2'], ['a3', 'b3', 'c3'], # rows
            ['a1', 'a2', 'a3'], ['b1', 'b2', 'b3'], ['c1', 'c2', 'c3'], # columns
            ['a1', 'b2', 'c3'], ['a3', 'b2', 'c1']                      # diagonals
        ]

        if all(self.board.values()): # No moves/ zeros left
            print(f"Game over. That's a draft.")
            return True
        else:
            for (a, b, c) in wins:
                if self.board[a] == self.board[b] == self.board[c] and self.board[a] != 0:
                    self.winner = self.board[a]
                    self.score[self.winner] += 1
                    print(f'{self.symbols[self.winner]} wins!')
                    self.print_score()
                    return True
        return False

    def clear_board(self):
        return dict((cell, 0) for cell in ['a1','b1','c1','a2','b2','c2','a3','b3','c3'])

    def start(self):
        # Winner start new match or player switch
        if self.winner:
            self.player = self.winner # winner starts a rematch

        # reset
        self.winner = None
        self.board = self.clear_board()
        console.clear()
        self.print_board()

    def print_score(self):
        print(f'\nScore [{self.symbols[-1]}: {self.score[-1]} | {self.symbols[1]}: {self.score[1]}]')

    def quit(self):
        self.game_on = False
        print("Good buy!")

    def players_move(self):
        # keep asking if answer is invalid
        chosen_cell = None
        while not chosen_cell:
            cell_code = input(f'\n{self.symbols[self.player]}, chose a cell:_').lower().strip()
            
            # reverse if number is first, letter second
            if len(cell_code) == 2 and cell_code[0].isdigit() and cell_code[1].isalpha():
                cell_code = cell_code[::-1]

            # check if cell is empty
            cell = self.board.get(cell_code)
            if cell:
                print("Sorry, chose an empty cell.")
            else:
                chosen_cell = cell_code

        # set move and switch players
        self.board[chosen_cell] = self.player
        self.player *= -1
        return

    def print_board(self):
        print(
            f"  a  b  c ",
            f"1 {self.symbols[self.board['a1']]} {self.symbols[self.board['b1']]} {self.symbols[self.board['c1']]}",
            f"2 {self.symbols[self.board['a2']]} {self.symbols[self.board['b2']]} {self.symbols[self.board['c2']]}",
            f"3 {self.symbols[self.board['a3']]} {self.symbols[self.board['b3']]} {self.symbols[self.board['c3']]}",
            sep='\n'
        )

    def quit_or_rematch(self):
        options = {'n': self.quit, 'y': self.start}
        decision = input('\nDo you wanna play again? [Y]es or [N]o_').strip().lower()

        # keep asking if answer is invalid
        while decision not in options.keys():
            decision = input('Type [q] to quit or [p] to play again:_').strip().lower()
        options[decision]()


if __name__ == "__main__":
    game = TicTacToe()

    while game.game_on:
        game.players_move()
        console.clear()
        game.print_board()
        if game.game_over():
            game.quit_or_rematch()
