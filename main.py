
from kivy.config import Config
Config.set("graphics", "orientation", "landscape")

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import (
    Color, Rectangle, Ellipse, Line, RoundedRectangle
)
from math import hypot
import random

Window.clearcolor = (0.025, 0.03, 0.05, 1)


class Game(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.state = "menu"
        self.hp = 100
        self.score = 0

        self.player = [0, 0]
        self.enemies = []
        self.bullets = []

        self.mx = 0
        self.my = 0

        self.joy_id = None
        self.fire_id = None
        self.joy_start = (0, 0)

        self.spawn = 0
        self.fire = 0

        self.bind(size=self.draw, pos=self.draw)
        Clock.schedule_interval(self.update, 1 / 30)

    def start(self):
        self.state = "game"
        self.hp = 100
        self.score = 0

        self.enemies.clear()
        self.bullets.clear()

        self.spawn = 0
        self.fire = 0

        self.mx = 0
        self.my = 0

        self.joy_id = None
        self.fire_id = None

        self.player = [
            self.width / 2,
            self.height / 2
        ]

        self.draw()

    def game_over(self):
        self.state = "over"

        if self.parent:
            self.parent.show_screen("over")

    def spawn_enemy(self):
        if len(self.enemies) >= 6:
            return

        side = random.randrange(4)

        if side == 0:
            x, y = random.uniform(0, self.width), self.height + 20
        elif side == 1:
            x, y = random.uniform(0, self.width), -20
        elif side == 2:
            x, y = -20, random.uniform(0, self.height)
        else:
            x, y = self.width + 20, random.uniform(0, self.height)

        self.enemies.append({
            "x": x,
            "y": y,
            "hp": 2,
            "speed": random.uniform(50, 75)
        })

    def shoot(self):
        if not self.enemies or len(self.bullets) >= 15:
            return

        px, py = self.player

        target = min(
            self.enemies,
            key=lambda e: hypot(e["x"] - px, e["y"] - py)
        )

        dx = target["x"] - px
        dy = target["y"] - py
        dist = max(1, hypot(dx, dy))

        self.bullets.append({
            "x": px,
            "y": py,
            "vx": dx / dist * 450,
            "vy": dy / dist * 450,
            "life": 1
        })

    def on_touch_down(self, touch):
        if self.state != "game":
            return False

        x, y = touch.pos

        if x < self.width * 0.55 and self.joy_id is None:
            self.joy_id = touch.uid
            self.joy_start = (x, y)
            touch.grab(self)
            self.joystick(x, y)
            return True

        if x >= self.width * 0.55 and self.fire_id is None:
            self.fire_id = touch.uid
            touch.grab(self)
            self.shoot()
            return True

        return True

    def joystick(self, x, y):
        ox, oy = self.joy_start
        dx, dy = x - ox, y - oy

        dist = max(1, hypot(dx, dy))

        self.mx = dx / dist * min(1, dist / 60)
        self.my = dy / dist * min(1, dist / 60)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            if touch.uid == self.joy_id:
                self.joystick(*touch.pos)
            return True

        return False

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)

            if touch.uid == self.joy_id:
                self.joy_id = None
                self.mx = 0
                self.my = 0

            if touch.uid == self.fire_id:
                self.fire_id = None

            return True

        return False

    def update(self, dt):
        if self.state != "game":
            return

        dt = min(dt, 0.04)

        self.player[0] += self.mx * 220 * dt
        self.player[1] += self.my * 220 * dt

        self.player[0] = max(
            20, min(max(20, self.width - 20), self.player[0])
        )

        self.player[1] = max(
            20, min(max(20, self.height - 20), self.player[1])
        )

        self.spawn += dt
        self.fire += dt

        if self.spawn >= 1.5:
            self.spawn_enemy()
            self.spawn = 0

        if self.fire_id is not None and self.fire >= 0.25:
            self.shoot()
            self.fire = 0

        px, py = self.player

        for e in self.enemies[:]:
            dx = px - e["x"]
            dy = py - e["y"]
            dist = max(1, hypot(dx, dy))

            e["x"] += dx / dist * e["speed"] * dt
            e["y"] += dy / dist * e["speed"] * dt

            if dist < 35:
                self.hp -= 20 * dt

        for b in self.bullets[:]:
            b["x"] += b["vx"] * dt
            b["y"] += b["vy"] * dt
            b["life"] -= dt

            if b["life"] <= 0:
                self.bullets.remove(b)
                continue

            for e in self.enemies[:]:
                if hypot(
                    b["x"] - e["x"],
                    b["y"] - e["y"]
                ) < 24:

                    e["hp"] -= 1

                    if b in self.bullets:
                        self.bullets.remove(b)

                    if e["hp"] <= 0:
                        if e in self.enemies:
                            self.enemies.remove(e)

                        self.score += 10

                    break

        if self.hp <= 0:
            self.hp = 0
            self.game_over()
            return

        self.draw()

    def draw(self, *args):
        self.canvas.clear()

        with self.canvas:

            Color(0.07, 0.08, 0.10, 1)
            Rectangle(pos=self.pos, size=self.size)

            Color(0.12, 0.13, 0.15, 1)

            for i in range(1, 9):
                y = self.height * i / 9
                Line(
                    points=[0, y, self.width, y],
                    width=0.6
                )

            Color(0.19, 0.20, 0.22, 1)
            Rectangle(
                pos=(0, self.height * 0.89),
                size=(self.width, self.height * 0.11)
            )

            Color(0.7, 0.025, 0.04, 1)
            Rectangle(
                pos=(0, self.height * 0.88),
                size=(self.width, 3)
            )

            if self.state != "game":
                return

            # ENEMIES
            for e in self.enemies:
                x, y = e["x"], e["y"]

                Color(0, 0, 0, 0.35)
                Ellipse(
                    pos=(x - 20, y - 12),
                    size=(40, 18)
                )

                Color(0.28, 0.09, 0.09, 1)
                RoundedRectangle(
                    pos=(x - 15, y - 4),
                    size=(30, 35),
                    radius=[5]
                )

                Color(0.12, 0.10, 0.10, 1)
                Ellipse(
                    pos=(x - 9, y + 20),
                    size=(18, 18)
                )

                Color(0.95, 0.05, 0.08, 1)
                Rectangle(
                    pos=(x - 15, y + 43),
                    size=(30, 3)
                )

            # BULLETS
            for b in self.bullets:
                Color(1, 0.75, 0.2, 1)
                Ellipse(
                    pos=(b["x"] - 4, b["y"] - 4),
                    size=(8, 8)
                )

            # PLAYER
            x, y = self.player

            Color(0, 0, 0, 0.4)
            Ellipse(
                pos=(x - 21, y - 13),
                size=(42, 18)
            )

            Color(0.13, 0.24, 0.19, 1)
            RoundedRectangle(
                pos=(x - 15, y - 5),
                size=(30, 36),
                radius=[6]
            )

            Color(0.1, 0.13, 0.12, 1)
            RoundedRectangle(
                pos=(x - 12, y + 1),
                size=(24, 22),
                radius=[4]
            )

            Color(0.7, 0.48, 0.34, 1)
            Ellipse(
                pos=(x - 9, y + 22),
                size=(18, 18)
            )

            Color(0.12, 0.19, 0.15, 1)
            Ellipse(
                pos=(x - 11, y + 29),
                size=(22, 12)
            )

            # WEAPON
            Color(0.035, 0.04, 0.045, 1)
            RoundedRectangle(
                pos=(x + 8, y + 9),
                size=(29, 6),
                radius=[2]
            )

            # JOYSTICK
            if self.joy_id is not None:
                ox, oy = self.joy_start

                Color(0.15, 0.45, 0.95, 0.2)
                Ellipse(
                    pos=(ox - 65, oy - 65),
                    size=(130, 130)
                )

                Color(0.3, 0.65, 1, 0.8)
                Line(
                    circle=(ox, oy, 65),
                    width=2
                )

                Color(0.2, 0.5, 1, 0.8)
                Ellipse(
                    pos=(
                        ox + self.mx * 35 - 22,
                        oy + self.my * 35 - 22
                    ),
                    size=(44, 44)
                )

            # FIRE BUTTON
            Color(0.85, 0.02, 0.06, 0.25)
            Ellipse(
                pos=(self.width - 135, 40),
                size=(90, 90)
            )

            Color(1, 0.1, 0.15, 1)
            Line(
                circle=(self.width - 90, 85, 42),
                width=2
            )


