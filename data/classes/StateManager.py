class StateManager:
    def __init__(self):
        self.states = {}
        self.current_state = None

    def setup(self, states, initial_state):
        self.states = states
        self.change_state(initial_state)

    def change_state(self, state_name):
        if state_name in self.states:
            self.current_state = self.states[state_name]
            self.current_state.on_enter()

    def handle_events(self, events):
        if self.current_state:
            self.current_state.handle_events(events)

    def update(self):
        if self.current_state:
            self.current_state.update()

    def draw(self, surface):
        if self.current_state:
            self.current_state.draw(surface)

    def get_target_fps(self):
        if self.current_state and hasattr(self.current_state, 'get_target_fps'):
            return self.current_state.get_target_fps()
        return 60

