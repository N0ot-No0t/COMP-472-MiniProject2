# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time
import numpy as np
import re

class Game:
    MINIMAX = 0
    ALPHABETA = 1
    HUMAN = 2
    AI = 3
    DEV = False
    
    def __init__(self, recommend = True):
        self.trace_file_content = []
        self.scoreboard_file_content = []
        self.heuristic_evaluations = 0
        self.initialize_game()
        self.recommend = recommend

    def initialize_game(self):
        if self.DEV:
            self.dimension = 5
            self.initialize_board()
            self.nb_blocs = 4
            self.win_size = 4
            self.current_state[2][2] = '#'
            self.current_state[1][0] = '#'
            self.current_state[0][4] = '#'
            self.current_state[4][3] = '#'
            self.max_time = 2
            self.algo = self.MINIMAX
            self.player_x = self.AI
            self.player_o = self.AI
            self.depth_x = 4
            self.depth_o = 4
        else:
            self.dimension = self.get_dimension_input("Enter your value for \"n\", where \"n\" will be the dimension (n x n) of the board: ")
            self.current_state = [['.' for col in range(self.dimension)] for row in range(self.dimension)]
            self.current_state = np.asarray(self.current_state)
            self.nb_blocs = self.get_num_blocs_input("Enter your value for \"b\", where \"b\" is the number of blocs present on the board: ")
            self.win_size = self.get_win_size_input("Enter your value for \"s\", where \"s\" is the number of required pieces to win: ")
            self.set_blocks() #add block to game board
            self.max_time = self.get_integer_input("Enter the max allowed time \"t\" (in seconds) for program to return a move: ")
            self.algo = self.get_algo_input("Enter false to do minimax or true to do alphabeta: ")
            self.player_x = self.get_player_input("Enter the word 'human' if you want player X to be a human. Enter 'AI' if you want player X to be under AI control: ")
            self.player_o = self.get_player_input("Enter the word 'human' if you want player O to be a human. Enter 'AI' if you want player O to be under AI control: ")
            self.depth_x = self.get_integer_input("Enter the max depth for player X: ")
            self.depth_o = self.get_integer_input("Enter the max depth for player O: ")
        # Player X always plays first
        self.player_turn = 'X'

        self.evaluations_by_depth = {i: 0 for i in range(max(self.depth_x, self.depth_o) + 1)}  # +1 because depth includes last value (depth 2 = 0, 1, 2)
        self.depths_evaluated = []
        self.all_evaluation_times = []
        self.all_num_heuristic_evaluations = []
        self.all_evaluations_by_depth = {i: 0 for i in range(max(self.depth_x, self.depth_o) + 1)}
        self.total_moves = 0

        self.trace_file_content.append(f"n={self.dimension} b={self.nb_blocs} s={self.win_size} t={self.max_time}")
        self.trace_file_content.append(f"Player X: {self.player_x} d={self.depth_x} a={self.algo} e2()")
        self.trace_file_content.append(f"Player O: {self.player_o} d={self.depth_o} a={self.algo} e2()")

        self.total_wins_e1 = 0
        self.total_wins_e2 = 0
        self.total_draws = 0
        self.draw = False
        self.scoreboard_total_moves = []

        # Set the blocs to random places on the board
        # np.put(self.current_state,np.random.choice(range(int(self.n)*int(self.n)), int(self.b), replace='#'),"#")

    def initialize_board(self):
        self.current_state = [['.' for col in range(self.dimension)] for row in range(self.dimension)]
        self.current_state = np.asarray(self.current_state)
        self.total_moves = 0

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
                if win_size >= 3 and win_size <= self.dimension:
                    return win_size
                print(f"Invalid input. The winning line-up size must be between 3 and {self.dimension}. Please try again!")
            except ValueError:
                print('Invalid input. Please try again!')
                break

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

    def get_heuristic_input(self, prompt):
        while True:
            try:
                heuristic = str(input(prompt))
                if heuristic.casefold() == "e1":
                    return 'e1'
                elif heuristic.casefold() == "e2":
                    return 'e2'
                print('Invalid input. Please try again!')
            except ValueError:
                print('Invalid input. Please try again!')

    def set_blocks(self):
        blocs = self.nb_blocs
        while (blocs > 0):
            print("Please input the coordinates of the bloc: ")
            x_coordinate = int(transform_input_to_int(input('enter the x (row) position (A,B,C,D...): ')))
            y_coordinate = int(input('enter the y (column) coordinate (0,1,2,3...): '))
            if self.is_valid(x_coordinate, y_coordinate):
                self.current_state[x_coordinate][y_coordinate] = '#'
                blocs-=1
            else:
                print('Invalid coordinate. Please Try again!')

    def draw_board(self):
        print()

        header_row = "~ "
        for i in range(int(self.dimension)):
            header_row += transform_input_to_char(i)+"  "

        print(f"{header_row}\t(move #{self.total_moves})")
        self.trace_file_content.append(f"\n{header_row}\t(move #{self.total_moves})")
        for y in range(0, int(self.dimension)):
            row_to_print = str(y)+" "
            for x in range(0, int(self.dimension)):
                row_to_print+=str(self.current_state[x][y])+'  '
            print(row_to_print)
            self.trace_file_content.append(row_to_print)
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
        for i in range(self.dimension):
            sequence = "".join(column(i, self.current_state)).strip()
            #X wins
            if re.search("X{"+str(self.win_size)+",}",sequence):
                return 'X'
            #O wins
            elif re.search("O{"+str(self.win_size)+",}",sequence):
                return 'O'

        # Horizontal win
        for i in range(self.dimension):
            sequence = "".join(row(i, self.current_state)).strip()
            #X wins
            if re.search("X{"+str(self.win_size)+",}",sequence):
                return 'X'
            #O wins
            elif re.search("O{"+str(self.win_size)+",}",sequence):
                return 'O'

        # Any diagonal win
        diag_l, diags = diagonals(self.current_state)
        for i in range(diag_l):
            sequence = "".join(diags[i]).strip()
            #X wins
            if re.search("X{"+str(self.win_size)+",}",sequence):
                return 'X'
            #O wins
            elif re.search("O{"+str(self.win_size)+",}",sequence):
                return 'O'      

        # Is whole board full?
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
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
                self.trace_file_content.append('\nThe winner is X!\n')
            elif self.result == 'O':
                print('The winner is O!')
                self.trace_file_content.append('\nThe winner is O!\n')
            elif self.result == '.':
                print("It's a tie!")
                self.draw = True
                self.trace_file_content.append("\nIt's a tie!\n")
            # self.initialize_game()
        return self.result

    def count_num_empty_cells(self):
        num_empty_cells = 0
        for col in range(self.dimension):
            sequence = "".join(column(col, self.current_state)).strip()
            num_empty_cells+=sequence.count('.')
        return num_empty_cells

    def input_move(self):
        while True:
            print(F'Player {self.player_turn}, enter your move:')
            px = int(transform_input_to_int(input('enter the x coordinate (A,B,C,D,...): ')) )
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
        self.heuristic_evaluations = 0
        self.depths_evaluated = []
        for i in range(len(self.evaluations_by_depth)):
            self.evaluations_by_depth[i] = 0       #reset evaluations at each depth to 0
        return self.player_turn

    def minimax(self, remaining_time, heuristic = 'e2',max=False, current_depth=0):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        begin = time.time()
        max_depth = self.depth_x
        value = float('inf')
        if max:
            value = float('-inf')
            max_depth = self.depth_o

        #check if num_empty cells (num of moves left) is less than the max depth
        if self.count_num_empty_cells() < (max_depth-current_depth):
            max_depth = self.count_num_empty_cells()
       
        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            self.heuristic_evaluations += 1
            self.evaluations_by_depth[current_depth] += 1
            self.depths_evaluated.append(current_depth)
            self.all_evaluations_by_depth[current_depth] += 1
            return (float('-inf'), x, y)
        elif result == 'O':
            self.heuristic_evaluations += 1
            self.evaluations_by_depth[current_depth] += 1
            self.depths_evaluated.append(current_depth)
            self.all_evaluations_by_depth[current_depth] += 1
            return (float('inf'), x, y)
        elif result == '.':
            self.heuristic_evaluations += 1
            self.evaluations_by_depth[current_depth] += 1
            self.depths_evaluated.append(current_depth)
            self.all_evaluations_by_depth[current_depth] += 1
            return (0, x, y)
        if remaining_time < 0.2:
            #print("Took too long with current heuristic. Switching to e1")
            self.evaluations_by_depth[current_depth] += 1
            self.depths_evaluated.append(current_depth)
            self.all_evaluations_by_depth[current_depth] += 1
            return (self.e1(), x, y)
        if current_depth == max_depth:
            self.evaluations_by_depth[current_depth] += 1
            self.depths_evaluated.append(current_depth)
            self.all_evaluations_by_depth[current_depth] += 1
            if heuristic == 'e2':
                return (self.e2(), x, y)
            if heuristic == 'e1':
                return (self.e1(), x, y)

        for i in range(0, int(self.dimension)):
            for j in range(0, int(self.dimension)):
                if self.current_state[i][j].strip() == '.':
                    if max:
                        end = time.time()
                        elapsed = end - begin
                        self.current_state[i][j] = 'O  '
                        (v, _, _) = self.minimax(max=False, current_depth=current_depth+1, remaining_time=(remaining_time - elapsed), heuristic=heuristic)
                        if v >= value:
                            value = v
                            x = i
                            y = j
                    else:
                        end = time.time()
                        elapsed = end - begin
                        self.current_state[i][j] = 'X  '
                        (v, _, _) = self.minimax(max=True, current_depth=current_depth+1, remaining_time=(remaining_time - elapsed), heuristic=heuristic)
                        if v <= value:
                            value = v
                            x = i
                            y = j
                    self.current_state[i][j] = '.  '
        return (value, x, y)

    def alphabeta(self, remaining_time, heuristic = 'e2',alpha=float('inf'), beta=float('-inf'), max=False, current_depth=0):
        # Minimizing for 'X' and maximizing for 'O'
        # Possible values are:
        # -1 - win for 'X'
        # 0  - a tie
        # 1  - loss for 'X'
        # We're initially setting it to 2 or -2 as worse than the worst case:
        begin = time.time()
        max_depth = self.depth_x
        value = float('inf')
        if max:
            value = float('-inf')
            max_depth = self.depth_o
        
        #check if num_empty cells (num of moves left) is less than the max depth
        if self.count_num_empty_cells() < (max_depth-current_depth):
            max_depth = self.count_num_empty_cells()

        x = None
        y = None
        result = self.is_end()
        if result == 'X':
            self.heuristic_evaluations += 1
            self.evaluations_by_depth[current_depth] += 1
            self.depths_evaluated.append(current_depth)
            self.all_evaluations_by_depth[current_depth] += 1
            return (float('-inf'), x, y)
        elif result == 'O':
            self.heuristic_evaluations += 1
            self.evaluations_by_depth[current_depth] += 1
            self.depths_evaluated.append(current_depth)
            self.all_evaluations_by_depth[current_depth] += 1
            return (float('inf'), x, y)
        elif result == '.':
            self.heuristic_evaluations += 1
            self.evaluations_by_depth[current_depth] += 1
            self.depths_evaluated.append(current_depth)
            self.all_evaluations_by_depth[current_depth] += 1
            return (0, x, y)
        if remaining_time < 0.2:
            #print("Took too long with current heuristic. Switching to e1")
            self.evaluations_by_depth[current_depth] += 1
            self.depths_evaluated.append(current_depth)
            self.all_evaluations_by_depth[current_depth] += 1
            return (self.e1(), x, y)
        if current_depth == max_depth:
            self.evaluations_by_depth[current_depth] += 1
            self.depths_evaluated.append(current_depth)
            self.all_evaluations_by_depth[current_depth] += 1
            if heuristic == 'e2':
                return (self.e2(), x, y)
            if heuristic == 'e1':
                return (self.e1(), x, y)


        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                if self.current_state[i][j] == '.':
                    if max:
                        end = time.time()
                        elapsed = end - begin
                        current_remaining_time = remaining_time - elapsed
                        self.current_state[i][j] = 'O'
                        (v, _, _) = self.alphabeta(alpha, beta, max=False, current_depth=current_depth+1, remaining_time=current_remaining_time, heuristic=heuristic)
                        if v > value:
                            value = v
                            x = i
                            y = j
                    else:
                        end = time.time()
                        elapsed = end - begin
                        current_remaining_time = remaining_time - elapsed
                        self.current_state[i][j] = 'X'
                        (v, _, _) = self.alphabeta(alpha, beta, max=True, current_depth=current_depth+1, remaining_time=current_remaining_time, heuristic=heuristic)
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

    def play(self, heuristic_x = 'e2', heuristic_o='e2'):
        while True:
            self.draw_board()
            if self.check_end():
                self.trace_file_content.append(F"6(b)i   Average evaluation time: {sum(self.all_evaluation_times)/len(self.all_evaluation_times)}")
                self.trace_file_content.append(F"6(b)ii  Total heuristic evaluations: {sum(self.all_num_heuristic_evaluations)}")
                self.trace_file_content.append(F"6(b)iii Evaluations by depth: {self.all_evaluations_by_depth}")
                avg_evaluation_depth = 0
                for i in range(len(self.all_evaluations_by_depth)):
                    avg_evaluation_depth += (i*self.all_evaluations_by_depth[i])

                avg_evaluation_depth /= float(sum(self.all_evaluations_by_depth.values()))
                self.trace_file_content.append(F"6(b)iv  Average evaluation depth: {avg_evaluation_depth}")
                self.trace_file_content.append(F"6(b)v   Average recursion depth: ")
                self.trace_file_content.append(F"6(b)vi  Total moves: {self.total_moves}")
                self.scoreboard_total_moves.append(self.total_moves)
                self.save_trace_file(self.trace_file_content)
                if self.player_turn == "X":
                    if heuristic_o == "e1":
                        self.total_wins_e1 += 1
                    else:
                        self.total_wins_e2 += 1
                else:
                    if heuristic_x == "e1":
                        self.total_wins_e1 += 1
                    else:
                        self.total_wins_e2 += 1
                if self.draw:
                        self.total_draws += 1
                        self.draw = False
                return
            self.total_moves += 1
            start = time.time()
            if self.algo == self.MINIMAX:
                if self.player_turn == 'X':
                    (_, x, y) = self.minimax(max=False, remaining_time=self.max_time, heuristic=heuristic_x)
                else:
                    (_, x, y) = self.minimax(max=True, remaining_time=self.max_time, heuristic=heuristic_o)
            else: # algo == self.ALPHABETA
                if self.player_turn == 'X':
                    (m, x, y) = self.alphabeta(max=False, remaining_time=self.max_time, heuristic=heuristic_x)
                else:
                    (m, x, y) = self.alphabeta(max=True, remaining_time=self.max_time, heuristic=heuristic_o)
            end = time.time()
            if (self.player_turn == 'X' and self.player_x == self.HUMAN) or (self.player_turn == 'O' and self.player_o == self.HUMAN):
                    if self.recommend:
                        print(F'Evaluation time: {round(end - start, 7)}s')
                        print(F'Recommended move: x = {transform_input_to_char(x)}, y = {y}')
                        self.trace_file_content.append(F'\nPlayer {self.player_turn} under AI control plays: i = {transform_input_to_char(x)}, j = {y}')
                        self.trace_file_content.append(F'   i.  Evaluation time: {round(end - start, 7)}s')
                        self.all_evaluation_times.append(round(end - start, 7))
                    (x,y) = self.input_move()
            if (self.player_turn == 'X' and self.player_x == self.AI) or (self.player_turn == 'O' and self.player_o == self.AI):
                        print(F'Evaluation time: {round(end - start, 7)}s')
                        print(F'Player {self.player_turn} under AI control plays: i = {transform_input_to_char(x)}, j = {y}')
                        self.trace_file_content.append(F'\nPlayer {self.player_turn} under AI control plays: i = {transform_input_to_char(x)}, j = {y}')
                        self.trace_file_content.append(F'   i.  Evaluation time: {round(end - start, 7)}s')
                        self.all_evaluation_times.append(round(end - start, 7))
            
            self.trace_file_content.append(F"   ii.  Heuristic evaluations: {self.heuristic_evaluations}")
            self.all_num_heuristic_evaluations.append(self.heuristic_evaluations)
            self.trace_file_content.append(F"   iii. Evaluations by depth: {self.evaluations_by_depth}")
            self.trace_file_content.append(F"   iv.  Average evaluation depth: {sum(self.depths_evaluated)/float(len(self.depths_evaluated))}")
            self.trace_file_content.append(F"   v.   Average recursion depth: ")

            self.current_state[x][y] = self.player_turn
            self.switch_player()

    #More complicated heuristic. Possible max O(n^2 + 2n^2 + n) so O(n^2).
    def e2(self):
        score = 0
        #for each row and column
        for i in range(self.dimension):
            col_sequence = "".join(column(i, self.current_state)).strip()
            row_sequence = "".join(row(i, self.current_state)).strip()
            for j in range(int(self.win_size)):
                if re.search("O{"+str(self.win_size-j)+",}",col_sequence):
                    score+=(self.win_size-j)*10**(self.win_size-j)
                elif re.search("X{"+str(self.win_size-j)+",}",col_sequence):
                    score-=(self.win_size-j)*10**(self.win_size-j)
                if re.search("O{"+str(self.win_size-j)+",}",row_sequence):
                    score+=(self.win_size-j)*10**(self.win_size-j)
                elif re.search("X{"+str(self.win_size-j)+",}",row_sequence):
                    score-=(self.win_size-j)*10**(self.win_size-j)
        #for each diagonal
        diag_l, diags = diagonals(self.current_state)
        for i in range(diag_l):
            diag_sequence = "".join(diags[i]).strip()
            if len(diag_sequence) >= self.win_size:
                for j in range(self.win_size):
                    if re.search("O{"+str(self.win_size-j)+",}",diag_sequence):
                        score+=(self.win_size-j)*10**(self.win_size-j)
                    elif re.search("X{"+str(self.win_size-j)+",}",diag_sequence):
                        score-=(self.win_size-j)*10**(self.win_size-j)

        self.heuristic_evaluations += 1
        return score

    #Simple heuristic. Possible max O(200) ==> n = 10
    def e1(self):
        score = 0

        #upper horizontal half
        score += eval_o_vs_x(self.current_state[:int(self.dimension/2)+1,:])
        #lower horizontal half
        score += eval_o_vs_x(self.current_state[int(self.dimension/2):,:])

        #left vertical half
        score += eval_o_vs_x(self.current_state[:,:int(self.dimension/2 + 1)])
        #right vertical half
        score += eval_o_vs_x(self.current_state[:,int(self.dimension/2):])

        self.heuristic_evaluations += 1
        return score


    def save_trace_file(self, trace):
        filename = f"gameTrace-{self.dimension}{self.nb_blocs}{self.win_size}{self.max_time}.txt"
        with open(filename, "w") as file:
            file.write('\n'.join(trace))