class MainScreen(FloatLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.game = Game()
        self.add_widget(self.game)

        self.title = Label(
            text="[b]RED ARENA[/b]",
            markup=True,
            font_size="48sp",
            color=(1, 0.06, 0.1, 1),
            size_hint=(1, 0.2),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.78
            }
        )
        self.add_widget(self.title)

        self.subtitle = Label(
            text="REALISTIC EDITION 2.5D",
            font_size="17sp",
            color=(0.7, 0.7, 0.8, 1),
            size_hint=(1, 0.1),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.65
            }
        )
        self.add_widget(self.subtitle)

        self.play = Button(
            text="▶ PLAY",
            font_size="25sp",
            bold=True,
            background_normal="",
            background_color=(0.75, 0.02, 0.07, 1),
            size_hint=(0.4, 0.17),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.44
            }
        )

        self.play.bind(
            on_release=lambda x: self.show_screen("game")
        )
        self.add_widget(self.play)

        self.info = Label(
            text="SURVIVE THE ARENA",
            font_size="15sp",
            color=(0.7, 0.7, 0.8, 1),
            size_hint=(1, 0.1),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.22
            }
        )
        self.add_widget(self.info)

        self.hud = Label(
            text="",
            font_size="18sp",
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(150, 40),
            pos_hint={"x": 0.02, "top": 0.98}
        )
        self.add_widget(self.hud)

        self.hp_label = Label(
            text="",
            font_size="18sp",
            bold=True,
            color=(1, 0.2, 0.2, 1),
            size_hint=(None, None),
            size=(130, 40),
            pos_hint={"right": 0.98, "top": 0.98}
        )
        self.add_widget(self.hp_label)

        self.over = Label(
            text="[b]GAME OVER[/b]\n",
            markup=True,
            font_size="40sp",
            color=(1, 0.05, 0.1, 1),
            size_hint=(1, 0.2),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.65
            }
        )
        self.add_widget(self.over)

        self.restart = Button(
            text="RESTART",
            font_size="23sp",
            background_normal="",
            background_color=(0.75, 0.02, 0.07, 1),
            size_hint=(0.4, 0.15),
            pos_hint={
                "center_x": 0.5,
                "center_y": 0.38
            }
        )

        self.restart.bind(
            on_release=lambda x: self.show_screen("game")
        )
        self.add_widget(self.restart)

        self.show_screen("menu")

        Clock.schedule_interval(self.refresh, 1 / 15)

    def show_screen(self, screen):

        if screen == "game":
            self.game.start()
        else:
            self.game.state = screen

        self.game.disabled = False
        self.game.opacity = 1

        menu = screen == "menu"
        over = screen == "over"
        playing = screen == "game"

        self.title.opacity = 1 if menu else 0
        self.subtitle.opacity = 1 if menu else 0
        self.play.opacity = 1 if menu else 0
        self.info.opacity = 1 if menu else 0

        self.over.opacity = 1 if over else 0
        self.restart.opacity = 1 if over else 0

        self.hud.opacity = 1 if playing else 0
        self.hp_label.opacity = 1 if playing else 0

        self.play.disabled = not menu
        self.restart.disabled = not over

    def refresh(self, dt):
        if self.game.state == "game":
            self.hud.text = "SCORE: " + str(self.game.score)
            self.hp_label.text = "HP: " + str(int(self.game.hp))

        if self.game.state == "over":
            self.over.text = (
                "[b]GAME OVER[/b]\n"
                "SCORE: " + str(self.game.score)
            )


class RedArenaApp(App):

    def build(self):
        self.title = "RED ARENA"
        return MainScreen()


if __name__ == "__main__":
    RedArenaApp().run()
