# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time
import numpy as np
import re

class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3
    
    def __init__(self, recommend = True):
        self.initialize_game()
        self.recommend = recommend
        
    def initialize_game(self):
        self.dimension = self.get_dimension_input("Enter your value for \"n\", where \"n\" will be the dimension (n x n) of the board: ")
        self.current_state = [['.' for col in range(self.dimension)] for row in range(self.dimension)]
        self.current_state = np.asarray(self.current_state)
        self.nb_blocs = self.get_num_blocs_input("Enter your value for \"b\", where \"b\" is the number of blocs present on the board: ")
        self.win_size = self.get_win_size_input("Enter your value for \"s\", where \"s\" is the number of required pieces to win: ")
        self.set_blocks() #add block to game board
        self.max_time = self.get_integer_input("Enter the max allowed time “t” (in seconds) for program to return a move: ")
        self.algo = self.get_algo_input("Enter false to do minimax or true to do alphabeta: ")
        self.player_x = self.get_player_input("Enter the word 'human' if you want player X to be a human. Enter 'AI' if you want player X to be under AI control: ")
        self.player_o = self.get_player_input("Enter the word 'human' if you want player O to be a human. Enter 'AI' if you want player O to be under AI control: ")
        self.depth_x = self.get_integer_input("Enter the max depth for player X: ")
        self.depth_o = self.get_integer_input("Enter the max depth for player O: ")
        # Player X always plays first
        self.player_turn = 'X'

        # Set the blocs to random places on the board
        # np.put(self.current_state,np.random.choice(range(int(self.n)*int(self.n)), int(self.b), replace='#'),"#")

    def get_dimension_input(self, prompt):
        while True:
            try:
                size = int(input(prompt))
                if size >= 3 and size <=10:
                    return size
                print("Invalid input. The dimension of the board must be between 3 and 10. Please try again!")
            except ValueError:
                print('Invalid input. Please try again!')

    def get_num_blocs_input(self, prompt):
        while True:
            try:
                num_blocs = int(input(prompt))
                if num_blocs >= 0 and num_blocs <=2*self.dimension:
                    return num_blocs
                print(f"Invalid input. The number of blocs must be between 0 and {2*self.dimension}. Please try again!")
            except ValueError:
                print('Invalid input. Please try again!')

    def get_win_size_input(self, prompt):
        while True:
            try:
                win_size = int(input(prompt))
                if win_size >= 3 and win_size <=self.dimension:
                    return win_size
                print(f"Invalid input. The winning line-up size must be between 3 and {self.dimension}. Please try again!")
            except ValueError:
                print('Invalid input. Please try again!')

    def get_integer_input(self, prompt):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print('Invalid input. Please try again!')

    def get_algo_input(self, prompt):
        while True:
            try:
                value = str(input(prompt))
                if value.casefold() == "true":
                    return self.ALPHABETA
                elif value.casefold() == "false":
                    return self.MINIMAX
                print('Invalid input. Please try again!')
            except ValueError:
                print('Invalid input. Please try again!')

    def get_player_input(self, prompt):
        while True:
            try:
                player = str(input(prompt))
                if player.casefold() == "human":
                    return self.HUMAN
                elif player.casefold() == "ai":
                    return self.AI
                print('Invalid input. Please try again!')
            except ValueError:
                print('Invalid input. Please try again!')

    def set_blocks(self):
        blocs = self.nb_blocs
        while (blocs > 0):
            print("Please input the coordinates of the bloc: ")
            x_coordinate = int(input('enter the x (row) coordinate: '))
            y_coordinate = int(input('enter the y (column) coordinate: '))
            if self.is_valid(x_coordinate, y_coordinate):
                self.current_state[x_coordinate][y_coordinate] = '*'
                blocs-=1
            else:
                print('Invalid coordinate. Please Try again!')

    def draw_board(self):
        print()

        header_row = "~ "
        for i in range(int(self.dimension)):
            header_row += transform_input_to_char(i)+"  "

        print(header_row)
        for y in range(0, int(self.dimension)):
            row_to_print = str(y)+" "
            for x in range(0, int(self.dimension)):
                row_to_print+=str(self.current_state[x][y])+'  '
            print(row_to_print)
        print()
        
    def is_valid(self, px, py):
        if px < 0 or px > self.dimension-1 or py < 0 or py > self.dimension-1:
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    def is_end(self):

        # Vertical win
        for i in range(int(self.dimension)):
            sequence = "".join(column(i, self.current_state)).strip()
            #X wins
            if re.search("X{"+str(self.win_size)+",}",sequence):
                return 'X'
            #O wins
            elif re.search("O{"+str(self.win_size)+",}",sequence):
                return 'O'

        # Horizontal win
        for i in range(int(self.dimension)):
            sequence = "".join(row(i, self.current_state)).strip()
            #X wins
            if re.search("X{"+str(self.win_size)+",}",sequence):
                return 'X'
            #O wins
            elif re.search("O{"+str(self.win_size)+",}",sequence):
                return 'O'

        # Main diagonal win
        sequence = "".join(diagonal1(self.current_state)).strip()
        #X wins
        if re.search("X{"+str(self.win_size)+",}",sequence):
            return 'X'
        #O wins
        elif re.search("O{"+str(self.win_size)+",}",sequence):
            return 'O'      

        # Second diagonal win
        sequence = "".join(diagonal2(self.current_state)).strip()
        #X wins
        if re.search("X{"+str(self.win_size)+",}",sequence):
            return 'X'
        #O wins
        elif re.search("O{"+str(self.win_size)+",}",sequence):
            return 'O'  

        # Is whole board full?
        for i in range(0, int(self.dimension)):
            for j in range(0, int(self.dimension)):
                # There's an empty field, we continue the game
                if (self.current_state[i][j] == '.'):
                    return None

        # It's a tie!
        return '.'

    def check_end(self):
        self.result = self.is_end()
        # Printing the appropriate message if the game has ended
        if self.result != None:
            if self.result == 'X':
                print('The winner is X!')
            elif self.result == 'O':
                print('The winner is O!')
            elif self.result == '.':
                print("It's a tie!")
            self.initialize_game()
        return self.result

    def count_num_empty_cells(self):
        num_empty_cells = 0;
        for col in range(self.dimension):
            sequence = "".join(column(col, self.current_state)).strip()
            num_empty_cells+=sequence.count('.')
        return num_empty_cells

    def input_move(self):
        while True:
            print(F'Player {self.player_turn}, enter your move:')
            px = int(input('enter the x coordinate: '))
            py = int(input('enter the y coordinate: '))
            if self.is_valid(px, py):
                return (px,py)
            else:
                print('The move is not valid! Try again.')

    def switch_player(self):
        if self.player_turn == 'X':
            self.player_turn = 'O'
        elif self.player_turn == 'O':
            self.player_turn = 'X'
        return self.player_turn

    def minimax(self, max=False, current_depth = 0):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        max_depth = self.depth_x;
        value = 10**5
        if max:
            value = -10**5
            max_depth = self.depth_o;

        #check if num_empty cells is less than the max depth
        if self.count_num_empty_cells() < max_depth:
            max_depth = self.count_num_empty_cells()
       
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return (-1, x, y)
        elif result == 'O':
            return (1, x, y)
        elif result == '.':
            return (0, x, y)
        if current_depth == max_depth:
            return (self.e2(), x, y)

        for i in range(0, int(self.dimension)):
            for j in range(0, int(self.dimension)):
                if self.current_state[i][j].strip() == '.':
                    if max:
                        self.current_state[i][j] = 'O  '
                        (v, _, _) = self.minimax(max=False, current_depth=current_depth+1)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X  '
                        (v, _, _) = self.minimax(max=True, current_depth=current_depth+1)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.  '
        return (value, x, y)

    def alphabeta(self, alpha=-2, beta=2, max=False):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        value = 2
        if max:
            value = -2
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            return (-1, x, y)
        elif result == 'O':
            return (1, x, y)
        elif result == '.':
            return (0, x, y)
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(alpha, beta, max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(alpha, beta, max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
                    if max: 
                        if value >= beta:
                            return (value, x, y)
                        if value > alpha:
                            alpha = value
                    else:
                        if value <= alpha:
                            return (value, x, y)
                        if value < beta:
                            beta = value
        return (value, x, y)

    def play(self):
        while True:
            self.draw_board()
            if self.check_end():
                return
            start = time.time()
            if self.algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (_, x, y) = self.minimax(max=False)
                else:
                    (_, x, y) = self.minimax(max=True)
            else: # algo == self.ALPHABETA
                if self.player_turn == 'X':
                    (m, x, y) = self.alphabeta(max=False)
                else:
                    (m, x, y) = self.alphabeta(max=True)
            end = time.time()
            if (self.player_turn == 'X' and self.player_x == self.HUMAN) or (self.player_turn == 'O' and self.player_o == self.HUMAN):
                    if self.recommend:
                        print(F'Evaluation time: {round(end - start, 7)}s')
                        print(F'Recommended move: x = {x}, y = {y}')
                    (x,y) = self.input_move()
            if (self.player_turn == 'X' and self.player_x == self.AI) or (self.player_turn == 'O' and self.player_o == self.AI):
                        print(F'Evaluation time: {round(end - start, 7)}s')
                        print(F'Player {self.player_turn} under AI control plays: i = {x}, j = {y}')
            self.current_state[x][y] = self.player_turn
            self.switch_player()

    def e2(self):
        sequence = ''
        score = 0
        #for each row and column
        for i in range(int(self.dimension)):
            col_sequence = "".join(column(i, self.current_state)).strip()
            row_sequence = "".join(row(i, self.current_state)).strip()
            for j in range(int(self.win_size)):
                if re.search("O{"+str(int(self.win_size)-j)+",}",col_sequence):
                    score+=(int(self.win_size)-j)*10**(int(self.win_size)-j)
                elif re.search("X{"+str(int(self.win_size)-j)+",}",col_sequence):
                    score-=(int(self.win_size)-j)*10**(int(self.win_size)-j)
                if re.search("O{"+str(int(self.win_size)-j)+",}",row_sequence):
                    score+=(int(self.win_size)-j)*10**(int(self.win_size)-j)
                elif re.search("X{"+str(int(self.win_size)-j)+",}",row_sequence):
                    score-=(int(self.win_size)-j)*10**(int(self.win_size)-j)
        return score
            

def transform_input_to_int(char):
    letters = ['A','B','C','D','E','F','G','H','I','J',]
    for i in range(len(letters)):
        if char.upper() == letters[i]:
            return i

def transform_input_to_char(int_val):
    letters = ['A','B','C','D','E','F','G','H','I','J',]
    return letters[int_val]

def column(i, state):
    return [col[i] for col in state.T]

def row(i, state):
    return [row[i] for row in state]

def diagonal1(state):
    return state.diagonal()

def diagonal2(state):
    return np.fliplr(state).diagonal()

def main():
    g = Game(recommend=True)
    #g.play(algo=Game.ALPHABETA,player_x=Game.AI,player_o=Game.AI)
    g.play()

if __name__ == "__main__":
    main()

