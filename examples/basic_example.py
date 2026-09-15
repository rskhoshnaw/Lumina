from manim import *
from lumina import LuminaScene
from lumina.themes import KURDISH_FONT

class SimpleDemo(LuminaScene):
    def construct(self):
        # عنوان انگلیسی
        title = Text("Lumina Animation Engine", font_size=44)
        title.to_edge(UP)

        # متن کوردی با فونت Rudaw
        kurdish = Text(
            "سڵاو، ئەمە لومینایە بۆ فێرکاری و بیرکاری",
            font_size=36,
            font=KURDISH_FONT
        )
        kurdish.next_to(title, DOWN, buff=0.8)

        # فرمول ریاضی با LaTeX
        formula = MathTex(r"e^{i\pi} + 1 = 0", font_size=54)
        formula.next_to(kurdish, DOWN, buff=1.0)

        # اجرای انیمیشن‌ها
        self.play(Write(title), run_time=1)
        self.play(FadeIn(kurdish, shift=UP), run_time=1)
        self.play(Write(formula), run_time=1.5)
        self.wait(1)

        # ترنزیشن و تغییر رنگ سینمایی
        self.play(
            title.animate.set_color("#4ECDC4"),
            kurdish.animate.set_color("#FF6B6B"),
            formula.animate.set_color("#FFE66D"),
            run_time=1.2
        )
        self.wait(2)