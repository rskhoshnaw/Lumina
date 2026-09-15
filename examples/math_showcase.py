from manim import *
from lumina import LuminaScene
from lumina.themes import KURDISH_FONT


class MathTransformationDemo(LuminaScene):
    def construct(self):
        # ساخت سیستم مختصات
        axes = (
            Axes(
                x_range=[-3, 3, 1],
                y_range=[-1, 9, 2],
                axis_config={"color": BLUE_C},
            )
            .scale(0.7)
            .to_edge(DOWN)
        )

        # رسم نمودار تابع توان دو
        graph = axes.plot(lambda x: x**2, color=YELLOW)
        func_label = MathTex(r"f(x) = x^2").next_to(axes, UP)

        # اشکال هندسی اولیه و تغییر شکل (Morphing)
        circle = Circle(radius=1.5, color=TEAL).shift(UP * 1.5)
        square = Square(side_length=2.5, color=RED).shift(UP * 1.5)

        # ۱. انیمیشن ترسیم و سپس مورف دایره به مربع
        self.play(Create(circle))
        self.wait(0.5)
        self.play(Transform(circle, square), run_time=1.5)
        self.wait(0.5)
        self.play(FadeOut(circle))

        # ۲. ورود نمودار و تابع تحلیلی
        self.play(Create(axes), run_time=1.5)
        self.play(Create(graph), Write(func_label), run_time=2)
        self.wait(2)
