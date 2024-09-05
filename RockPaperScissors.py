import random
import console

computer = 0
player = 0
options = ['👊','✋','✌️']

def chose():
    while True:
        choices = '\n'.join(f'\t[{i}] {ch}' for i, ch in enumerate(options, start=1))
        choice = input(f'Chose\n{choices}\n').strip()
        if choice.isdigit() and 0 < int(choice) <= len(options):
            return int(choice) - 1
            
            
def quit_game():
    valid_answers = 'yYnN'
    while True:
        answer = input('Do you wanna play again? [Y]es or [N]o?').strip()
        if answer in valid_answers:
            if answer.lower() == 'y':
                return False
            else:
                return True
                
def print_both(c, p):
    half = 15
    print(f'Computer [{c:^5}]'.ljust(half) + f'[{p:^5}] Player'.rjust(half), end=2*'\n')
    


if __name__ == '__main__':
    print("Let's play 'Rock Paper Scissors'\n")
    
    game_is_on = True
    while game_is_on:
        console.clear()
        print_both(computer, player)
        computer_choice = random.randint(0, 2)
        player_choice = chose()
        
        console.clear()
        print_both(computer, player)
        print_both(options[computer_choice], options[player_choice])
        
        if computer_choice == player_choice:
            print('Draw', end=2*'\n')
        elif (computer_choice - player_choice) % 3 == 1:
            print('Computer wins!', end=2*'\n')
            computer += 1
        else:
            print('You win!', end=2*'\n')
            player += 1
            
        if quit_game():
            console.clear()
            print_both(computer, player)
            print('Thanks for playing. Good bye.')
            game_is_on = False
        
    
