from pico2d import *


class UI:
    def __init__(self):
        # 폰트 로드 (경로 에러나면 파일명만 적으세요)
        self.font = load_font('ENCR10B.TTF', 26)  # 일반 정보용
        self.big_font = load_font('ENCR10B.TTF', 100)  # 카운트다운/승리용
        self.mid_font = load_font('ENCR10B.TTF', 60)  # 타이머/KO용

    def draw(self, p1, p2, p1_score, p2_score, round_num, phase, phase_time, fight_time):
        # 1. 상단 정보창 (체력바, 타이머, 스코어)
        self.draw_hud(p1, p2, p1_score, p2_score, fight_time)

        # 2. 중앙 상태 메시지 (3-2-1, KO, WIN)
        self.draw_message(phase, phase_time, p1, p2, p1_score, p2_score)

    def draw_hud(self, p1, p2, p1_score, p2_score, fight_time):
        # --- [타이머] 중앙 상단 ---
        color = (255, 0, 0) if fight_time <= 10 else (255, 255, 255)
        self.mid_font.draw(925, 1020, f"{int(fight_time):02d}", color)  # 02d: 두자리수 유지

        # --- [체력바] ---
        bar_width = 700  # 바 길이 늘림
        bar_height = 25
        y_pos = 1030  # 화면 맨 위쪽

        # [1P HP Bar]
        # 1. 배경 (검은색/회색)
        draw_rectangle(50, y_pos, 50 + bar_width, y_pos + bar_height)
        # 2. 체력 (노란색 -> 빨간색)
        p1_ratio = max(0, p1.hp / p1.max_hp)

        draw_rectangle(50, y_pos, 50 + int(bar_width * p1_ratio), y_pos + bar_height)

        # [2P HP Bar]
        draw_rectangle(1170, y_pos, 1170 + bar_width, y_pos + bar_height)
        # 오른쪽에서 왼쪽으로 줄어들게
        p2_ratio = max(0, p2.hp / p2.max_hp)
        draw_rectangle(1170 + int(bar_width * (1 - p2_ratio)), y_pos, 1170 + bar_width, y_pos + bar_height)

        # --- [텍스트 정보] ---
        # 이름 및 HP 숫자 표시
        self.font.draw(50, y_pos - 30, f"1P  HP {int(p1.hp)}", (255, 100, 100))
        self.font.draw(1700, y_pos - 30, f"2P  HP {int(p2.hp)}", (100, 100, 255))

        # 1P 스코어 (왼쪽 정렬)
        self.font.draw(50, y_pos - 60, f"WIN: {p1_score}", (255, 215, 0))  # 금색

        # 2P 스코어 (오른쪽 정렬)
        self.font.draw(1750, y_pos - 60, f"WIN: {p2_score}", (255, 215, 0))

    def draw_message(self, phase, phase_time, p1, p2, p1_score, p2_score):
        current_time = get_time()
        elapsed = current_time - phase_time

        center_x = 960
        center_y = 540

        if phase == 'ROUND_START':
            # 카운트다운 (화면 중앙)
            if elapsed < 1.0:
                self.big_font.draw(center_x - 30, center_y, "3", (255, 0, 0))
            elif elapsed < 2.0:
                self.big_font.draw(center_x - 30, center_y, "2", (255, 100, 0))
            elif elapsed < 3.0:
                self.big_font.draw(center_x - 30, center_y, "1", (255, 255, 0))
            else:
                self.big_font.draw(center_x - 150, center_y, "FIGHT!", (255, 50, 50))

        elif phase == 'ROUND_OVER':
            self.mid_font.draw(center_x - 70, center_y + 100, "K.O.", (255, 0, 0))
            if p1.hp > 0:
                self.font.draw(center_x - 120, center_y, "1P WINS THE ROUND", (255, 255, 255))
            else:
                self.font.draw(center_x - 120, center_y, "2P WINS THE ROUND", (255, 255, 255))

        elif phase == 'GAME_OVER':
            self.big_font.draw(center_x - 250, center_y + 150, "GAME SET", (255, 255, 255))

            winner = "1P" if p1_score > p2_score else "2P"
            color = (255, 50, 50) if winner == "1P" else (50, 50, 255)

            self.mid_font.draw(center_x - 260, center_y, f"FINAL WINNER: {winner}", color)

            remaining_time = 4.0 - elapsed
            sec = int(max(0, remaining_time))
            self.font.draw(center_x - 150, center_y - 100, f" { sec } seconds to Return", (200, 200, 200))