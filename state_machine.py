from event_to_string import event_to_string

class StateMachine:
    def __init__(self, start_state, rules):
        self.current_state = start_state
        self.rules = rules
        self.current_state.enter(('START', 0))  # 시작 상태에 진입
        pass

    def update(self):
        self.current_state.do()
        pass

    def draw(self):
        self.current_state.draw()
        pass

    def handle_state_event(self, state_event):
        for check_event in self.rules[self.current_state].keys():
            if check_event(state_event): # 만약 True라면?
                self.next_state = self.rules[self.current_state][check_event]
                self.current_state.exit(state_event)
                self.next_state.enter(state_event)
                print(f'{self.current_state.__class__.__name__} - {event_to_string(state_event)} -> {self.next_state.__class__.__name__}')
                self.current_state = self.next_state
                return

        print(f'처리되지 않은 이벤트{event_to_string(state_event)}가 있습니다.')
        pass