class StateMachine:
    def __init__(self, start_state):
        self.current_state = start_state
        self.current_state.enter()
        pass

    def update(self):
        self.current_state.do()
        pass

    def draw(self):
        self.current_state.draw()
        pass