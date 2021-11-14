# based on code from https://stackabuse.com/minimax-and-alpha-beta-pruning-in-python

import time
import numpy as np
import re

class Game:
	MINIMAX = 0
	ALPHABETA = 1
	HUMAN = 2
	AI = 3
	
	def __init__(self, b, n, s, recommend = True):
		self.b = b
		self.n = n
		self.s = s
		self.initialize_game()
		self.recommend = recommend
		
	def initialize_game(self):

		# Set the board with empty spaces (dots)
		self.current_state = np.zeros((int(self.n),int(self.n)), dtype='U1')
		self.current_state[:] = '.'

		# Set the blocs to random places on the board
		np.put(self.current_state,np.random.choice(range(int(self.n)*int(self.n)), int(self.b), replace='#'),"#")

		# Player X always plays first
		self.player_turn = 'X'

	def draw_board(self):
		print()

		header_row = "~ "
		for i in range(int(self.n)):
			header_row += transform_input_to_char(i)+"  "

		print(header_row)
		for y in range(0, int(self.n)):
			row_to_print = str(y)+" "
			for x in range(0, int(self.n)):
				row_to_print+=str(self.current_state[x][y])+'  '
			print(row_to_print)
		print()
		
	def is_valid(self, px, py):
		if px < 0 or px > 2 or py < 0 or py > 2:
			return False
		elif self.current_state[px][py] != '.':
			return False
		else:
			return True

	def is_end(self):

		# Vertical win
		for i in range(int(self.n)):
			sequence = "".join(column(i, self.current_state)).strip()
			#X wins
			if re.search("X{"+str(self.s)+",}",sequence):
				return 'X'
			#O wins
			elif re.search("O{"+str(self.s)+",}",sequence):
				return 'O'

		# Horizontal win
		for i in range(int(self.n)):
			sequence = "".join(row(i, self.current_state)).strip()
			#X wins
			if re.search("X{"+str(self.s)+",}",sequence):
				return 'X'
			#O wins
			elif re.search("O{"+str(self.s)+",}",sequence):
				return 'O'

		# Main diagonal win
		sequence = "".join(diagonal1(self.current_state)).strip()
		#X wins
		if re.search("X{"+str(self.s)+",}",sequence):
			return 'X'
		#O wins
		elif re.search("O{"+str(self.s)+",}",sequence):
			return 'O'		

		# Second diagonal win
		sequence = "".join(diagonal2(self.current_state)).strip()
		#X wins
		if re.search("X{"+str(self.s)+",}",sequence):
			return 'X'
		#O wins
		elif re.search("O{"+str(self.s)+",}",sequence):
			return 'O'	

		# Is whole board full?
		for i in range(0, int(self.n)):
			for j in range(0, int(self.n)):
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
		for i in range(0, self.n):
			for j in range(0, self.n):
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
		for i in range(0, self.n):
			for j in range(0, self.n):
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
						print(F'Player {self.player_turn} under AI control plays: i = {x}, j = {y}')
			self.current_state[x][y] = self.player_turn
			self.switch_player()

	def e2(self, state):
		sequence = ''
		score = 0
		#for each row
		for i in range(int(self.n)):
			sequence = "".join(column(i, state)).strip()
			if re.search("X{"+str(self.s)+",}",sequence):
				score+=1000
			elif re.search("O{"+str(self.s)+",}",sequence):
				score-=1000

		return score
			

def transform_input_to_int(char):
	letters = ['A','B','D','E','F','G','H','I','J',]
	for i in range(len(letters)):
		if char.upper() == letters[i]:
			return i

def transform_input_to_char(int_val):
	letters = ['A','B','D','E','F','G','H','I','J',]
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

	dimension = 5
	nb_blocs = 4
	required_nb_of_pieces_to_win = 4

	#dimension = input("Enter your value for \"n\", where \"n\" will be the dimension of (n x n) of the board: ")
	#nb_blocs = input("Enter your value for \"b\", where \"b\" is the number of blocs present on the board: ")
	#required_nb_of_pieces_to_win = input("Enter your value for \"s\", where \"s\" is the number of required pieces to win: ")

	g = Game(nb_blocs, dimension, required_nb_of_pieces_to_win, recommend=True)
	#g.play(algo=Game.ALPHABETA,player_x=Game.AI,player_o=Game.AI)
	#g.play(algo=Game.MINIMAX,player_x=Game.AI,player_o=Game.HUMAN)
	g.draw_board()

	g.current_state[0][0] = 'O'
	g.current_state[1][1] = 'O'
	g.current_state[2][2] = 'O'
	g.current_state[3][3] = 'O'

	g.draw_board()
	print(column(1,g.current_state))
	print(g.is_end())

if __name__ == "__main__":
	main()

