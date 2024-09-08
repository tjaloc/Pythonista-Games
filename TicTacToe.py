import console


class TicTacToe():
    def __init__(self):
        self.player1 = 'X'
        self.player2 = 'O'
        self.empty = ' '
        self.board = self.clear_board()
        self.current_player = self.player1
        self.next_player = self.player2
        self.winner = None
        self.game_on = True
        self.score = {self.player2: 0, self.player1: 0}
        print(f'TIC TAC TOE\n{self.current_player}-Player begins.')
        self.start()

    def game_over(self):
        if self.empty not in self.board.values(): # No moves left
            print(f"Game over. That's a draft.")
            return True
        else:
            wins = [
                ['a1', 'b1', 'c1'], ['a2', 'b2', 'c2'], ['a3', 'b3', 'c3'], # rows
                ['a1', 'a2', 'a3'], ['b1', 'b2', 'b3'], ['c1', 'c2', 'c3'], # columns
                ['a1', 'b2', 'c3'], ['a3', 'b2', 'c1']                      # diagonals
            ]
            for (a, b, c) in wins:
                if (self.board[a] == self.board[b] == self.board[c]) and (self.board[a] != self.empty):
                    self.winner = self.board[a]
                    self.score[game.winner] += 1
                    print(f'{game.winner}-Player wins!')
                    self.print_score()
                    return True
        return False

    def clear_board(self):
        return dict((cell, self.empty) for cell in ['a1','b1','c1','a2','b2','c2','a3','b3','c3'])

    def start(self):
        if self.winner: self.current_player = self.winner # winner starts a rematch
        if self.current_player == self.player1:
            self.next_player = self.player2
        else:
            self.next_player = self.player1

        self.winner = None
        self.board = self.clear_board()
        console.clear()
        self.print_board()


    def print_score(self):
        print(f'Score [{self.player2}: {self.score[self.player2]} {self.player1}: {self.score[self.player1]}]')


    def quit(self):
        self.game_on = False
        print("Good buy!")


    def players_move(self):
        # keep asking if answer is invalid
        while True:
            cell_code = input(f'{self.current_player}-player, chose a cell:_').lower().strip()
            
            # reverse if number is first, letter second
            if len(cell_code) == 2 and cell_code[0].isdigit() and cell_code[1].isalpha():
                cell_code = cell_code[::-1]
                
            cell = self.board.get(cell_code)
            if not cell or cell != self.empty:
                print("Sorry, move isn't valid.")
                continue
            else:
                self.board[cell_code] = self.current_player
                self.current_player, self.next_player = self.next_player, self.current_player
                return


    def print_board(self):
        print(
            f"    a   b   c ",
            f"──┼───┼───┼───┤ ",
            f"1 | {self.board['a1']} | {self.board['b1']} | {self.board['c1']} |",
            f"──┼───┼───┼───┤ ",
            f"2 | {self.board['a2']} | {self.board['b2']} | {self.board['c2']} |",
            f"──┼───┼───┼───┤ ",
            f"3 | {self.board['a3']} | {self.board['b3']} | {self.board['c3']} |",
            f"──┴───┴───┴───┘", sep='\n'
        )


    def quit_or_rematch(self):
        options = {'q': self.quit, 'p': self.start}
        decision = input('Do you wanna [q]uit or [p]lay again?_').strip().lower()

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
