# from pico2d import load_image
#
# from state_machine import StateMachine
#
# class Idle:
#     def __init__(self, short):
#         self.short = short
#         pass
#
#     def enter(self):
#         pass
#
#     def exit(self):
#         pass
#
#     def do(self):
#         self.short.current_frame = 2
#
#         pass
#
#     def draw(self):
#         sprite_w, sprite_h = self.short.current_sprite_size
#         self.short.current_image.clip_draw(
#             self.short.current_frame * sprite_w, 0, sprite_w, sprite_h,
#             self.short.x, self.short.y, 250, 300
#         )
#         pass
#
# class short_sword:
#     def __init__(self):
#         self.idle_image = load_image('short_sword.png')
#         self.x, self.y = 700, 300
#         self.idle_sprite_size = (354, 495)
#         self.frame_idle = 3
#         self.current_image = self.idle_image
#         self.current_sprite_size = self.idle_sprite_size
#         self.frame = self.frame_idle
#         self.current_frame = 0
#
#         self.IDLE = Idle(self)
#         self.state_machine = StateMachine(self.IDLE,{})  # 상태머신 생성 및 초기 시작 상태 설정
#
#     def update(self):
#         self.state_machine.update()
#
#     def draw(self):
#         self.state_machine.draw()
