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
                # current_state가 속한 오브젝트(예: shadowMan, peasant)를 찾아 식별자 표시
                owner = None
                # 상태 객체 내부에 owner 참조의 일반적인 이름들을 검사
                for attr in ('monk', 'peasant', 'owner'):
                    if hasattr(self.current_state, attr):
                        owner = getattr(self.current_state, attr)
                        break
                owner_name = ''
                if owner is not None:
                    owner_name = getattr(owner, 'player_id', owner.__class__.__name__) + ': '

                print(f'{owner_name}{self.current_state.__class__.__name__} - {event_to_string(state_event)} -> {self.next_state.__class__.__name__}')
                self.current_state = self.next_state
                return

        # INPUT 이벤트는 자주 발생하며 정상적으로 무시되는 경우가 많으므로
        # 디버그 모드가 아닐 경우에는 출력하지 않도록 합니다.
        # 필요하면 디버그 플래그를 추가하여 출력하도록 변경할 수 있습니다.
        if state_event[0] != 'INPUT':
            print(f'처리되지 않은 이벤트{event_to_string(state_event)}가 있습니다.')
        pass