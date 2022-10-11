from asyncore import write
from pickle import TRUE
import tkinter as tk
from tkinter import Frame, messagebox
from tkinter import filedialog

from setuptools import Command

# You may import any submodules of tkinter here if you wish
# You may also import anything from the typing module
# All other additional imports will result in a deduction of up to 100% of your A3 mark

from a3_support import *

# Write your classes here
"""
[[1,2,3,None], [1,3,2,None], [1,2,3,None], [1,3,2,None]]
m = Model()
m.current_tiles = [[2,2,4,4], [4,2,2,2], [8,2,8,4], [4,16,2,32]]
m.get_tiles()
m.move_
"""


class Model():
	def __init__(self) -> None:
		self.current_tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
		self.points = 0
		self.previous_points  = 0
		self._undo = MAX_UNDOS
		self.previous_tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]

	def new_game(self) -> None:
		for i in range(NUM_ROWS):
			for j in range(NUM_COLS):
				if self.current_tiles[i][j] != None:
					self.current_tiles[i][j] = None
		for _ in range(2):
			self.add_tile()

	def get_tiles(self):
		return self.current_tiles

	def add_tile(self) -> None:
		random_tile = generate_tile(self.current_tiles)
		value = random_tile[1]
		position = random_tile[0]
		self.current_tiles[position[0]][position[1]] = value

	def move_left(self) -> None:
		self.current_tiles = stack_left(self.current_tiles)
		tiles_points = combine_left(self.current_tiles)
		self.current_tiles = tiles_points[0]    			# Simplification
		self.points += tiles_points[1]
		self.current_tiles = stack_left(self.current_tiles)
			

	def move_right(self) -> None:
		self.current_tiles = reverse(self.current_tiles)
		self.move_left()									# Simplification
		self.current_tiles = reverse(self.current_tiles)    # sth wrong here

	def move_up(self) -> None:
		self.current_tiles = transpose(self.current_tiles)
		self.move_left()
		self.current_tiles = transpose(self.current_tiles)

	def move_down(self) -> None:
		self.current_tiles = transpose(self.current_tiles)
		self.move_right()
		self.current_tiles = transpose(self.current_tiles)

	def attempt_combine(self, move: str) -> bool:
		if move in ["a" ,"d"]:
			for i in range(NUM_ROWS):
					for j in range(NUM_COLS-1):
						if self.current_tiles[i][j] == self.current_tiles[i][j+1] \
							and self.current_tiles[i][j] != None:
							return True
		if move in ["w" ,"s"]:
			for i in range(NUM_ROWS-1):
					for j in range(NUM_COLS):
						if self.current_tiles[i][j] == self.current_tiles[i+1][j] \
							and self.current_tiles[i][j] != None:
							return True
		return False

	def attempt_move(self, move: str) -> bool:
		if self.attempt_combine(move):
			return True
		elif move in ["a" ,"d"]:
			for i in range(NUM_ROWS):
				for j in range(NUM_COLS-1):
					if move == "d":
						if f"{self.current_tiles[i][j]}".isdigit() and \
							self.current_tiles[i][j+1] == None:
							return True
					if move == "a":
						if f"{self.current_tiles[i][j+1]}".isdigit() and \
							self.current_tiles[i][j] == None:
							return True
		elif move in ["w", "s"]:
			for i in range(NUM_ROWS-1):
				for j in range(NUM_COLS):
					if move == "s":
						if f"{self.current_tiles[i][j]}".isdigit() and \
							self.current_tiles[i+1][j] == None:
							return True
					if move == "w":
						if f"{self.current_tiles[i+1][j]}".isdigit() and \
							self.current_tiles[i][j] == None:
							return True
			
		return False		

		# temp = self.get_tiles()
		# if move == 'w':
		# 	self.move_up()
		# elif move == 'a':
		# 	self.move_left()
		# elif move == 's':
		# 	self.move_down()
		# elif move == 'd':
		# 	self.move_right()
		# if temp == self.get_tiles():
		# 	return False
		# else:
		# 	return True

	def has_won(self) -> bool:
		for i in range(NUM_ROWS):
			for j in range(NUM_COLS):
				if self.get_tiles()[i][j] == 2048:
					return True
		return False
		

	def has_lost(self) -> bool:
		values = []
		for i in range(NUM_ROWS):
			for j in range(NUM_COLS):
				values.append(self.get_tiles()[i][j])
		if len(values) == 16 and not self.attempt_move("w") and not self.attempt_move("a")\
			and not self.attempt_move("s") and not self.attempt_move("d") and not self.has_won():
			return True
		else:
			return False

	def get_score(self) -> int:
		return self.points

	def get_undos_remaining(self) -> int:
		return self._undo

	def use_undo(self) -> None:
		if self._undo >= 1:
			self.current_tiles = self.previous_tiles
			self.points = self.previous_points
			self._undo = self._undo - 1


