class State:
    def __init__(self, manager):
        self.manager = manager

    def on_enter(self):
        pass

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self, surface):
        pass
    
    def reset(self):        
        pass

    def get_target_fps(self):
        return 60
