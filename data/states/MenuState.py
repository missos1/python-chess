from data.states.State import State
from data.classes.Button import Button

class MenuState(State):
    def __init__(self, manager):
        super().__init__(manager)
        # Centered horizontally for a 600x600 window
        self.btn_pvp = Button(200, 200, 200, 60, "PvP")
        self.btn_pve = Button(200, 300, 200, 60, "PvE")
        self.btn_eve = Button(200, 400, 200, 60, "EvE")

    def handle_events(self, events):
        for event in events:
            if self.btn_pvp.is_clicked(event):
                self.manager.change_state('pvp')
            elif self.btn_pve.is_clicked(event):
                self.manager.change_state('pve')
            elif self.btn_eve.is_clicked(event):
                self.manager.change_state('eve')

    def draw(self, surface):
        surface.fill((230, 230, 230)) # Light gray background
        self.btn_pvp.draw(surface)
        self.btn_pve.draw(surface)
        self.btn_eve.draw(surface)
