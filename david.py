# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time

class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3
    
    def __init__(self, recommend = True):
        self.initialize_game()
        self.recommend = recommend
        
    def initialize_game(self):
        self.dimension = self.get_integer_input("Enter your value for \"n\", where \"n\" will be the dimension (n x n) of the board: ")
        self.current_state = [['.' for col in range(self.dimension)] for row in range(self.dimension)]
        self.nb_blocs = self.get_integer_input("Enter your value for \"b\", where \"b\" is the number of blocs present on the board: ")
        self.required_nb_of_pieces_to_win = self.get_integer_input("Enter your value for \"s\", where \"s\" is the number of required pieces to win: ")
        self.set_blocks() #add block to game board
        self.max_time = self.get_integer_input("Enter the max allowed time “t” (in seconds) for program to return a move: ")
        # algo = input("Enter false to do minimax or true to do alphabeta: ")
        self.player_x = self.get_player_input("Enter the word 'human' if you want player X to be a human. Enter 'AI' if you want player X to be under AI control: ")
        self.player_o = self.get_player_input("Enter the word 'human' if you want player O to be a human. Enter 'AI' if you want player O to be under AI control: ")
        depth_p1 = self.get_integer_input("Enter the max depth for player 1: ")
        depth_p2 = self.get_integer_input("Enter the max depth for player 2: ")
        # Player X always plays first
        self.player_turn = 'X'
        self.draw_board()
        self.is_end()

    def get_integer_input(self, prompt):
        while True:
            try:
                return int(input(prompt))
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
        for y in range(0, self.dimension):
            for x in range(0, self.dimension):
                print(F'{self.current_state[x][y]}', end="")
            print()
        print()
        
    def is_valid(self, px, py):
        if px < 0 or px > self.dimension-1 or py < 0 or py > self.dimension-1:
            return False
        elif self.current_state[px][py] != '.':
            return False
        else:
            return True

    def is_end(self):
        def check(values):
            x_counter = 0
            o_counter = 0
            for value in values:
                if value == "X":
                    x_counter += 1
                    o_counter = 0
                elif value == "O":
                    o_counter += 1
                    x_counter = 0
                else:
                    x_counter = 0
                    o_counter = 0
                if x_counter == self.required_nb_of_pieces_to_win:
                    return 'X'
                elif o_counter == self.required_nb_of_pieces_to_win:
                    return 'O'
            return None
        
        # Vertical win
        for col in range(self.dimension):
            result = check([self.current_state[row][col] for row in range(self.dimension)])
            if result:
                return result

        # Horizontal win
        for row in range(self.dimension):
            result = check([self.current_state[row][col] for col in range(self.dimension)])
            if result:
                return result

        # Main diagonal win
        result = check([self.current_state[index][index] for index in range(self.dimension)])
        if result:
            return result

        # Second diagonal win
        result = check([self.current_state[index][self.dimension-1-index] for index in range(self.dimension)])
        if result:
            return result

        # Is whole board full?
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                # There's an empty field, we continue the game
                if (self.current_state[i][j] == '.'):
                    return None

        # It's a tie!
        return '.'

    #Checks if the game has ended - Winner or draw has occured
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

    def minimax(self, max=False):
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
        for i in range(0, 3):
            for j in range(0, 3):
                if self.current_state[i][j] == '.':
                    if max:
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.minimax(max=False)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.minimax(max=True)
                        if v < value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.'
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
        for i in range(0, 3):
            for j in range(0, 3):
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

    def play(self,algo=None,player_x=None,player_o=None):
        if algo == None:
            algo = self.ALPHABETA
        if player_x == None:
            player_x = self.HUMAN
        if player_o == None:
            player_o = self.HUMAN
        while True:
            self.draw_board()
            if self.check_end():
                return
            start = time.time()
            if algo == self.MINIMAX:
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
            if (self.player_turn == 'X' and player_x == self.HUMAN) or (self.player_turn == 'O' and player_o == self.HUMAN):
                    if self.recommend:
                        print(F'Evaluation time: {round(end - start, 7)}s')
                        print(F'Recommended move: x = {x}, y = {y}')
                    (x,y) = self.input_move()
            if (self.player_turn == 'X' and player_x == self.AI) or (self.player_turn == 'O' and player_o == self.AI):
                        print(F'Evaluation time: {round(end - start, 7)}s')
                        print(F'Player {self.player_turn} under AI control plays: x = {x}, y = {y}')
            self.current_state[x][y] = self.player_turn
            self.switch_player()

def main():
    g = Game(recommend=True)
    # g.play(algo=Game.ALPHABETA,player_x=Game.AI,player_o=Game.AI)
    # g.play(algo=Game.MINIMAX,player_x=Game.AI,player_o=Game.HUMAN)

if __name__ == "__main__":
    main()

