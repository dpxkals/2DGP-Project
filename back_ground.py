from pico2d import load_image


class background:
    def __init__(self):
        self.image = load_image('backGround.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(960,540,1920,1080)
