from pico2d import draw_rectangle, load_font


class UI:
    def __init__(self):
        self.font = load_font('ENCR10B.TTF', 20)

    def draw(self, p1, p2):
        # Player 1 HP Bar (Left Top)
        self.draw_hp_bar(p1, 50, 1000, (255, 0, 0))
        # Player 2 HP Bar (Right Top)
        self.draw_hp_bar(p2, 1470, 1000, (0, 0, 255))

    def draw_hp_bar(self, player, x, y, color):
        # 배경 (회색)
        draw_rectangle(x, y, x + 400, y + 30)

        # 현재 체력 비율
        ratio = player.hp / player.max_hp
        # 체력 바 (색상) - pico2d에는 fill_rectangle이 없으므로 굵은 선을 여러 개 긋거나
        # 이미지가 없다면 draw_rectangle로 테두리만 그리고 내부는 텍스트로 대체
        # 여기서는 간단하게 텍스트와 길이조절된 박스로 표현
        draw_rectangle(x, y, x + int(400 * ratio), y + 30)
        self.font.draw(x + 10, y + 10, f'HP: {int(player.hp)}/{player.max_hp}', color)