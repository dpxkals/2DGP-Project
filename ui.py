from pico2d import *


class UI:
    def __init__(self):
        # 폰트 로드
        self.font = load_font('ENCR10B.TTF', 26)
        self.big_font = load_font('ENCR10B.TTF', 100)
        self.mid_font = load_font('ENCR10B.TTF', 60)

        self.bar_red = load_image('hp_bar_1.png')


    def draw(self, p1, p2, p1_score, p2_score, round_num, phase, phase_time, fight_time):
        self.draw_hud(p1, p2, p1_score, p2_score, fight_time)
        self.draw_message(phase, phase_time, p1, p2, p1_score, p2_score)

    def draw_hud(self, p1, p2, p1_score, p2_score, fight_time):
        # --- [타이머] ---
        color = (255, 0, 0) if fight_time <= 10 else (255, 255, 255)
        self.mid_font.draw(925, 1020, f"{int(fight_time):02d}", color)

        # --- [체력바 설정] ---
        bar_width = 700  # 체력바 전체 길이
        bar_height = 25  # 체력바 높이
        y_pos = 1030  # Y 위치

        # 1. 겉 테두리 (항상 고정된 크기)
        draw_rectangle(50, y_pos, 50 + bar_width, y_pos + bar_height)

        # 2. 속 채우기 (빨간색 이미지 사용)
        if self.bar_red:
            p1_ratio = max(0, p1.hp / p1.max_hp)  # 현재 체력 비율 (0.0 ~ 1.0)
            current_width = int(bar_width * p1_ratio)  # 현재 체력바 길이

            if current_width > 0:
                self.bar_red.draw(50 + current_width // 2, y_pos + bar_height // 2, current_width, bar_height)

        # 1. 겉 테두리
        draw_rectangle(1170, y_pos, 1170 + bar_width, y_pos + bar_height)

        # 2. 속 채우기 (파란색 이미지 사용)
        if self.bar_red:
            p2_ratio = max(0, p2.hp / p2.max_hp)
            current_width = int(bar_width * p2_ratio)

            if current_width > 0:
                self.bar_red.draw(1870 - current_width // 2, y_pos + bar_height // 2, current_width, bar_height)

        # --- [텍스트 정보] ---
        self.font.draw(50, y_pos - 30, f"1P  HP {int(p1.hp)}", (255, 100, 100))
        self.font.draw(1700, y_pos - 30, f"2P  HP {int(p2.hp)}", (100, 100, 255))
        self.font.draw(50, y_pos - 60, f"WIN: {p1_score}", (255, 215, 0))
        self.font.draw(1750, y_pos - 60, f"WIN: {p2_score}", (255, 215, 0))

    def draw_message(self, phase, phase_time, p1, p2, p1_score, p2_score):
        # 기존 코드 유지
        current_time = get_time()
        elapsed = current_time - phase_time
        center_x = 960
        center_y = 540

        if phase == 'ROUND_START':
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
            if p1.hp > p2.hp:
                self.font.draw(center_x - 120, center_y, "1P WINS THE ROUND", (255, 255, 255))
            elif p2.hp > p1.hp:
                self.font.draw(center_x - 120, center_y, "2P WINS THE ROUND", (255, 255, 255))
            else:
                # 체력이 같으면 무승부
                self.mid_font.draw(center_x - 80, center_y, "DRAW", (200, 200, 200))

        elif phase == 'GAME_OVER':
            self.big_font.draw(center_x - 250, center_y + 150, "GAME SET", (255, 255, 255))
            if p1_score > p2_score:
                winner = "1P"
            elif p1_score < p2_score:
                winner = "2P"
            else :
                winner = "DRAW"
            if winner == "1P" :
                color = (255, 50, 50)
            elif winner == "2P" :
                color = (50, 50, 255)
            else :
                color = (50, 255, 50)
            self.mid_font.draw(center_x - 300, center_y, f"FINAL WINNER: {winner}", color)

            remaining_time = 4.0 - elapsed
            sec = int(max(0, remaining_time))
            self.font.draw(center_x - 150, center_y - 100, f" {sec} seconds to Return", (200, 200, 200))