class GameGrid(tk.Canvas):
	def __init__(self, master: tk.Tk, **kwargs) -> None:
		super().__init__(master, width=BOARD_WIDTH, height=BOARD_HEIGHT,\
			bg=BACKGROUND_COLOUR,**kwargs)

		# self.frame=tk.Frame(
		# 	self.master,
		# 	bg=BACKGROUND_COLOUR
		# )

		self.box_side = 87
		self.padding = BUFFER
		self.pack(
			expand=tk.TRUE,
			fill = tk.BOTH
		)
		# for row in range(NUM_ROWS):
		# 	for col in range(NUM_COLS):
		# 		self._draw_box([row, col])

	"""
	a = tk.Tk()
	b = GameGrid(a)
	[[2,2,4,4], [4,2,2,None], [8,2,8,4], [4,16,2,None]]

	"""

	def _draw_box(self, position: tuple[int, int], colour) -> None:
		(x_min, y_min, x_max, y_max) = self._get_bbox(position)
		self.create_rectangle(
			x_min,y_min,x_max,y_max,
			fill=colour,
			width = 1
		)

	def _get_bbox(self, position: tuple[int, int]) -> tuple[int, int, int, int]:
		row = position[0]
		col = position[1]

		x_min = self.padding*(col+1) + self.box_side*(col)
		y_min = self.padding*(row+1) + self.box_side*(row)
		x_max = x_min + self.box_side
		y_max = y_min + self.box_side
		return (x_min, y_min, x_max, y_max)

	def _get_midpoint(self, position: tuple[int, int]) -> tuple[int, int]:
		(x_min, y_min, x_max, y_max) = self._get_bbox(position)
		return ((x_min + x_max)/2, (y_min + y_max)/2)

	def clear(self) -> None:
		self.delete('all')
		# for i in range(NUM_ROWS):
		# 	for j in range(NUM_COLS):
		# 		self._draw_box([i, j], COLOURS[None])

	def redraw(self, tiles: list[list[int]]) -> None:
		self.clear()
		for i in range(NUM_ROWS):
			for j in range(NUM_COLS):
				if tiles[i][j] == None:
					self._draw_box([i, j], COLOURS[None])
				else:
					self._draw_box([i, j], COLOURS[tiles[i][j]])
					(x, y) = self._get_midpoint([i, j])
					self.create_text(x, y, text=f"{tiles[i][j]}", \
						fill=FG_COLOURS[tiles[i][j]], font=TILE_FONT)


class StatusBar(tk.Frame):
	def __init__(self, master: tk.Tk, **kwargs):
		super().__init__(master, **kwargs)
		self.pack(
			fill=tk.BOTH,
			expand=tk.TRUE,
			side=tk.BOTTOM
		)
#################################### pack two labels
		label_frame=tk.Frame(
			self
		)
		label_frame.pack(
			expand=tk.TRUE,
			fill=tk.BOTH,
			side=tk.LEFT
		)