def transform_input_to_int(char):
    letters = ['A','B','C','D','E','F','G','H','I','J',]
    for i in range(len(letters)):
        if char.upper() == letters[i]:
            return i

def transform_input_to_char(int_val):
    letters = ['A','B','C','D','E','F','G','H','I','J',]
    return letters[int_val]

def eval_o_vs_x(grid):
    x_count = 0
    o_count = 0
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if grid[i][j] == 'X':
                x_count+=1
            elif grid[i][j] == 'O':
                o_count+=1
    return (o_count - x_count)

#Return i_th col
def column(i, state):
    return [col[i] for col in state.T]

#Return i_th row
def row(i, state):
    return [row[i] for row in state]

#It just works, don't question it. Returns all the diagonals, corners don't count.
#https://stackoverflow.com/questions/6313308/get-all-the-diagonals-in-a-matrix-list-of-lists-in-python
def diagonals(state):
    diags = [state[::-1,:].diagonal(i) for i in range(-state.shape[0]+1,state.shape[1])]
    diags.extend(state.diagonal(i) for i in range(state.shape[1]-1,-state.shape[0],-1))

    return len(diags), diags 

def scoreboard(r = 10):
    g = Game(recommend=True)
    p_x_heuristic = g.get_heuristic_input("Enter \'e1\' or \'e2\' to set the heuristic for player X: ")
    p_o_heuristic = g.get_heuristic_input("Enter \'e1\' or \'e2\' to set the heuristic for player O: ")

    #start with X by default
    for round in range(r):
        print("Round #"+str(round))
        g.play(heuristic_x=p_x_heuristic, heuristic_o=p_o_heuristic)
        g.initialize_board()

    print("Time to switch players!")

    #start with O
    g.player_turn = 'O'
    for round in range(r):
        print("Round #"+str(round))
        g.play(heuristic_x=p_x_heuristic, heuristic_o=p_o_heuristic)
        g.initialize_board()

    g.scoreboard_file_content.append(f"n={g.dimension} b={g.nb_blocs} s={g.win_size} t={g.max_time}")

    g.scoreboard_file_content.append(f"Player X: d={g.depth_x} a={g.player_x}")
    g.scoreboard_file_content.append(f"Player Y: d={g.depth_o} a={g.player_o}")

    g.scoreboard_file_content.append(f"{2*r} games")
    g.scoreboard_file_content.append(f"Total wins for heuristic e1: {g.total_wins_e1}")
    g.scoreboard_file_content.append(f"Total wins for heuristic e2: {g.total_wins_e2}")
    g.scoreboard_file_content.append(f"Total draws: {g.total_draws}")

    g.scoreboard_file_content.append(F"i   Average evaluation time: {sum(g.all_evaluation_times)/len(g.all_evaluation_times)}s")
    g.scoreboard_file_content.append(F"ii   Total heuristic evaluations: {sum(g.all_num_heuristic_evaluations)}")
    g.scoreboard_file_content.append(F"iii   Evaluations by depth: {g.all_evaluations_by_depth}")
    avg_evaluation_depth = 0
    for i in range(len(g.all_evaluations_by_depth)):
        avg_evaluation_depth += (i*g.all_evaluations_by_depth[i])

    avg_evaluation_depth /= float(sum(g.all_evaluations_by_depth.values()))
    g.scoreboard_file_content.append(F"iv   Average evaluation depth: {avg_evaluation_depth}")
    g.scoreboard_file_content.append(F"v   Average recursion depth: ")
    g.scoreboard_file_content.append(F"vi   Average moves per game: {sum(g.scoreboard_total_moves)/len(g.scoreboard_total_moves)}")
    filename = "scoreboard.txt"
    with open(filename, "w") as file:
        file.write('\n'.join(g.scoreboard_file_content))

def main():
    g = Game(recommend=True)
    g.play()

    #scoreboard(5)

if __name__ == "__main__":
    main()

