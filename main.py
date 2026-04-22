import pygame
from data.classes.chess_bot.constants import *
from data.classes.chess_bot.move_gens import get_knights_moves

from data.classes.Board import Board

pygame.init()

WINDOW_SIZE = (600, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)

board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])

# debug function to visualize bitboards in the console
def print_bitboards(bitboard):
		print("\n  A B C D E F G H")
		print("  ---------------")
		
		for rank in range(7, -1, -1):
			row_string = f"{rank + 1}|"
   
			for file in range(8):
				square_index = (rank * 8) + file
				
				# check if the bit at this index is 1
				# do this by creating a temporary board with a 1 at the target square,
				# using Bitwise AND to see if they overlap.
				if bitboard & (1 << square_index):
					row_string += "1 "  # Piece exists
				else:
					row_string += ". "  # Empty square
					
			print(row_string)
			
		print("  ---------------\n")

def draw(display):
	display.fill('white')

	board.draw(display)

	pygame.display.update()

running = True
while running:
	mx, my = pygame.mouse.get_pos()
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		elif event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				board.handle_click(mx, my)
		
		# debug
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_d:
				bitboards = board.get_bitboards()
				knight_test_moves = bitboards[W_KNIGHT]
				for move in get_knights_moves(bitboards, WHITE):
					knight_test_moves |= (1 << move[1])
				print_bitboards(knight_test_moves)
	
	if board.is_in_checkmate('black'):
		print('White wins!')
		running = False
	elif board.is_in_checkmate('white'):
		print('Black wins!')
		running = False

	draw(screen)