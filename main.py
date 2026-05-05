import pygame
import sys

from data.classes.StateManager import StateManager
from data.states.MenuState import MenuState
from data.states.PvPState import PvPState
from data.states.PvEState import PvEState

pygame.init()

WINDOW_SIZE = (600, 600)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Chess AI")

manager = StateManager()
states = {
    'menu': MenuState(manager),
    'pvp': PvPState(manager),
    'pve': PvEState(manager)
}
manager.setup(states, 'menu')

clock = pygame.time.Clock()
running = True

while running:
	events = pygame.event.get()
	for event in events:
		if event.type == pygame.QUIT:
			running = False
			
	manager.handle_events(events)
	manager.update()
	
	manager.draw(screen)
	pygame.display.update()
	
	clock.tick(manager.get_target_fps())

pygame.quit()
sys.exit()