######################################## pack two labels into score frame
		self.score_frame=tk.Frame(
			label_frame,
			bg=BACKGROUND_COLOUR
		)
		self.score_frame.pack(
			expand=tk.TRUE,
			fill=tk.BOTH,
			side=tk.LEFT,
			padx=10,
			pady=10
		)
###############################################
		self.stext_label=tk.Label(
			self.score_frame,
			bg=BACKGROUND_COLOUR,
			text="SCORE",
			fg=COLOURS[None]
		)
		self.stext_label.pack(
			expand=tk.TRUE,
			fill=tk.BOTH,
			side=tk.TOP,
			pady=5
		)

		self.snum=tk.Label(
			self.score_frame,
			bg=BACKGROUND_COLOUR,
			text="0",
			fg=LIGHT
		)
		self.snum.pack(
			expand=tk.TRUE,
			fill=tk.BOTH,
			side=tk.BOTTOM,
			pady=5
		)
####################################### pack two labels into undo frame
		self.undo_frame=tk.Frame(
			label_frame,
			bg=BACKGROUND_COLOUR
		)
		self.undo_frame.pack(
			expand=tk.TRUE,
			fill=tk.BOTH,
			side=tk.LEFT,
			padx=10,
			pady=10
		)
#########################################
		self.utext=tk.Label(
			self.undo_frame,
			bg=BACKGROUND_COLOUR,
			text="UNDOS",
			fg=COLOURS[None]
		)
		self.utext.pack(
			expand=tk.TRUE,
			fill=tk.BOTH,
			side=tk.TOP,
			pady=5
		)

		self.unum=tk.Label(
			self.undo_frame,
			bg=BACKGROUND_COLOUR,
			text="3",
			fg=LIGHT
		)
		self.unum.pack(
			expand=tk.TRUE,
			fill=tk.BOTH,
			side=tk.BOTTOM,
			pady=5
		)
#######################################################  pack two buttons into a frame
		button_frame=tk.Frame(
			self
		)
		button_frame.pack(
			fill=tk.BOTH,
			expand=tk.TRUE,
			side=tk.RIGHT
		)

		self.new_game=tk.Button(
			button_frame,
			text="New Game",
			#command=self.set_callbacks
		)
		self.new_game.pack(
			side=tk.TOP,
			pady=5
		)

		self.undo_move=tk.Button(
			button_frame,
			text="Undo Move",
			#command=self.set_callbacks
		)
		self.undo_move.pack(
			side=tk.TOP,
			pady=5
		)

	def redraw_infos(self, score: int, undos: int) -> None:
		self.snum.config(text=f"{score}")
		self.unum.config(text=f"{undos}")


	def set_callbacks(self, new_game_command: callable, undo_command: callable) -> None:
		self.new_game.config(command=new_game_command)
		self.undo_move.config(command=undo_command)

