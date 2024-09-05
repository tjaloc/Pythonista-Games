""" FOUR IN A ROW -
Play the classic game with a friend in your console.
"""

import numpy as np
import console


SYMBOLS = ['⬛️', '🟠', '🔵']   # Emojis for empty cell, player 1, player 2
BOARD_SIZE = 5                # change if you like a smaller/bigger board
BOARD = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

def board_filled() -> bool:
    return not (0 in BOARD)
    
def has_4_in_a_row(sequence, player) -> bool:
    return any(all(cell == player for cell in sequence[i:i+4]) for i in range(len(sequence) - 3))
    
def get_diagonals() -> list:
    """Get all 4 item long diagonals in BOARD (global)
    """
    diagonals = []
    
    # top left to bottom right
    for row in range(BOARD_SIZE - 3): 
        for col in range(BOARD_SIZE - 3):
            diagonals.append(BOARD[[row, row+1, row+2, row+3], [col, col+1, col+2, col+3]])

    # bottom left to top right
    for row in range(3, BOARD_SIZE):  
        for col in range(BOARD_SIZE - 3):  
            diagonals.append(BOARD[[row, row-1, row-2, row-3], [col, col+1, col+2, col+3]])

    return diagonals

def is_winner(player) -> bool:
    # check rows
    for row in BOARD:
        if has_4_in_a_row(row, player):
            return True

    # check columns
    for col in range(BOARD_SIZE):
        column = BOARD[:, col]
        if has_4_in_a_row(column, player):
            return True
        
    # check diagonals
    diagonals = get_diagonals()
    for diagonal in diagonals:
        if has_4_in_a_row(diagonal, player):
            return True

    return False

def drop_coin(column: int, player: int) -> None:
    """ Try to drop a coin in the given column. If column is full recursively ask for another."""

    col = BOARD[:, column - 1]
    if 0 in col:
        row = max(i for i, cell in enumerate(col) if cell == 0)
        BOARD[row, column -1] = player
        return
    else:
        print(f'Chose another. Column {column} is full.')
        drop_coin(chose_column(player), player)

    return

def print_board():
    """Print board with SYMBOLS """
    pretty_board = np.array(
        [SYMBOLS[i] for i in BOARD.flatten()]).reshape(BOARD_SIZE, BOARD_SIZE)

    print('\n', ''.join([str(i).center(3) for i in range(1, BOARD_SIZE +1)]))
    print(*[' '.join(row) for row in pretty_board], sep='\n', end='\n')

def chose_column(player) -> int:
    """ Keep asking for a column until valid answer is given """
    while True:
        col = input(f'\n{SYMBOLS[player]} chose a column:').strip()
        if not col.isdigit():
            print(f'Chose a column between 1 and {BOARD_SIZE}')
        elif 0 < int(col) <= BOARD_SIZE:
            return int(col)

if __name__ == '__main__':
    print('4 in a row'.upper())

    game_on = True
    player = 1
    print(f'\n{SYMBOLS[player]} begins. Chose a column.')
    print_board()

    while game_on:
        
        column = chose_column(player)
        drop_coin(column, player)
        console.clear()
        print_board()

        if is_winner(player):
            print(f'\n{SYMBOLS[player]} wins.')
            game_on = False

        if board_filled():
            print('\nGame over.')
            game_on = False

        player *= -1