class Game:
	def __init__(self, master: tk.Tk) -> None:
		self.model = Model()
		self.master = master
		self.master.title("CSSE1001/7030 2022 Semester 2 A3")
		self._moved = False
		# self.frame = tk.Frame(
		# 	self.master
		# )
		# self.frame.pack(
		# 	side=tk.BOTTOM
		# )

		menu = tk.Menu(self.master)
		self.master.config(menu=menu)
		#save_menu = tk.Menu(menu)

		file_menu = tk.Menu(menu)

		menu.add_cascade(
			label="File",
			menu=file_menu
		)


		file_menu.add_command(
			label="Save game",
			command=self.save_game
		)

		file_menu.add_command(
			label="Load game",
			command=self.import_game
		)

		file_menu.add_command(
			label="New game",
			command=self.start_new_game
		)

		file_menu.add_command(
			label='Quit', 
			command=self.quit_game
		)


		# save_menu.add_command(
		# 	label="Save game",
		# 	command=self.save_game
		# )

		self.statusbar = StatusBar(self.master)
		self.statusbar.set_callbacks(self.start_new_game, self.undo_previous_move)

		self.title = tk.Label(
            self.master,
            text="2048",
			font=TITLE_FONT,
			fg=LIGHT,
            bg="yellow"
        )
		self.title.pack(
			fill = tk.BOTH,
			expand=tk.TRUE,
            side=tk.TOP
        )

		self.grid = GameGrid(self.master)
		self.grid.pack(
            side = tk.TOP
        )

		self.master.bind("<Key>", self.attempt_move)

	def save_game(self):
		with filedialog.asksaveasfile(mode="w") as game_status:
			#game_status.write(f"{self.model.get_tiles()}")
			game_status.write(f"{self.model.get_tiles()}\n{self.model.previous_tiles}\n\
{self.model.get_score()}\n{self.model.get_undos_remaining()}")
				
	def import_game(self):
		i = 0
		with filedialog.askopenfile(mode="r") as board:
			for line in board:
				if i == 0:
					self.model.current_tiles = eval(line)
				if i == 1:
					self.model.previous_tiles = eval(line)
				if i == 2:
					self.model.points = int(line)
					self.model.previous_points = int(line)
				if i == 3:
					self.model._undo = int(line)
				i += 1
		# self.model.points = 0
		# self.model._undo = 3
		self.statusbar.redraw_infos(self.model.get_score(), self.model.get_undos_remaining())
		self.draw()

	# Maybe add timestamp here
	def quit_game(self):
		quit = messagebox.askyesno(
			title=None,
			message="Are you sure to quit?"
		)
		if quit:
			self.master.destroy()

	def start_game(self):								# maybe replace with func strart_new_game
		self.model.new_game()
		#self.master.bind("<Key>", self.attempt_move)

	def draw(self) -> None:
		tiles = self.model.get_tiles()
		self.grid.redraw(tiles)

	def attempt_move(self, event: tk.Event) -> None:
		key_press = event.keysym
		print('{} key pressed'.format(key_press))

		if self.model.attempt_move(key_press):
			self.model.previous_points = self.model.get_score()
			self.model.previous_tiles = self.model.get_tiles()
			self._moved = True
			if key_press == LEFT:
				self.model.move_left()
				#self.new_tile()
			elif key_press == UP:
				self.model.move_up()
				#self.new_tile()
			elif key_press == DOWN:
				self.model.move_down()
				#self.new_tile()
			elif key_press == RIGHT:
				self.model.move_right()
				#self.new_tile()
			#self.new_tile()
			self.statusbar.redraw_infos(self.model.get_score(), self.model.get_undos_remaining())
			# self.statusbar.set_callbacks(self.start_new_game, self.undo_previous_move)


			self.draw()
			# if any move then redraw, determine if a move has been made

		if self.model.has_won():
			messagebox.showinfo(
				message=WIN_MESSAGE
			)
		else:
			if self._moved:
				self.master.after(NEW_TILE_DELAY, self.new_tile)
		print('Score: {}'.format(self.model.get_score()))

		self._moved = False

		
	def new_tile(self) -> None:
		self.model.add_tile()
		self.draw()
		if self.model.has_lost():
			messagebox.showinfo(
				message=LOSS_MESSAGE
			)

	def undo_previous_move(self) -> None:
		self.model.use_undo() #############################################
		self.statusbar.redraw_infos(self.model.get_score(), self.model.get_undos_remaining())
		self.draw()


	def start_new_game(self) -> None:
		self.model.points = 0
		self.model._undo = MAX_UNDOS
		self.statusbar.redraw_infos(self.model.get_score(), self.model.get_undos_remaining())
		self.model.new_game()
		self.draw()
		

def play_game(root):
	# Add a docstring and type hints to this function
	# Then write your code here
	start_game = Game(root)
	start_game.start_game()
	start_game.draw()


    # def start(self):
    #     self.add_start_cells()
    #     self.panel.paint()
    #     self.panel.root.bind('<Key>', self.key_handler)
    #     self.panel.root.mainloop()

if __name__ == '__main__':
	root = tk.Tk()
	play_game(root)
	root.mainloop()

